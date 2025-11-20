# database.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# ============================================================
# 🔹 URL de conexión (Citus coordinador)
# ============================================================
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres123@citus_coordinator:5432/citus"
)

# ============================================================
# 🔹 Engine asincrónico
# ============================================================
engine = create_async_engine(
    DATABASE_URL,
    echo=True,            # Muestra las consultas SQL
    future=True,
    pool_pre_ping=True    # Verifica conexiones muertas
)

# ============================================================
# 🔹 Session asincrónica
# ============================================================
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,   # Evita recargas innecesarias
    autoflush=False,
    autocommit=False
)

# ============================================================
# 🔹 Declarative Base
# ============================================================
Base = declarative_base()

# ============================================================
# 🔹 Dependencia para obtener DB en FastAPI
# ============================================================
async def get_db():
    session = async_session()
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
