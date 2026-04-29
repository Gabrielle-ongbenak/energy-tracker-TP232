"""
Point d'entrée principal de l'API FastAPI.
TP INF 232 — Suivi de consommation d'énergie domestique
"""
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import io
import csv

from backend.database import get_db, init_db
from backend.schemas import (
    ConsommationCreate,
    ConsommationResponse,
    StatistiquesResponse,
    Appareils,
)
from backend.models import APPAREILS_PREDÉFINIS
from backend import crud

# ─────────────────────────────────────────────
# Initialisation
# ─────────────────────────────────────────────
app = FastAPI(
    title="⚡ Energy Tracker API",
    description="API de suivi de consommation d'énergie domestique — TP INF 232",
    version="1.0.0",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


# ─────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────

@app.get("/", tags=["Santé"])
def root():
    return {"message": "⚡ Energy Tracker API opérationnelle", "version": "1.0.0"}


@app.get("/appareils", response_model=Appareils, tags=["Référentiel"])
def get_appareils():
    """Retourne la liste des types d'appareils disponibles."""
    return {"appareils": APPAREILS_PREDÉFINIS}


@app.post("/consommations", response_model=ConsommationResponse, status_code=201, tags=["Collecte"])
def creer_consommation(data: ConsommationCreate, db: Session = Depends(get_db)):
    """Enregistre une nouvelle mesure de consommation."""
    return crud.creer_consommation(db, data)


@app.get("/consommations", response_model=list[ConsommationResponse], tags=["Collecte"])
def lire_consommations(
    skip: int = 0,
    limit: int = 500,
    appareil: Optional[str] = Query(None, description="Filtrer par type d'appareil"),
    date_debut: Optional[datetime] = Query(None),
    date_fin: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
):
    """Récupère toutes les consommations avec filtres optionnels."""
    return crud.lire_consommations(db, skip, limit, appareil, date_debut, date_fin)


@app.delete("/consommations/{consommation_id}", tags=["Collecte"])
def supprimer_consommation(consommation_id: int, db: Session = Depends(get_db)):
    """Supprime une entrée par son ID."""
    success = crud.supprimer_consommation(db, consommation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Entrée non trouvée")
    return {"message": f"Entrée #{consommation_id} supprimée"}


@app.get("/statistiques", tags=["Analyse"])
def get_statistiques(db: Session = Depends(get_db)):
    """Retourne les statistiques descriptives complètes."""
    stats = crud.calculer_statistiques(db)
    if stats is None:
        raise HTTPException(status_code=404, detail="Aucune donnée disponible")
    return stats


@app.get("/export/csv", tags=["Export"])
def exporter_csv(db: Session = Depends(get_db)):
    """Exporte toutes les données au format CSV."""
    df = crud.get_dataframe(db)
    if df.empty:
        raise HTTPException(status_code=404, detail="Aucune donnée à exporter")

    output = io.StringIO()
    df.to_csv(output, index=False, encoding="utf-8")
    output.seek(0)

    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=consommation_energie.csv"},
    )
