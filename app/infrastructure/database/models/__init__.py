"""Import every model here so Alembic's autogenerate (and Base.metadata)
sees the full schema. Models are never imported piecemeal elsewhere for
migration purposes — always via this module.
"""

from app.infrastructure.database.base import Base
from app.infrastructure.database.models.build import Build, BuildItem
from app.infrastructure.database.models.category import Category
from app.infrastructure.database.models.commerce import (
    CartItem,
    Favorite,
    Order,
    OrderItem,
    Review,
)
from app.infrastructure.database.models.components import (
    Case,
    CaseFormFactorSupport,
    Cpu,
    CpuCooler,
    CpuCoolerSocketSupport,
    Gpu,
    Motherboard,
    Psu,
    Ram,
    Storage,
)
from app.infrastructure.database.models.product import Product
from app.infrastructure.database.models.user import User

__all__ = [
    "Base",
    "User",
    "Category",
    "Product",
    "Cpu",
    "Gpu",
    "Motherboard",
    "Ram",
    "Storage",
    "Psu",
    "Case",
    "CaseFormFactorSupport",
    "CpuCooler",
    "CpuCoolerSocketSupport",
    "Favorite",
    "CartItem",
    "Order",
    "OrderItem",
    "Review",
    "Build",
    "BuildItem",
]
