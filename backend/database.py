"""
Configuration et initialisation de la base de données SQLite.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models import Base
import os

DATABASE_URL = "sqlite:///./data/energy_tracker.db"

# Assurer que le dossier data existe
os.makedirs("data", exist_ok=True)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Nécessaire pour SQLite + FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Crée toutes les tables si elles n'existent pas."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Générateur de session DB pour FastAPI (dependency injection)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
