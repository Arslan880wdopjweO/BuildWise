"""Async SQLAlchemy engine & session factory.

A single AsyncEngine is created per process. `get_session` is a FastAPI
dependency (wired in `app/core/dependencies.py` later) that yields a session
per-request and guarantees it's closed afterward — repositories never create
their own sessions, they always receive one via dependency injection.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.database_url, echo=settings.app_debug, future=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
