"""
Script de génération de données de démonstration.
Lance ce script une fois après avoir démarré l'API.
"""
import requests
from datetime import datetime, timedelta
import random

API_URL = "http://localhost:8000"

DONNEES_DEMO = [
    ("Climatiseur", 2.8, 7.0),
    ("Climatiseur", 3.1, 8.0),
    ("Réfrigérateur", 1.2, 24.0),
    ("Réfrigérateur", 1.15, 24.0),
    ("Télévision", 0.35, 5.0),
    ("Télévision", 0.42, 6.0),
    ("Ordinateur", 0.25, 5.0),
    ("Ordinateur", 0.30, 6.0),
    ("Machine à laver", 1.5, 2.0),
    ("Chauffe-eau", 2.0, 2.0),
    ("Éclairage", 0.18, 6.0),
    ("Éclairage", 0.20, 7.0),
    ("Fer à repasser", 0.70, 1.0),
    ("Micro-ondes", 0.18, 0.5),
    ("Ventilateur", 0.06, 8.0),
    ("Climatiseur", 2.5, 6.0),
    ("Chauffe-eau", 1.8, 1.8),
    ("Ordinateur", 0.28, 5.5),
    ("Télévision", 0.38, 5.5),
    ("Machine à laver", 1.6, 2.2),
]

def seeder():
    today = datetime.now()
    print("🌱 Insertion des données de démonstration...")

    for i, (appareil, kwh, duree) in enumerate(DONNEES_DEMO):
        date = today - timedelta(days=random.randint(0, 14))
        payload = {
            "date": date.isoformat(),
            "type_appareil": appareil,
            "consommation_kwh": kwh + random.uniform(-0.1, 0.1),
            "duree_utilisation_h": duree,
            "notes": f"Mesure de démonstration #{i+1}"
        }
        r = requests.post(f"{API_URL}/consommations", json=payload)
        if r.status_code == 201:
            print(f"  ✅ {appareil} — {kwh} kWh")
        else:
            print(f"  ❌ Erreur : {r.text}")

    print(f"\n✅ {len(DONNEES_DEMO)} entrées insérées avec succès !")

if __name__ == "__main__":
    seeder()
