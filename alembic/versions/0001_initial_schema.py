"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-06-30

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# --- Enum type definitions -------------------------------------------------
# Created explicitly once (checkfirst=True) because several tables share the
# same Postgres ENUM type (e.g. `cpu_socket` is used by both `cpus` and
# `motherboards`) — letting SQLAlchemy auto-create the type per-column would
# attempt CREATE TYPE twice and fail.

user_role = postgresql.ENUM("admin", "user", name="user_role")
cpu_socket = postgresql.ENUM("AM5", "AM4", "LGA1700", "LGA1851", name="cpu_socket")
memory_type = postgresql.ENUM("DDR4", "DDR5", name="memory_type")
form_factor = postgresql.ENUM("ATX", "mATX", "ITX", "EATX", name="form_factor")
psu_form_factor = postgresql.ENUM("ATX", "SFX", "SFX-L", name="psu_form_factor")
psu_efficiency = postgresql.ENUM(
    "80+ Bronze", "80+ Silver", "80+ Gold", "80+ Platinum", "80+ Titanium",
    name="psu_efficiency",
)
psu_modularity = postgresql.ENUM("Full", "Semi", "None", name="psu_modularity")
storage_type = postgresql.ENUM("SSD_NVME", "SSD_SATA", "HDD", name="storage_type")
storage_interface = postgresql.ENUM("NVMe", "SATA", name="storage_interface")
cooler_type = postgresql.ENUM("Air", "AIO_Liquid", name="cooler_type")
component_role = postgresql.ENUM(
    "CPU", "GPU", "MOTHERBOARD", "RAM", "STORAGE", "PSU", "CASE", "COOLER",
    name="component_role",
)
order_status = postgresql.ENUM(
    "pending", "paid", "shipped", "delivered", "cancelled", name="order_status"
)

ALL_ENUMS = [
    user_role, cpu_socket, memory_type, form_factor, psu_form_factor,
    psu_efficiency, psu_modularity, storage_type, storage_interface,
    cooler_type, component_role, order_status,
]


