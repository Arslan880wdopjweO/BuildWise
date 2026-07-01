"""Enums shared across ORM models.

Using Python enums (mapped to Postgres ENUM types via SQLAlchemy) instead of
plain strings is deliberate: it gives us DB-level validation. The compatibility
engine compares values like CPU socket against motherboard socket directly —
"AM5" must never silently mismatch "am5" or "AM-5" due to a typo, and a
Postgres-level CHECK on the enum makes that impossible at the data layer,
not just in application code.
"""

import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"


class CpuSocket(str, enum.Enum):
    AM5 = "AM5"
    AM4 = "AM4"
    LGA1700 = "LGA1700"
    LGA1851 = "LGA1851"


class MemoryType(str, enum.Enum):
    DDR4 = "DDR4"
    DDR5 = "DDR5"


class FormFactor(str, enum.Enum):
    ATX = "ATX"
    MATX = "mATX"
    ITX = "ITX"
    EATX = "EATX"


class PsuFormFactor(str, enum.Enum):
    ATX = "ATX"
    SFX = "SFX"
    SFX_L = "SFX-L"


class PsuEfficiency(str, enum.Enum):
    BRONZE = "80+ Bronze"
    SILVER = "80+ Silver"
    GOLD = "80+ Gold"
    PLATINUM = "80+ Platinum"
    TITANIUM = "80+ Titanium"


class PsuModularity(str, enum.Enum):
    FULL = "Full"
    SEMI = "Semi"
    NONE = "None"


class StorageType(str, enum.Enum):
    SSD_NVME = "SSD_NVME"
    SSD_SATA = "SSD_SATA"
    HDD = "HDD"


class StorageInterface(str, enum.Enum):
    NVME = "NVMe"
    SATA = "SATA"


class CoolerType(str, enum.Enum):
    AIR = "Air"
    AIO_LIQUID = "AIO_Liquid"


class ComponentRole(str, enum.Enum):
    CPU = "CPU"
    GPU = "GPU"
    MOTHERBOARD = "MOTHERBOARD"
    RAM = "RAM"
    STORAGE = "STORAGE"
    PSU = "PSU"
    CASE = "CASE"
    COOLER = "COOLER"


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
