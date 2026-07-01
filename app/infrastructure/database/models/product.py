from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, TimestampMixin


class Product(Base, TimestampMixin):
    """Shared fields for every component type (catalog, cart, orders, reviews
    all reference this table). Type-specific specs live in extension tables
    — see models/components.py — joined manually via product_id.
    """

    __tablename__ = "products"
    __table_args__ = (
        # Composite index for the most common catalog query: filter by
        # category, sort/range by price.
        Index("ix_products_category_price", "category_id", "price"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    stock_quantity: Mapped[int] = mapped_column(default=0, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    avg_rating: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=0, nullable=False)
