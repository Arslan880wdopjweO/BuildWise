# PC Parts Store & Smart PC Builder

A production-style e-commerce backend for computer components, featuring a
**rule-based Smart PC Builder**: users describe their needs (budget, use case,
resolution, preferences) and the backend recommends a fully compatible build —
validated component-by-component (socket, RAM type, PSU wattage, case clearance, etc.)
and scored per workload (Gaming / Programming / Rendering / AI / Streaming).

> Status: 🚧 in active development — built incrementally, one feature per commit.
> See [`docs/architecture.md`](docs/architecture.md) for design decisions and rationale.

## Tech Stack

- **API**: FastAPI, Pydantic v2
- **Data**: PostgreSQL, SQLAlchemy 2.0 (async), Alembic migrations
- **Auth**: JWT access/refresh tokens, bcrypt, role-based permissions
- **Async/Background**: Redis, Celery
- **Infra**: Docker, Docker Compose
- **Testing**: Pytest (unit / integration / e2e)
- **Package management**: uv

## Architecture

Clean Architecture / modular monolith — see [`docs/architecture.md`](docs/architecture.md)
for the full breakdown of layers and why each exists.

```
app/
├── api/              # FastAPI routers, request/response wiring (thin)
├── core/              # config, security, exceptions, shared DI
├── domain/            # pure business logic — compatibility & recommendation engines
├── application/       # use-case orchestration (service layer)
├── infrastructure/    # SQLAlchemy models, repositories, Redis, Celery
└── schemas/           # Pydantic DTOs
```

## Getting Started

> Setup instructions will be added once the Docker environment is in place (next steps).

## Roadmap

- [x] Project scaffolding & architecture
- [x] Database schema & migrations
- [ ] Auth (register/login/refresh/logout, RBAC)
- [ ] Product catalog (CRUD, search, filters, pagination)
- [ ] Cart, Favorites, Orders, Reviews
- [ ] Compatibility Engine
- [ ] Smart PC Builder + Recommendation Engine
- [ ] Performance Score calculator
- [ ] Admin panel
- [ ] Dockerization
- [ ] Tests (unit/integration/e2e)
- [ ] CI
