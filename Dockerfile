# On part d'une image Python légère
FROM python:3.10-slim

# On définit le dossier de travail dans le conteneur
WORKDIR /app

# On copie le fichier des dépendances
COPY requirements.txt .

# On installe les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# On copie tout le reste du code
COPY . .

# On expose le port 8000 (celui de FastAPI)
EXPOSE 8000

# La commande pour lancer le serveur au démarrage du conteneur
CMD ["uvicorn", "streamlit run frontend/app.py", "--host", "0.0.0.0", "--port", "8000"]