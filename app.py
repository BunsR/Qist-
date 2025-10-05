import streamlit as st

# Qist - Halal Investeringsapp (officiële versie)
# Auteur: BunsR
# Versie: 1.0 - educatieve MVP
# -----------------------------------------------

import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Qist - Halal Investeringsapp", page_icon="🧭", layout="centered")

# ------------------- HEADER --------------------
st.title("🧭 Qist – Halal Investeringsapp")
st.caption("Beoordeel aandelen, ETF's en crypto eenvoudig op halal-compliance volgens basiscriteria.")

# Gumroad-knop (voor abonnement)
st.markdown("---")
st.markdown("### 💳 Word Premium Lid (€2 per maand)")
st.markdown("[Klik hier om lid te worden via Gumroad](https://gumroad.com)", unsafe_allow_html=True)
st.markdown("---")

# ------------------- FUNCTIES -------------------

CSV_FILE = "verdicts.csv"

def save_result(asset_type, name, verdict, reasons):
    """Slaat resultaten op in een CSV-bestand."""
    row = {
        "datum": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "asset_type": asset_type,
        "naam": name,
        "verdict": verdict,
        "uitleg": " | ".join(reasons)
    }
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row])
    df.to_csv(CSV_FILE, index=False)

# ------------------- HALAL-CHECK -------------------

def halal_check_equity(name, sector, debt_ratio):
    haram_sectors = {"Alcohol", "Gambling", "Pork", "Conventional Banking", "Adult Entertainment", "Weapons"}
    reasons = []
    if sector in haram_sectors:
        return "❌ Haram", [f"Sectorkeuze '{sector}' valt onder uitgesloten categorieën."]
    if debt_ratio == 0:
        return "✅ Volledig Halal", ["Geen schulden – geen rente-risico."]
    if debt_ratio <= 30:
        return "✅ Halal", [f"Schuldratio {debt_ratio}% ≤ 30%."]
    if 30 < debt_ratio <= 33:
        return "⚠️ Twijfelachtig", [f"Schuldratio {debt_ratio}% ligt tussen 30% en 33%."]
    return "❌ Haram", [f"Schuldratio {debt_ratio}% > 33%."]

def halal_check_etf(name, sharia_certified, halal_pct, purification_pct):
    reasons = []
    if sharia_certified:
        return "✅ Halal", ["Shariah-gecertificeerd (extern bevestigd)."]
    if halal_pct >= 95 and purification_pct < 5:
        return "✅ Halal (Purificatie vereist)", [
            f"{halal_pct}% van holdings halal | Purificatie: {purification_pct}%"
        ]
    return "⚠️ Twijfelachtig/Haram", [f"Halal holdings: {halal_pct}%, Purificatie: {purification_pct}%"]

def halal_check_crypto(name, violates_usecase, fixed_yield, staking_service, interest_like):
    reasons = []
    if violates_usecase:
        return "❌ Haram", ["Use-case bevat verboden toepassingen (bijv. gokken, rente of adult content)."]
    if fixed_yield:
        return "❌ Haram", ["Crypto adverteert vaste (rente-achtige) opbrengst."]
    if staking_service and not interest_like:
        return "✅ Halal (Board Policy A)", ["Staking-beloningen zijn gebaseerd op servicevergoeding."]
    return "⚠️ Shubha", ["Onvoldoende informatie of twijfelachtige structuur."]

# ------------------- INTERFACE -------------------

tab1, tab2, tab3 = st.tabs(["🏢 Aandelen (Equity)", "📦 ETF's", "🪙 Crypto"])

# ---- EQUITY ----
with tab1:
    st.subheader("Aandeel beoordelen")
    name = st.text_input("Naam van het bedrijf of aandeel:")
    sector = st.selectbox("Sector", [
        "Technology","Healthcare","Energy","Broad Market","Crypto",
        "Alcohol","Gambling","Pork","Conventional Banking","Adult Entertainment","Weapons","Other"
    ])
    debt = st.number_input("Schuldratio (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
    if st.button("Check aandeel"):
        verdict, reasons = halal_check_equity(name, sector, debt)
        st.markdown(f"### Resultaat: {verdict}")
        for r in reasons:
            st.write("•", r)
        save_result("Equity", name, verdict, reasons)

# ---- ETF ----
with tab2:
    st.subheader("ETF beoordelen")
    name_etf = st.text_input("Naam van de ETF:")
    sharia_certified = st.checkbox("Shariah-gecertificeerd (extern)", value=False)
    halal_pct = st.slider("Percentage halal holdings (%)", 0, 100, 100)
    purification_pct = st.slider("Purificatie (%)", 0, 20, 0)
    if st.button("Check ETF"):
        verdict, reasons = halal_check_etf(name_etf, sharia_certified, halal_pct, purification_pct)
        st.markdown(f"### Resultaat: {verdict}")
        for r in reasons:
            st.write("•", r)
        save_result("ETF", name_etf, verdict, reasons)

# ---- CRYPTO ----
with tab3:
    st.subheader("Crypto beoordelen")
    name_crypto = st.text_input("Naam van de crypto:")
    violates_usecase = st.checkbox("Schendt halal-usecase (bijv. gokken, rente)?", value=False)
    fixed_yield = st.checkbox("Adverteert vaste (rente-achtige) yield?", value=False)
    staking_service = st.checkbox("Staking is service-based (geen rente)?", value=False)
    interest_like = st.checkbox("Zijn er rente-achtige voorwaarden?", value=False)
    if st.button("Check crypto"):
        verdict, reasons = halal_check_crypto(name_crypto, violates_usecase, fixed_yield, staking_service, interest_like)
        st.markdown(f"### Resultaat: {verdict}")
        for r in reasons:
            st.write("•", r)
        save_result("Crypto", name_crypto, verdict, reasons)

# ---- Footer ----
st.markdown("---")
st.caption("© 2025 Qist | Educatieve demo. Niet bedoeld als religieus of financieel advies.")
