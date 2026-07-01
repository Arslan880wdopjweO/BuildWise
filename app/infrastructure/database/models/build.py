import uuid
from decimal import Decimal

from sqlalchemy import CheckConstraint, Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, TimestampMixin
from app.infrastructure.database.models.enums import ComponentRole


class Build(Base, TimestampMixin):
    """A saved PC build, produced either manually or via the Smart Builder.

    Guests are allowed to build without registering (per product requirement),
    so `user_id` is nullable. For guests, `guest_token` (a random UUID issued
    to the client and stored e.g. in a cookie/localStorage) identifies the
    build instead — this lets a guest revisit/edit their build, and gives us
    a clean migration path: a guest build can later be claimed by a user_id
    once they register, by just filling in that FK.
    """

    __tablename__ = "builds"
    __table_args__ = (
        CheckConstraint(
            "user_id IS NOT NULL OR guest_token IS NOT NULL", name="owner_required"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    guest_token: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(255), default="My Build", nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0, nullable=False)

    # Performance scores (0-100), computed by the recommendation engine.
    gaming_score: Mapped[int | None]
    programming_score: Mapped[int | None]
    rendering_score: Mapped[int | None]
    ai_score: Mapped[int | None]
    streaming_score: Mapped[int | None]


class BuildItem(Base):
    __tablename__ = "build_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    build_id: Mapped[int] = mapped_column(ForeignKey("builds.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    component_role: Mapped[ComponentRole] = mapped_column(
        Enum(ComponentRole, name="component_role"), nullable=False
    )
