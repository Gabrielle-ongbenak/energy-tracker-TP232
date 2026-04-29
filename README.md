# ⚡ Energy Tracker — TP INF 232

Suivi de consommation d'énergie domestique : collecte, stockage et analyse descriptive.

---

## Architecture

```
energy_tracker/
├── main.py                  ← Point d'entrée FastAPI
├── requirements.txt
├── seed_data.py             ← Données de démonstration
├── backend/
│   ├── __init__.py
│   ├── models.py            ← Modèles SQLAlchemy (ORM)
│   ├── database.py          ← Connexion SQLite
│   ├── schemas.py           ← Schémas Pydantic (validation)
│   └── crud.py              ← Opérations DB + Analyse Pandas/NumPy
├── frontend/
│   └── app.py               ← Dashboard Streamlit
└── data/
    └── energy_tracker.db    ← Base de données SQLite (auto-créée)
```

---

## Installation

```bash
# 1. Cloner/décompresser le projet
cd energy_tracker

# 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate       # Linux/Mac
venv\Scripts\activate          # Windows

# 3. Installer les dépendances
pip install -r requirements.txt
```

---

## Démarrage

### Terminal 1 — Backend API
```bash
uvicorn main:app --reload --port 8000
```
→ API disponible sur http://localhost:8000  
→ Documentation interactive : http://localhost:8000/docs

### Terminal 2 — Frontend Dashboard
```bash
streamlit run frontend/app.py
```
→ Dashboard disponible sur http://localhost:8501

### (Optionnel) Charger les données de démo
```bash
python seed_data.py
```

---

## Fonctionnalités

| Fonctionnalité | Endpoint / Page |
|---|---|
| Saisie de données | `➕ Saisie` / `POST /consommations` |
| Visualisation KPIs | `📊 Dashboard` |
| Histogramme + Scatter | `📈 Analyse` |
| Tableau + Filtres | `📋 Données` |
| Export CSV | `📋 Données` → bouton téléchargement |
| Statistiques descriptives | `GET /statistiques` |

---

## Technologies

- **Backend** : FastAPI + SQLAlchemy + SQLite
- **Analyse** : Pandas + NumPy (moyenne, écart-type, corrélation Pearson)
- **Frontend** : Streamlit + Plotly (graphiques interactifs)
- **Export** : CSV natif (compatible Excel, R, scikit-learn)
