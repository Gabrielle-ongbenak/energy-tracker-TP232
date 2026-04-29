"""
Modèles de données pour le suivi de consommation énergétique.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

APPAREILS_PREDÉFINIS = [
    "Climatiseur", "Réfrigérateur", "Télévision", "Ordinateur",
    "Machine à laver", "Chauffe-eau", "Éclairage", "Fer à repasser",
    "Micro-ondes", "Ventilateur", "Autre"
]


class ConsommationEnergie(Base):
    """Modèle de la table principale de consommation d'énergie."""
    __tablename__ = "consommations"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    type_appareil = Column(String(100), nullable=False)
    consommation_kwh = Column(Float, nullable=False)
    duree_utilisation_h = Column(Float, nullable=False)
    puissance_w = Column(Float, nullable=True)   # calculée automatiquement
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.isoformat() if self.date else None,
            "type_appareil": self.type_appareil,
            "consommation_kwh": self.consommation_kwh,
            "duree_utilisation_h": self.duree_utilisation_h,
            "puissance_w": self.puissance_w,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
