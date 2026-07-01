# Architecture Decision Log

This document records the *why* behind structural decisions, not just the *what*.
Updated incrementally as the project grows, commit by commit.

---

## 1. Overall style: Modular Monolith + Clean Architecture

**Decision:** single deployable FastAPI app, internally layered using Clean
Architecture (a.k.a. Hexagonal / Ports & Adapters), instead of microservices
or a flat `routers/services/models` structure.

**Alternatives considered:**

| Option | Why rejected / accepted |
|---|---|
| Microservices | Overkill for a single-team project; adds network/orchestration complexity with no real benefit here, and most interviewers read it as over-engineering for a portfolio project at this level. |
| Flat structure (`routers/`, `services/`, `models/`) | Fastest to write, but mixes business rules with framework/DB code, harder to unit test, doesn't demonstrate SOLID/DI skills. |
| Modular monolith + Clean Architecture | Chosen. Single process to run/deploy (simple), but internally enforces separation of concerns, testability, and dependency inversion — the actual skills this project exists to demonstrate. |

**Layers and dependency direction** (outer layers depend on inner ones, never the reverse):

```
api (FastAPI routers, DTOs)
   → application (use-case services, orchestration)
       → domain (pure business rules: compatibility engine, recommendation engine)
   → infrastructure (SQLAlchemy models/repos, Redis, Celery) — implements interfaces
       defined in application/interfaces, injected at runtime
```

- **`domain/`** has zero framework dependencies (no FastAPI, no SQLAlchemy imports).
  It contains the compatibility rules and recommendation logic — the actual
  "product" of this app. This is what lets us unit-test things like *"an RTX 4090
  doesn't fit in a Mini-ITX case"* in milliseconds, with no database involved.
- **`application/`** orchestrates use cases (e.g. `RegisterUserUseCase`,
  `BuildPCUseCase`). It depends on **interfaces** (`application/interfaces/`,
  abstract repository contracts), not concrete implementations — classic
  Dependency Inversion. This is what enables swapping Postgres for an in-memory
  fake in tests without touching business logic.
- **`infrastructure/`** holds the concrete, swappable details: SQLAlchemy ORM
  models, repository implementations, Redis client, Celery tasks.
- **`api/`** stays intentionally thin: parse request → call an application
  service → map result to a response schema. No business logic lives here.

**Why this matters for the Smart PC Builder specifically:** the compatibility
and recommendation engines are pure rule-based logic, not data-access code.
Isolating them in `domain/` keeps them independently testable and easy to
extend (e.g. adding a new workload-scoring rule later doesn't touch the API
or DB layer at all).

---

## 2. Package management: `uv`

**Decision:** use `uv` instead of `poetry` or plain `pip`.

**Why:** `uv` is significantly faster (Rust-based resolver/installer), uses a
standard `pyproject.toml` (no proprietary lock format to explain in an
interview), and is rapidly becoming the modern default in the Python
ecosystem — signals that the stack is current, not copy-pasted from an old
tutorial.

---

## 3. Pydantic v2 schemas separate from SQLAlchemy ORM models

**Decision:** `app/schemas/` (Pydantic DTOs, request/response validation) is
kept fully separate from `app/infrastructure/database/models/` (SQLAlchemy
ORM entities).

**Why:** conflating them is a common beginner mistake — it couples your API
contract to your DB schema, leaks ORM internals (lazy-loaded relationships,
DB-only fields) into responses, and makes versioning the API painful. Keeping
them separate is standard production practice and a mapping step (ORM model
→ DTO) is cheap.

---

## 4. SQLAlchemy 2.0 (typed, async) + Alembic from day one

**Decision:** use the SQLAlchemy 2.0 `Mapped[]`/`mapped_column()` typed style
(not the legacy 1.x `Column()` style), async engine (`asyncpg` driver), and
Alembic migrations starting from the very first schema, never hand-edited.

**Why:** demonstrates familiarity with the current SQLAlchemy API (a common
interview discussion point), and async DB access matches FastAPI's async-first
design — avoids blocking the event loop under load.

---

## 5. Redis & Celery — concrete use cases (not just "for show")

To avoid bolting these on superficially, here's what each is actually used
for as the project grows (will be refined as those features are implemented):

- **Redis:** refresh-token rotation/blacklist (logout invalidation), caching
  expensive recommendation/catalog queries.
