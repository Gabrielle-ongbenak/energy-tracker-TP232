"""
Opérations CRUD et calculs d'analyse descriptive.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.models import ConsommationEnergie
from backend.schemas import ConsommationCreate
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional


# ─────────────────────────────────────────────
# CRUD
# ─────────────────────────────────────────────

def creer_consommation(db: Session, data: ConsommationCreate) -> ConsommationEnergie:
    """Enregistre une nouvelle consommation en base."""
    # Calcul automatique de la puissance en Watts
    puissance = None
    if data.duree_utilisation_h > 0:
        puissance = round((data.consommation_kwh / data.duree_utilisation_h) * 1000, 2)

    entree = ConsommationEnergie(
        date=data.date,
        type_appareil=data.type_appareil,
        consommation_kwh=data.consommation_kwh,
        duree_utilisation_h=data.duree_utilisation_h,
        puissance_w=puissance,
        notes=data.notes,
    )
    db.add(entree)
    db.commit()
    db.refresh(entree)
    return entree


def lire_consommations(
    db: Session,
    skip: int = 0,
    limit: int = 1000,
    appareil: Optional[str] = None,
    date_debut: Optional[datetime] = None,
    date_fin: Optional[datetime] = None,
) -> list[ConsommationEnergie]:
    """Récupère les consommations avec filtres optionnels."""
    q = db.query(ConsommationEnergie)
    if appareil:
        q = q.filter(ConsommationEnergie.type_appareil == appareil)
    if date_debut:
        q = q.filter(ConsommationEnergie.date >= date_debut)
    if date_fin:
        q = q.filter(ConsommationEnergie.date <= date_fin)
    return q.order_by(ConsommationEnergie.date.desc()).offset(skip).limit(limit).all()


def supprimer_consommation(db: Session, consommation_id: int) -> bool:
    """Supprime une entrée par son ID."""
    entree = db.query(ConsommationEnergie).filter(ConsommationEnergie.id == consommation_id).first()
    if not entree:
        return False
    db.delete(entree)
    db.commit()
    return True


# ─────────────────────────────────────────────
# ANALYSE DESCRIPTIVE
# ─────────────────────────────────────────────

def calculer_statistiques(db: Session) -> dict:
    """Calcule les statistiques descriptives complètes."""
    enregistrements = db.query(ConsommationEnergie).all()

    if not enregistrements:
        return None

    df = pd.DataFrame([e.to_dict() for e in enregistrements])
    df["date"] = pd.to_datetime(df["date"])
    df["jour"] = df["date"].dt.date

    # Statistiques de base sur la consommation
    kwh = df["consommation_kwh"]
    duree = df["duree_utilisation_h"]

    # Corrélation Pearson entre durée et consommation
    correlation = float(np.corrcoef(duree.values, kwh.values)[0, 1])

    # Appareil le plus consommateur
    top_appareil = (
        df.groupby("type_appareil")["consommation_kwh"]
        .sum()
        .idxmax()
    )

    # Moyenne journalière
    conso_par_jour = df.groupby("jour")["consommation_kwh"].sum()

    # Coût estimé (100 FCFA / kWh — tarif résidentiel AES SONEL Cameroun approx.)
    TARIF_FCFA_KWH = 100

    return {
        "total_kwh": round(float(kwh.sum()), 3),
        "moyenne_journaliere_kwh": round(float(conso_par_jour.mean()), 3),
        "ecart_type_kwh": round(float(kwh.std()), 3),
        "min_kwh": round(float(kwh.min()), 3),
        "max_kwh": round(float(kwh.max()), 3),
        "mediane_kwh": round(float(kwh.median()), 3),
        "nb_enregistrements": len(df),
        "nb_jours": int(df["jour"].nunique()),
        "correlation_duree_conso": round(correlation, 4),
        "appareil_plus_consommateur": top_appareil,
        "cout_estime_fcfa": round(float(kwh.sum()) * TARIF_FCFA_KWH, 0),
    }


def get_dataframe(db: Session) -> pd.DataFrame:
    """Retourne toutes les données sous forme de DataFrame."""
    enregistrements = db.query(ConsommationEnergie).all()
    if not enregistrements:
        return pd.DataFrame()
    df = pd.DataFrame([e.to_dict() for e in enregistrements])
    df["date"] = pd.to_datetime(df["date"])
    return df
