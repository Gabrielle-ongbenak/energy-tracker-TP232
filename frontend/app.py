"""
Dashboard Streamlit — Suivi de consommation d'énergie domestique
TP INF 232 — Interface principale
"""
import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, date, timedelta
import io

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="⚡ Energy Tracker",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }

    .main { background: #0a0e1a; }

    .kpi-card {
        background: linear-gradient(135deg, #1a1f35 0%, #12172b 100%);
        border: 1px solid #2a3050;
        border-radius: 16px;
        padding: 1.4rem 1.6rem;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #00d4ff, #7b2ff7);
    }
    .kpi-value {
        font-size: 2.2rem;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        background: linear-gradient(135deg, #00d4ff, #7b2ff7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: block;
        line-height: 1.1;
    }
    .kpi-label {
        color: #8892b0;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-top: 0.4rem;
    }
    .kpi-sub {
        color: #4fc3f7;
        font-size: 0.85rem;
        margin-top: 0.3rem;
        font-family: 'JetBrains Mono', monospace;
    }
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #cdd6f4;
        border-left: 3px solid #00d4ff;
        padding-left: 0.8rem;
        margin: 1.5rem 0 1rem 0;
    }
    .correlation-badge {
        display: inline-block;
        background: rgba(0, 212, 255, 0.1);
        border: 1px solid #00d4ff;
        color: #00d4ff;
        border-radius: 8px;
        padding: 0.3rem 0.8rem;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        font-size: 1.1rem;
    }
    div[data-testid="stSidebar"] {
        background: #0d1224;
        border-right: 1px solid #1e2640;
    }
    .stButton > button {
        background: linear-gradient(135deg, #00d4ff20, #7b2ff720);
        border: 1px solid #00d4ff50;
        color: #00d4ff;
        border-radius: 10px;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        transition: all 0.2s;
        width: 100%;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #00d4ff30, #7b2ff730);
        border-color: #00d4ff;
        transform: translateY(-1px);
    }
    .stDataFrame { border-radius: 12px; overflow: hidden; }
    .alert-success {
        background: rgba(0, 255, 100, 0.08);
        border: 1px solid #00ff6440;
        border-radius: 10px;
        padding: 0.7rem 1rem;
        color: #00ff64;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
@st.cache_data(ttl=5)
def fetch_data():
    try:
        r = requests.get(f"{API_URL}/consommations", timeout=5)
        if r.status_code == 200:
            df = pd.DataFrame(r.json())
            if not df.empty:
                df["date"] = pd.to_datetime(df["date"])
                df["jour"] = df["date"].dt.date
                df["mois"] = df["date"].dt.to_period("M").astype(str)
            return df
    except Exception:
        pass
    return pd.DataFrame()

@st.cache_data(ttl=5)
def fetch_stats():
    try:
        r = requests.get(f"{API_URL}/statistiques", timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

@st.cache_data(ttl=60)
def fetch_appareils():
    try:
        r = requests.get(f"{API_URL}/appareils", timeout=5)
        if r.status_code == 200:
            return r.json()["appareils"]
    except Exception:
        pass
    return ["Climatiseur", "Réfrigérateur", "Télévision", "Ordinateur", "Autre"]

def api_ok():
    try:
        r = requests.get(f"{API_URL}/", timeout=3)
        return r.status_code == 200
    except Exception:
        return False

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(10,14,26,0.8)",
    font=dict(family="Space Grotesk", color="#cdd6f4"),
    margin=dict(t=40, b=40, l=20, r=20),
    xaxis=dict(gridcolor="#1e2640", linecolor="#2a3050"),
    yaxis=dict(gridcolor="#1e2640", linecolor="#2a3050"),
)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("# ⚡ Energy Tracker")
    st.markdown("*TP INF 232 — Analyse descriptive*")
    st.divider()

    # Statut API
    if api_ok():
        st.markdown("🟢 **API connectée**")
    else:
        st.markdown("🔴 **API hors ligne**")
        st.error("Lance d'abord : `uvicorn main:app --reload`")

    st.divider()
    page = st.radio(
        "Navigation",
        ["📊 Dashboard", "➕ Saisie", "📋 Données", "📈 Analyse"],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("v1.0.0 · SQLite + FastAPI")

# ─────────────────────────────────────────────
# PAGE : DASHBOARD
# ─────────────────────────────────────────────
if page == "📊 Dashboard":
    st.markdown("## 📊 Tableau de bord")

    df = fetch_data()
    stats = fetch_stats()

    if df.empty or stats is None:
        st.info("Aucune donnée. Commence par saisir des mesures dans **➕ Saisie**.")
        st.stop()

    # ── KPIs ──
    st.markdown('<div class="section-title">Indicateurs clés</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="kpi-card">
            <span class="kpi-value">{stats['total_kwh']:.2f}</span>
            <div class="kpi-label">Consommation totale</div>
            <div class="kpi-sub">kWh</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="kpi-card">
            <span class="kpi-value">{stats['moyenne_journaliere_kwh']:.2f}</span>
            <div class="kpi-label">Moyenne / jour</div>
            <div class="kpi-sub">kWh/jour</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="kpi-card">
            <span class="kpi-value">{int(stats['cout_estime_fcfa']):,}</span>
            <div class="kpi-label">Coût estimé</div>
            <div class="kpi-sub">FCFA</div>
        </div>""", unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="kpi-card">
            <span class="kpi-value">{stats['nb_enregistrements']}</span>
            <div class="kpi-label">Mesures collectées</div>
            <div class="kpi-sub">sur {stats['nb_jours']} jours</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Graphiques : ligne temporelle + camembert ──
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown('<div class="section-title">Évolution journalière</div>', unsafe_allow_html=True)
        daily = df.groupby("jour")["consommation_kwh"].sum().reset_index()
        daily.columns = ["Jour", "kWh"]
        fig_line = px.area(
            daily, x="Jour", y="kWh",
            color_discrete_sequence=["#00d4ff"],
        )
        fig_line.update_traces(fill="tozeroy", fillcolor="rgba(0,212,255,0.08)", line_width=2)
        fig_line.update_layout(**PLOTLY_LAYOUT, showlegend=False)
        st.plotly_chart(fig_line, use_container_width=True)

    with col_right:
        st.markdown('<div class="section-title">Répartition appareils</div>', unsafe_allow_html=True)
        pie_data = df.groupby("type_appareil")["consommation_kwh"].sum().reset_index()
        fig_pie = px.pie(
            pie_data, values="consommation_kwh", names="type_appareil",
            color_discrete_sequence=px.colors.sequential.Plasma_r,
            hole=0.5,
        )
        fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#cdd6f4"), margin=dict(t=20, b=20))
        fig_pie.update_traces(textfont_color="#fff")
        st.plotly_chart(fig_pie, use_container_width=True)

    # ── Appareil le plus consommateur ──
    st.info(f"🏆 Appareil le plus consommateur : **{stats['appareil_plus_consommateur']}**  |  Écart-type : **{stats['ecart_type_kwh']} kWh**  |  Médiane : **{stats['mediane_kwh']} kWh**")


# ─────────────────────────────────────────────
# PAGE : SAISIE
# ─────────────────────────────────────────────
elif page == "➕ Saisie":
    st.markdown("## ➕ Saisie de consommation")

    appareils = fetch_appareils()

    with st.form("form_saisie", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            date_saisie = st.date_input("📅 Date de mesure", value=date.today())
            heure_saisie = st.time_input("🕐 Heure", value=datetime.now().time())
            appareil = st.selectbox("🔌 Type d'appareil", appareils)

        with c2:
            kwh = st.number_input(
                "⚡ Consommation (kWh)",
                min_value=0.001, max_value=100.0, value=1.0, step=0.1, format="%.3f",
                help="Relevé direct depuis le compteur ou calculé"
            )
            duree = st.number_input(
                "⏱️ Durée d'utilisation (heures)",
                min_value=0.1, max_value=24.0, value=1.0, step=0.5,
                help="Durée totale de fonctionnement"
            )
            notes = st.text_input("📝 Notes (optionnel)", placeholder="Ex: nuit chaude, utilisation continue…")

        # Preview puissance
        puissance_preview = round((kwh / duree) * 1000, 1) if duree > 0 else 0
        st.caption(f"⚙️ Puissance calculée : **{puissance_preview} W**")

        submitted = st.form_submit_button("💾 Enregistrer", use_container_width=True)

        if submitted:
            dt = datetime.combine(date_saisie, heure_saisie)
            payload = {
                "date": dt.isoformat(),
                "type_appareil": appareil,
                "consommation_kwh": kwh,
                "duree_utilisation_h": duree,
                "notes": notes or None,
            }
            try:
                r = requests.post(f"{API_URL}/consommations", json=payload)
                if r.status_code == 201:
                    st.success(f"✅ Enregistré ! {kwh} kWh pour **{appareil}** le {date_saisie}")
                    fetch_data.clear()
                    fetch_stats.clear()
                else:
                    st.error(f"Erreur API : {r.json().get('detail', r.text)}")
            except Exception as e:
                st.error(f"Connexion impossible à l'API : {e}")

    st.divider()
    st.markdown("#### 📌 Valeurs de référence (appareils courants)")
    ref_data = {
        "Appareil": ["Climatiseur 1.5 CV", "Réfrigérateur", "Télévision LED 43\"", "Ordinateur portable", "Fer à repasser"],
        "Puissance (W)": [1200, 50, 70, 45, 1000],
        "Conso estimée (kWh/h)": [1.2, 0.05, 0.07, 0.045, 1.0],
    }
    st.dataframe(pd.DataFrame(ref_data), use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────
# PAGE : DONNÉES
# ─────────────────────────────────────────────
elif page == "📋 Données":
    st.markdown("## 📋 Données collectées")

    df = fetch_data()

    if df.empty:
        st.info("Aucune donnée enregistrée pour l'instant.")
        st.stop()

    # Filtres
    st.markdown('<div class="section-title">Filtres</div>', unsafe_allow_html=True)
    fcol1, fcol2, fcol3 = st.columns(3)

    with fcol1:
        appareils_dispo = ["Tous"] + sorted(df["type_appareil"].unique().tolist())
        filtre_appareil = st.selectbox("Appareil", appareils_dispo)

    with fcol2:
        date_min = df["date"].min().date()
        date_max = df["date"].max().date()
        filtre_debut = st.date_input("Du", value=date_min)

    with fcol3:
        filtre_fin = st.date_input("Au", value=date_max)

    # Appliquer filtres
    df_filtered = df.copy()
    if filtre_appareil != "Tous":
        df_filtered = df_filtered[df_filtered["type_appareil"] == filtre_appareil]
    df_filtered = df_filtered[
        (df_filtered["date"].dt.date >= filtre_debut) &
        (df_filtered["date"].dt.date <= filtre_fin)
    ]

    st.caption(f"{len(df_filtered)} entrée(s) affichée(s) sur {len(df)} au total")

    # Tableau
    cols_display = ["date", "type_appareil", "consommation_kwh", "duree_utilisation_h", "puissance_w", "notes"]
    cols_available = [c for c in cols_display if c in df_filtered.columns]

    st.dataframe(
        df_filtered[cols_available].rename(columns={
            "date": "Date",
            "type_appareil": "Appareil",
            "consommation_kwh": "kWh",
            "duree_utilisation_h": "Durée (h)",
            "puissance_w": "Puissance (W)",
            "notes": "Notes",
        }).sort_values("Date", ascending=False),
        use_container_width=True,
        hide_index=True,
        height=400,
    )

    # Export CSV
    st.divider()
    st.markdown('<div class="section-title">Export</div>', unsafe_allow_html=True)

    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        csv_bytes = df_filtered[cols_available].to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Télécharger CSV (données filtrées)",
            data=csv_bytes,
            file_name=f"consommation_energie_{date.today()}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col_exp2:
        st.caption(f"Le fichier CSV contient {len(df_filtered)} lignes et {len(cols_available)} colonnes.")
        st.caption("✅ Format compatible avec Excel, R et les futurs TPs de régression.")

    # Suppression
    st.divider()
    with st.expander("🗑️ Supprimer une entrée"):
        del_id = st.number_input("ID de l'entrée à supprimer", min_value=1, step=1)
        if st.button("Supprimer", type="secondary"):
            r = requests.delete(f"{API_URL}/consommations/{del_id}")
            if r.status_code == 200:
                st.success(f"Entrée #{del_id} supprimée.")
                fetch_data.clear()
                fetch_stats.clear()
                st.rerun()
            else:
                st.error(r.json().get("detail", "Erreur"))


# ─────────────────────────────────────────────
# PAGE : ANALYSE
# ─────────────────────────────────────────────
elif page == "📈 Analyse":
    st.markdown("## 📈 Analyse descriptive")

    df = fetch_data()
    stats = fetch_stats()

    if df.empty or stats is None:
        st.info("Aucune donnée à analyser.")
        st.stop()

    # ── Statistiques tabulaires ──
    st.markdown('<div class="section-title">Statistiques descriptives</div>', unsafe_allow_html=True)

    stat_df = pd.DataFrame({
        "Statistique": ["Total", "Moyenne/jour", "Écart-type", "Minimum", "Maximum", "Médiane"],
        "Valeur (kWh)": [
            stats["total_kwh"], stats["moyenne_journaliere_kwh"],
            stats["ecart_type_kwh"], stats["min_kwh"],
            stats["max_kwh"], stats["mediane_kwh"]
        ]
    })
    st.dataframe(stat_df, use_container_width=True, hide_index=True)

    st.divider()

    # ── Histogramme ──
    col_h, col_s = st.columns(2)

    with col_h:
        st.markdown('<div class="section-title">Histogramme de distribution</div>', unsafe_allow_html=True)
        fig_hist = px.histogram(
            df, x="consommation_kwh", nbins=15,
            color="type_appareil",
            labels={"consommation_kwh": "Consommation (kWh)", "count": "Fréquence"},
            color_discrete_sequence=px.colors.qualitative.Vivid,
        )
        fig_hist.update_layout(**PLOTLY_LAYOUT, bargap=0.05)
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_s:
        st.markdown('<div class="section-title">Nuage de points : Durée vs Consommation</div>', unsafe_allow_html=True)
        fig_scatter = px.scatter(
            df,
            x="duree_utilisation_h",
            y="consommation_kwh",
            color="type_appareil",
            size="puissance_w" if "puissance_w" in df.columns else None,
            hover_data=["type_appareil", "notes"],
            labels={
                "duree_utilisation_h": "Durée d'utilisation (h)",
                "consommation_kwh": "Consommation (kWh)"
            },
            trendline="ols",
            color_discrete_sequence=px.colors.qualitative.Vivid,
        )
        fig_scatter.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig_scatter, use_container_width=True)

    # ── Corrélation ──
    st.divider()
    st.markdown('<div class="section-title">Analyse de corrélation</div>', unsafe_allow_html=True)

    corr = stats["correlation_duree_conso"]
    interpretation = (
        "Forte corrélation positive 📈" if corr > 0.7
        else "Corrélation modérée 📊" if corr > 0.4
        else "Faible corrélation 📉" if corr > 0
        else "Corrélation négative 🔽"
    )

    cc1, cc2 = st.columns([1, 2])
    with cc1:
        st.markdown(f"""
        <div class="kpi-card" style="margin-top:0.5rem">
            <span class="kpi-value">{corr:.4f}</span>
            <div class="kpi-label">Corrélation de Pearson</div>
            <div class="kpi-sub">Durée ↔ Consommation</div>
        </div>
        """, unsafe_allow_html=True)

    with cc2:
        st.markdown(f"**Interprétation :** {interpretation}")
        st.markdown("""
        La corrélation de Pearson mesure la relation linéaire entre la durée d'utilisation 
        et la consommation en kWh. Une valeur proche de **+1** indique que plus un appareil 
        fonctionne longtemps, plus il consomme (relation attendue).
        """)

    # ── Box plot par appareil ──
    st.divider()
    st.markdown('<div class="section-title">Distribution par appareil (Box Plot)</div>', unsafe_allow_html=True)
    fig_box = px.box(
        df, x="type_appareil", y="consommation_kwh",
        color="type_appareil",
        labels={"type_appareil": "Appareil", "consommation_kwh": "kWh"},
        color_discrete_sequence=px.colors.qualitative.Vivid,
    )
    fig_box.update_layout(**PLOTLY_LAYOUT, showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)

    # ── Tableau de corrélation numérique ──
    with st.expander("🔬 Matrice de corrélation complète"):
        num_cols = ["consommation_kwh", "duree_utilisation_h", "puissance_w"]
        num_cols = [c for c in num_cols if c in df.columns]
        corr_matrix = df[num_cols].corr()
        fig_corr = px.imshow(
            corr_matrix,
            text_auto=True,
            color_continuous_scale="RdBu_r",
            aspect="auto",
        )
        fig_corr.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#cdd6f4"))
        st.plotly_chart(fig_corr, use_container_width=True)