- **Celery (broker: Redis):** async email sending (registration confirmation,
  order confirmation), any background recalculation jobs (e.g. "trending
  products").

---

## 6. Project scaffolding (this step)

Created the full directory skeleton matching the layered architecture above,
`pyproject.toml` (uv-managed), `.env.example`, `.gitignore`, and this log.
No business logic yet — this is purely the structural foundation the rest of
the project will be built on top of, one feature/commit at a time.

---

## 7. Database schema: Class Table Inheritance over `products`

**Decision:** a shared `products` table holds catalog-wide fields (price,
stock, rating, category, etc.), and each component type (CPU, GPU,
motherboard, RAM, storage, PSU, case, cooler) has its own extension table
with `product_id` as both primary key and foreign key — a strict 1:1
relationship.

**Alternatives considered:**

| Option | Why rejected / accepted |
|---|---|
| Single `products` table + JSONB `specs` column | Simple, flexible for adding new component types, but specs become unindexable/un-typed at the DB level — exactly wrong for a compatibility engine that needs to query `WHERE socket = 'AM5'` directly and rely on the DB to reject typos. |
| Fully separate, unrelated tables per component (no shared `products`) | Loses all the shared catalog logic (price, stock, cart, orders, reviews would need to be duplicated or polymorphic per type) — much worse. |
| Class Table Inheritance (shared `products` + typed extension tables) | Chosen. Generic commerce fields live once; compatibility-relevant fields (socket, wattage, length_mm, form_factor...) are typed columns, indexable, and validated by Postgres ENUM/CHECK constraints. |

**Polymorphic access:** chose **manual JOINs in the repository layer** over
SQLAlchemy's `Joined Table Inheritance` (`polymorphic_identity` mapping).
Manual JOINs keep the generated SQL transparent and easy to reason about —
important for a compatibility engine where query correctness has real
consequences (a bad join could silently recommend an incompatible part). It
also avoids fighting the inheritance mapper's polymorphic loading config when
all that's needed in practice is "give me the CPU row joined to its product
row."

**Many-to-many junctions instead of array columns:** `case_form_factor_support`
and `cpu_cooler_socket_support` model the fact that one case supports several
motherboard form factors, and one cooler supports several CPU sockets.
Modeled as junction tables (not Postgres array columns) so they stay joinable
and indexable like the rest of the compatibility data, and so adding/removing
a supported socket doesn't require rewriting an array.

**Enums as Postgres ENUM types:** `socket`, `memory_type`, `form_factor`, etc.
are Python `str, enum.Enum` classes mapped to native Postgres `ENUM` types
(not free-text strings, not Python-side-only enums). This pushes validation
down to the database itself — a write with `socket = "am5"` (wrong case) or
any value outside the known set is rejected at the DB layer, not just by
application code that might have a bug. Since several tables share the same
enum type (e.g. `cpu_socket` used by both `cpus` and `motherboards`), the
initial migration creates each Postgres ENUM type explicitly once
(`checkfirst=True`) rather than letting SQLAlchemy attempt to auto-create it
per-column, which would error on the second table.

**Guest builds:** the product spec requires that unauthenticated users can
use the Smart PC Builder. `builds.user_id` is nullable; an unauthenticated
build is instead identified by a `guest_token` (a UUID issued client-side and
persisted in a cookie/localStorage). A `CHECK` constraint enforces that at
least one of `user_id` / `guest_token` is always present — a build can never
be ownerless. This also gives a clean later upgrade path: when a guest
registers, their build can be "claimed" by simply setting `user_id` on the
existing row instead of recreating it.

**Price snapshotting:** `order_items.price_at_purchase` stores the price at
the time of purchase, separate from `products.price`. Order history must stay
accurate even after a product's price changes — a common real-world
correctness requirement that's easy to miss if you just join to the live
products table.

**Indexing decisions:**
- `products.slug`, `users.email`, `categories.slug` — unique B-tree indexes
  for lookup/routing.
- `products(category_id, price)` — composite index matching the most common
  catalog query shape: filter by category, sort/range by price.
- `products.is_active` — indexed since the vast majority of catalog queries
  filter on it.
- `cpus.socket`, `motherboards.socket`, `motherboards.form_factor`,
  `ram.memory_type`, `storage.storage_type`, `psus.wattage`,
  `cases.is_small_form_factor` — indexed because these are exactly the
  columns the compatibility engine and Smart Builder filters will query on.

**Naming convention:** `Base.metadata` is configured with an explicit
constraint naming convention (`ix_/uq_/ck_/fk_/pk_` prefixes) up front. Without
this, Alembic autogenerate produces inconsistent, auto-generated constraint
names across migrations, which makes future migration diffs noisy and harder
to review.

**Note on this environment:** this sandbox has no network access and no
Postgres instance running, so the migration could not be executed or
autogenerate-verified against a live database here — only syntax-checked.
Before running the project, verify the migration with
`alembic upgrade head` against a real Postgres instance (e.g. via the Docker
Compose setup planned in a later step).
