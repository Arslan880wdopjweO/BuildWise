"""Component extension tables (Class Table Inheritance over `products`).

Each table's primary key is also a foreign key to `products.id` — a strict
1:1 relationship. This keeps generic catalog data (price, stock, rating) in
one place while letting each component type have its own typed, indexable,
DB-validated columns — which is exactly what the compatibility engine needs
to query directly in SQL (e.g. "all motherboards WHERE socket = 'AM5'").
"""

from sqlalchemy import Boolean, Enum, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base
from app.infrastructure.database.models.enums import (
    CoolerType,
    CpuSocket,
    FormFactor,
    MemoryType,
    PsuEfficiency,
    PsuFormFactor,
    PsuModularity,
    StorageInterface,
    StorageType,
)


class Cpu(Base):
    __tablename__ = "cpus"

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), primary_key=True)
    socket: Mapped[CpuSocket] = mapped_column(
        Enum(CpuSocket, name="cpu_socket"), nullable=False, index=True
    )
    cores: Mapped[int] = mapped_column(nullable=False)
    threads: Mapped[int] = mapped_column(nullable=False)
    base_clock_ghz: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False)
    boost_clock_ghz: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False)
    tdp_watts: Mapped[int] = mapped_column(nullable=False)
    has_integrated_graphics: Mapped[bool] = mapped_column(Boolean, default=False)
    max_memory_type: Mapped[MemoryType] = mapped_column(
        Enum(MemoryType, name="memory_type"), nullable=False
    )


class Gpu(Base):
    __tablename__ = "gpus"

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), primary_key=True)
    chipset: Mapped[str] = mapped_column(nullable=False)
    vram_gb: Mapped[int] = mapped_column(nullable=False)
    length_mm: Mapped[int] = mapped_column(nullable=False)
    tdp_watts: Mapped[int] = mapped_column(nullable=False)
    recommended_psu_watts: Mapped[int] = mapped_column(nullable=False)


class Motherboard(Base):
    __tablename__ = "motherboards"

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), primary_key=True)
    socket: Mapped[CpuSocket] = mapped_column(
        Enum(CpuSocket, name="cpu_socket"), nullable=False, index=True
    )
    chipset: Mapped[str] = mapped_column(nullable=False)
    form_factor: Mapped[FormFactor] = mapped_column(
        Enum(FormFactor, name="form_factor"), nullable=False, index=True
    )
    memory_type: Mapped[MemoryType] = mapped_column(
        Enum(MemoryType, name="memory_type"), nullable=False
    )
    memory_slots: Mapped[int] = mapped_column(nullable=False)
    max_memory_gb: Mapped[int] = mapped_column(nullable=False)
    wifi_built_in: Mapped[bool] = mapped_column(Boolean, default=False)
    pcie_x16_slots: Mapped[int] = mapped_column(default=1)


class Ram(Base):
    __tablename__ = "ram"

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), primary_key=True)
    memory_type: Mapped[MemoryType] = mapped_column(
        Enum(MemoryType, name="memory_type"), nullable=False, index=True
    )
    capacity_gb: Mapped[int] = mapped_column(nullable=False)
    speed_mhz: Mapped[int] = mapped_column(nullable=False)
    modules_count: Mapped[int] = mapped_column(default=2, nullable=False)


class Storage(Base):
    __tablename__ = "storage"

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), primary_key=True)
    storage_type: Mapped[StorageType] = mapped_column(
        Enum(StorageType, name="storage_type"), nullable=False, index=True
    )
    interface: Mapped[StorageInterface] = mapped_column(
        Enum(StorageInterface, name="storage_interface"), nullable=False
    )
    capacity_gb: Mapped[int] = mapped_column(nullable=False)
    read_speed_mbps: Mapped[int | None]
    write_speed_mbps: Mapped[int | None]


class Psu(Base):
    __tablename__ = "psus"

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), primary_key=True)
    wattage: Mapped[int] = mapped_column(nullable=False, index=True)
    efficiency_rating: Mapped[PsuEfficiency] = mapped_column(
        Enum(PsuEfficiency, name="psu_efficiency"), nullable=False
    )
    modularity: Mapped[PsuModularity] = mapped_column(
        Enum(PsuModularity, name="psu_modularity"), nullable=False
    )
    form_factor: Mapped[PsuFormFactor] = mapped_column(
        Enum(PsuFormFactor, name="psu_form_factor"), nullable=False
    )


class Case(Base):
    __tablename__ = "cases"

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), primary_key=True)
    max_gpu_length_mm: Mapped[int] = mapped_column(nullable=False)
    max_cooler_height_mm: Mapped[int] = mapped_column(nullable=False)
    supports_psu_form_factor: Mapped[PsuFormFactor] = mapped_column(
        Enum(PsuFormFactor, name="psu_form_factor"), nullable=False
    )
    is_small_form_factor: Mapped[bool] = mapped_column(Boolean, default=False, index=True)


class CaseFormFactorSupport(Base):
    """A case can support multiple motherboard form factors (e.g. an ATX
    case usually also fits mATX and ITX boards) — modeled as a many-to-many
    junction table rather than an array column, so it stays queryable and
    indexable like the rest of the compatibility-relevant data.
    """

    __tablename__ = "case_form_factor_support"

    case_id: Mapped[int] = mapped_column(ForeignKey("cases.product_id"), primary_key=True)
    form_factor: Mapped[FormFactor] = mapped_column(
        Enum(FormFactor, name="form_factor"), primary_key=True
    )


class CpuCooler(Base):
    __tablename__ = "cpu_coolers"

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), primary_key=True)
    cooler_type: Mapped[CoolerType] = mapped_column(
        Enum(CoolerType, name="cooler_type"), nullable=False
    )
    height_mm: Mapped[int | None]  # null for AIO (height isn't the constraint, radiator is)
    max_tdp_watts: Mapped[int] = mapped_column(nullable=False)


class CpuCoolerSocketSupport(Base):
    """Many-to-many: one cooler model typically supports many CPU sockets
    (e.g. a single cooler bracket kit covers AM4, AM5, LGA1700...).
    """

    __tablename__ = "cpu_cooler_socket_support"

    cooler_id: Mapped[int] = mapped_column(ForeignKey("cpu_coolers.product_id"), primary_key=True)
    socket: Mapped[CpuSocket] = mapped_column(Enum(CpuSocket, name="cpu_socket"), primary_key=True)