def upgrade() -> None:
    bind = op.get_bind()
    for enum_type in ALL_ENUMS:
        enum_type.create(bind, checkfirst=True)

    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("role", user_role, nullable=False, server_default="user"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"])

    # --- categories ---
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.UniqueConstraint("name", name="uq_categories_name"),
        sa.UniqueConstraint("slug", name="uq_categories_slug"),
    )
    op.create_index("ix_categories_slug", "categories", ["slug"])

    # --- products ---
    op.create_table(
        "products",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("category_id", sa.Integer, sa.ForeignKey("categories.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False),
        sa.Column("brand", sa.String(100), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("stock_quantity", sa.Integer, nullable=False, server_default="0"),
        sa.Column("description", sa.Text),
        sa.Column("image_url", sa.String(500)),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("avg_rating", sa.Numeric(3, 2), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint("slug", name="uq_products_slug"),
    )
    op.create_index("ix_products_slug", "products", ["slug"])
    op.create_index("ix_products_is_active", "products", ["is_active"])
    op.create_index("ix_products_category_price", "products", ["category_id", "price"])

    # --- component extension tables (1:1 with products) ---
    op.create_table(
        "cpus",
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id"), primary_key=True),
        sa.Column("socket", cpu_socket, nullable=False),
        sa.Column("cores", sa.Integer, nullable=False),
        sa.Column("threads", sa.Integer, nullable=False),
        sa.Column("base_clock_ghz", sa.Numeric(3, 2), nullable=False),
        sa.Column("boost_clock_ghz", sa.Numeric(3, 2), nullable=False),
        sa.Column("tdp_watts", sa.Integer, nullable=False),
        sa.Column("has_integrated_graphics", sa.Boolean, server_default=sa.false()),
        sa.Column("max_memory_type", memory_type, nullable=False),
    )
    op.create_index("ix_cpus_socket", "cpus", ["socket"])

    op.create_table(
        "gpus",
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id"), primary_key=True),
        sa.Column("chipset", sa.String(100), nullable=False),
        sa.Column("vram_gb", sa.Integer, nullable=False),
        sa.Column("length_mm", sa.Integer, nullable=False),
        sa.Column("tdp_watts", sa.Integer, nullable=False),
        sa.Column("recommended_psu_watts", sa.Integer, nullable=False),
    )

    op.create_table(
        "motherboards",
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id"), primary_key=True),
        sa.Column("socket", cpu_socket, nullable=False),
        sa.Column("chipset", sa.String(100), nullable=False),
        sa.Column("form_factor", form_factor, nullable=False),
        sa.Column("memory_type", memory_type, nullable=False),
        sa.Column("memory_slots", sa.Integer, nullable=False),
        sa.Column("max_memory_gb", sa.Integer, nullable=False),
        sa.Column("wifi_built_in", sa.Boolean, server_default=sa.false()),
        sa.Column("pcie_x16_slots", sa.Integer, server_default="1"),
    )
    op.create_index("ix_motherboards_socket", "motherboards", ["socket"])
    op.create_index("ix_motherboards_form_factor", "motherboards", ["form_factor"])

    op.create_table(
        "ram",
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id"), primary_key=True),
        sa.Column("memory_type", memory_type, nullable=False),
        sa.Column("capacity_gb", sa.Integer, nullable=False),
        sa.Column("speed_mhz", sa.Integer, nullable=False),
        sa.Column("modules_count", sa.Integer, nullable=False, server_default="2"),
    )
    op.create_index("ix_ram_memory_type", "ram", ["memory_type"])

    op.create_table(
        "storage",
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id"), primary_key=True),
        sa.Column("storage_type", storage_type, nullable=False),
        sa.Column("interface", storage_interface, nullable=False),
        sa.Column("capacity_gb", sa.Integer, nullable=False),
        sa.Column("read_speed_mbps", sa.Integer),
        sa.Column("write_speed_mbps", sa.Integer),
    )
    op.create_index("ix_storage_storage_type", "storage", ["storage_type"])

    op.create_table(
        "psus",
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id"), primary_key=True),
        sa.Column("wattage", sa.Integer, nullable=False),
        sa.Column("efficiency_rating", psu_efficiency, nullable=False),
        sa.Column("modularity", psu_modularity, nullable=False),
        sa.Column("form_factor", psu_form_factor, nullable=False),
    )
    op.create_index("ix_psus_wattage", "psus", ["wattage"])

    op.create_table(
        "cases",
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id"), primary_key=True),
        sa.Column("max_gpu_length_mm", sa.Integer, nullable=False),
        sa.Column("max_cooler_height_mm", sa.Integer, nullable=False),
        sa.Column("supports_psu_form_factor", psu_form_factor, nullable=False),
        sa.Column("is_small_form_factor", sa.Boolean, server_default=sa.false()),
    )
    op.create_index("ix_cases_is_small_form_factor", "cases", ["is_small_form_factor"])

    op.create_table(
        "case_form_factor_support",
        sa.Column("case_id", sa.Integer, sa.ForeignKey("cases.product_id"), primary_key=True),
        sa.Column("form_factor", form_factor, primary_key=True),
    )

    op.create_table(
        "cpu_coolers",
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id"), primary_key=True),
        sa.Column("cooler_type", cooler_type, nullable=False),
        sa.Column("height_mm", sa.Integer),
        sa.Column("max_tdp_watts", sa.Integer, nullable=False),
    )

    op.create_table(
        "cpu_cooler_socket_support",
        sa.Column(
            "cooler_id", sa.Integer, sa.ForeignKey("cpu_coolers.product_id"), primary_key=True
        ),
        sa.Column("socket", cpu_socket, primary_key=True),
    )

    # --- e-commerce tables ---
    op.create_table(
        "favorites",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id"), primary_key=True),
    )

    op.create_table(
        "cart_items",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id"), nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "product_id", name="uq_cart_user_product"),
    )

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", order_status, nullable=False, server_default="pending"),
        sa.Column("total_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("order_id", sa.Integer, sa.ForeignKey("orders.id"), nullable=False),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id"), nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False),
        sa.Column("price_at_purchase", sa.Numeric(10, 2), nullable=False),
    )

    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id"), nullable=False),
        sa.Column("rating", sa.Integer, nullable=False),
        sa.Column("comment", sa.Text),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "product_id", name="uq_review_user_product"),
        sa.CheckConstraint("rating >= 1 AND rating <= 5", name="ck_reviews_rating_range"),
    )

    # --- Smart PC Builder ---
    op.create_table(
        "builds",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        # Nullable: guests can create builds without an account (see model docstring).
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("guest_token", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(255), nullable=False, server_default="My Build"),
        sa.Column("total_price", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("gaming_score", sa.Integer),
        sa.Column("programming_score", sa.Integer),
        sa.Column("rendering_score", sa.Integer),
        sa.Column("ai_score", sa.Integer),
        sa.Column("streaming_score", sa.Integer),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.CheckConstraint(
            "user_id IS NOT NULL OR guest_token IS NOT NULL", name="ck_builds_owner_required"
        ),
    )
    op.create_index("ix_builds_guest_token", "builds", ["guest_token"])

    op.create_table(
        "build_items",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("build_id", sa.Integer, sa.ForeignKey("builds.id"), nullable=False),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id"), nullable=False),
        sa.Column("component_role", component_role, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("build_items")
    op.drop_table("builds")
    op.drop_table("reviews")
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_table("cart_items")
    op.drop_table("favorites")
    op.drop_table("cpu_cooler_socket_support")
    op.drop_table("cpu_coolers")
    op.drop_table("case_form_factor_support")
    op.drop_table("cases")
    op.drop_table("psus")
    op.drop_table("storage")
    op.drop_table("ram")
    op.drop_table("motherboards")
    op.drop_table("gpus")
    op.drop_table("cpus")
    op.drop_table("products")
    op.drop_table("categories")
    op.drop_table("users")

    bind = op.get_bind()
    for enum_type in reversed(ALL_ENUMS):
        enum_type.drop(bind, checkfirst=True)
