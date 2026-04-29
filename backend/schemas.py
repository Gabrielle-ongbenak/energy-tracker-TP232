"""
Schémas Pydantic pour la validation des données API.
"""
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional


class ConsommationCreate(BaseModel):
    """Schéma pour créer une nouvelle entrée de consommation."""
    date: datetime
    type_appareil: str = Field(..., min_length=2, max_length=100)
    consommation_kwh: float = Field(..., gt=0, description="Consommation en kWh (doit être > 0)")
    duree_utilisation_h: float = Field(..., gt=0, le=24, description="Durée en heures (0-24h)")
    notes: Optional[str] = Field(None, max_length=500)

    @validator("consommation_kwh")
    def validate_kwh(cls, v):
        if v > 100:
            raise ValueError("Consommation trop élevée (max 100 kWh par entrée)")
        return round(v, 4)

    @validator("duree_utilisation_h")
    def validate_duree(cls, v):
        return round(v, 2)

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2025-04-15T08:00:00",
                "type_appareil": "Climatiseur",
                "consommation_kwh": 2.5,
                "duree_utilisation_h": 5.0,
                "notes": "Nuit chaude, utilisation continue"
            }
        }


class ConsommationResponse(ConsommationCreate):
    """Schéma pour la réponse de l'API (inclut les champs générés)."""
    id: int
    puissance_w: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class StatistiquesResponse(BaseModel):
    """Schéma pour les statistiques descriptives."""
    total_kwh: float
    moyenne_journaliere_kwh: float
    ecart_type_kwh: float
    min_kwh: float
    max_kwh: float
    mediane_kwh: float
    nb_enregistrements: int
    nb_jours: int
    correlation_duree_conso: float
    appareil_plus_consommateur: str
    cout_estime_fcfa: float  # 1 kWh ≈ 100 FCFA au Cameroun


class Appareils(BaseModel):
    """Liste des appareils disponibles."""
    appareils: list[str]
