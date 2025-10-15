# app.py — Qist – Check (NL/EN) + echte tickers + halal-screening + guide + analytics
import re
import json
import uuid
import hashlib
from datetime import datetime
from typing import Dict, Tuple, List, Optional

import pandas as pd
import requests
import streamlit as st
import yfinance as yf

APP_VERSION = "2025-10-15-v4"

# ---------- Basis-config ----------
st.set_page_config(page_title="Qist – Check", page_icon="✅", layout="centered")

# ---------- Taal (i18n) ----------
LANGS = {"nl": "Nederlands", "en": "English"}
if "lang" not in st.session_state:
    st.session_state.lang = "nl"
lang = st.session_state.lang

T: Dict[str, Dict[str, str]] = {
    "nl": {
        "brand_title": "Qist – Check",
        "brand_caption": "Beoordeel aandelen, ETF's en crypto op halal-compliance (educatieve demo).",
        "language": "Taal",
        "beginner_open": "Open de uitleg",
        "guide_title": "Hoe gebruik je Qist – Check?",
        "guide_steps": (
            "1) Kies je **taal** rechtsboven.\n"
            "2) Voor **aandelen**: zoek op **naam/ticker/ISIN** en kies de exacte notering.\n"
            "3) Bekijk de **basisdata** en **schuldratio**.\n"
            "4) Lees het **oordeel** (Halal / Niet halal / Ongeclassificeerd) met uitleg.\n"
            "5) Voor **ETF/crypto**: vul de vragen in → direct een oordeel.\n"
            "⚠️ Educatief; geen religieus of financieel advies."
        ),
        "tabs_equity": "🏢 Aandelen",
        "tabs_etf": "📦 ETF's",
        "tabs_crypto": "🪙 Crypto",
        "tabs_analytics": "📊 Analytics",
        "search_ph": "Zoek op bedrijfsnaam, ticker of ISIN (bijv. ASML, AAPL, NL0010273215)",
        "choose_listing": "Kies de exacte notering:",
        "no_results": "Geen noteringen gevonden. Controleer de spelling of probeer een andere zoekterm.",
        "valid_listing": "Geldige notering gevonden ✅",
        "field_name": "Naam",
        "field_ticker": "Ticker",
        "field_exchange": "Beurs",
        "field_currency": "Valuta",
        "field_country": "Land",
        "field_sector": "Sector",
        "field_industry": "Industrie",
        "field_mcap": "Market cap",
        "field_debt_ratio": "Schuldratio",
        "debt_basis_mc": "t.o.v. market cap",
        "debt_basis_assets": "t.o.v. totale activa",
        "debt_unknown": "onbekend",
        "check_equity": "Check aandeel",
        "result": "Resultaat",
        "etf_name": "Naam van de ETF",
        "etf_cert": "Shariah-gecertificeerd (extern)?",
        "etf_halal_pct": "Percentage halal holdings (%)",
        "etf_pur_pct": "Purificatie (%)",
        "check_etf": "Check ETF",
        "crypto_name": "Naam van de crypto",
        "crypto_haram_use": "Schendt halal-usecase (bijv. gokken, rente)?",
        "crypto_fixed_yield": "Adverteert vaste (rente-achtige) yield?",
        "crypto_staking_service": "Staking is service-based (geen rente)?",
        "crypto_interest_like": "Zijn er rente-achtige voorwaarden?",
        "check_crypto": "Check crypto",
        "status_halal_full": "✅ Volledig halal",
        "status_halal": "✅ Halal",
        "status_purify": "✅ Halal (purificatie vereist)",
        "status_doubt": "⚠️ Twijfelachtig",
        "status_not_halal": "❌ Niet halal",
        "status_unclassified": "❓ Ongeclassificeerd",
        "equity_rules_title": "Regels (samengevat)",
        "equity_rules": (
            "- **Verboden sectoren**: alcohol, gokken, varkensvlees, conventionele banken/verzekeraars, adult, wapens, tabak → Niet halal.\n"
            "- **Schuld-screen**: interestdragende schuld ≤ **30%** van market cap (of activa) → Halal; 30–33% → Twijfelachtig; >33% → Niet halal.\n"
            "- **Ontbrekende data** → Ongeclassificeerd."
        ),
        "footer": "© 2025 Qist | Educatieve demo. Niet bedoeld als religieus of financieel advies.",
        "admin_pin": "Admin-PIN voor analytics",
        "show_stats": "Toon statistieken",
        "stats_tip": "Configureer Google Sheets/GA4 secrets om statistieken te zien.",
    },
    "en": {
        "brand_title": "Qist – Check",
        "brand_caption": "Assess stocks, ETFs and crypto for halal compliance (educational demo).",
        "language": "Language",
        "beginner_open": "Open the guide",
        "guide_title": "How to use Qist – Check?",
        "guide_steps": (
            "1) Choose your **language** (top-right).\n"
            "2) For **equities**: search by **name/ticker/ISIN** and select the exact listing.\n"
            "3) Review **fundamentals** and **debt ratio**.\n"
            "4) Read the **verdict** (Halal / Not halal / Unclassified) with reasons.\n"
            "5) For **ETF/crypto**: answer the questions → instant verdict.\n"
            "⚠️ Educational; not religious or financial advice."
        ),
        "tabs_equity": "🏢 Stocks",
        "tabs_etf": "📦 ETFs",
        "tabs_crypto": "🪙 Crypto",
        "tabs_analytics": "📊 Analytics",
        "search_ph": "Search by company name, ticker or ISIN (e.g., ASML, AAPL, NL0010273215)",
        "choose_listing": "Select the exact listing:",
        "no_results": "No listings found. Check spelling or try another query.",
        "valid_listing": "Valid listing found ✅",
        "field_name": "Name",
        "field_ticker": "Ticker",
        "field_exchange": "Exchange",
        "field_currency": "Currency",
        "field_country": "Country",
        "field_sector": "Sector",
        "field_industry": "Industry",
        "field_mcap": "Market cap",
        "field_debt_ratio": "Debt ratio",
        "debt_basis_mc": "vs market cap",
        "debt_basis_assets": "vs total assets",
        "debt_unknown": "unknown",
        "check_equity": "Check stock",
        "result": "Result",
        "etf_name": "Name of the ETF",
        "etf_cert": "Shariah-certified (external)?",
        "etf_halal_pct": "Percentage halal holdings (%)",
        "etf_pur_pct": "Purification (%)",
        "check_etf": "Check ETF",
        "crypto_name": "Name of the crypto",
        "crypto_haram_use": "Violates halal use-case (e.g., gambling, interest)?",
        "crypto_fixed_yield": "Advertises fixed (interest-like) yield?",
        "crypto_staking_service": "Staking is service-based (no interest)?",
        "crypto_interest_like": "Interest-like terms present?",
        "check_crypto": "Check crypto",
        "status_halal_full": "✅ Fully halal",
        "status_halal": "✅ Halal",
        "status_purify": "✅ Halal (purification required)",
        "status_doubt": "⚠️ Doubtful",
        "status_not_halal": "❌ Not halal",
        "status_unclassified": "❓ Unclassified",
        "equity_rules_title": "Rules (summary)",
        "equity_rules": (
            "- **Excluded activities**: alcohol, gambling, pork, conventional banking/insurance, adult, weapons, tobacco → Not halal.\n"
            "- **Debt screen**: interest-bearing debt ≤ **30%** of market cap (or assets) → Halal; 30–33% → Doubtful; >33% → Not halal.\n"
            "- **Missing data** → Unclassified."
        ),
        "footer": "© 2025 Qist | Educational demo. Not religious or financial advice.",
        "admin_pin": "Admin PIN for analytics",
        "show_stats": "Show statistics",
        "stats_tip": "Configure Google Sheets/GA4 secrets to view stats.",
    },
}
def t(key: str) -> str:
    return T.get(lang, T["nl"]).get(key, key)

# Taalkeuze + header
colA, colB = st.columns([4,1])
with colA:
    st.title(t("brand_title"))
    st.caption(t("brand_caption"))
    st.caption(f"Build: {APP_VERSION}")
with colB:
    sel = st.radio(t("language"), options=list(LANGS.keys()), format_func=lambda k: LANGS[k], index=0 if lang=="nl" else 1)
    if sel != lang:
        st.session_state.lang = sel
        st.rerun()

# ---------- Beginner’s guide (popup) ----------
with st.popover(t("beginner_open")):
    st.subheader(t("guide_title"))
    st.markdown(t("guide_steps"))

# ---------- Yahoo search helpers ----------
YAHOO_SEARCH_URL = "https://query2.finance.yahoo.com/v1/finance/search"

@st.cache_data(ttl=1800)
def yahoo_search(query: str, quotes_count: int = 15):
    """Zoek wereldwijd naar noteringen; met headers en fallbacks om 403/429 te voorkomen."""
    if not query or len(query.strip()) < 2:
        return []

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://finance.yahoo.com/",
    }
    params = {
        "q": query.strip(),
        "quotesCount": quotes_count,
        "newsCount": 0,
        "lang": "en-US",
        "region": "US",
    }

    # 1) primary
    try:
        r = requests.get(YAHOO_SEARCH_URL, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json() or {}
        keep_types = {"EQUITY"}
        out = []
        for q in (data.get("quotes", []) or []):
            if q.get("quoteType") in keep_types and q.get("symbol"):
                out.append({
                    "symbol": q.get("symbol"),
                    "shortname": q.get("shortname") or q.get("longname") or q.get("name"),
                    "exchange": q.get("exchange") or q.get("exchDisp"),
                    "score": q.get("score", 0.0),
                })
        seen, uniq = set(), []
        for item in sorted(out, key=lambda x: x["score"], reverse=True):
            if item["symbol"] not in seen:
                uniq.append(item); seen.add(item["symbol"])
        return uniq

    except requests.HTTPError:
        # 2) secondary
        try:
            r = requests.get("https://query1.finance.yahoo.com/v1/finance/search",
                             params=params, headers=headers, timeout=10)
            r.raise_for_status()
            data = r.json() or {}
            keep_types = {"EQUITY"}
            out = []
            for q in (data.get("quotes", []) or []):
                if q.get("quoteType") in keep_types and q.get("symbol"):
                    out.append({
                        "symbol": q.get("symbol"),
                        "shortname": q.get("shortname") or q.get("longname") or q.get("name"),
                        "exchange": q.get("exchange") or q.get("exchDisp"),
                        "score": q.get("score", 0.0),
                    })
            seen, uniq = set(), []
            for item in sorted(out, key=lambda x: x["score"], reverse=True):
                if item["symbol"] not in seen:
                    uniq.append(item); seen.add(item["symbol"])
            return uniq
        except Exception:
            # 3) tertiary
            try:
                r = requests.get("https://autoc.finance.yahoo.com/autoc",
                                 params={"query": query.strip(), "region": 1, "lang": "en"},
                                 headers=headers, timeout=10)
                r.raise_for_status()
                js = r.json() or {}
                out = []
                for it in (js.get("ResultSet", {}).get("Result", []) or []):
                    typ = (it.get("typeDisp") or "").lower()
                    if typ in {"equity", "etf"} and it.get("symbol"):
                        out.append({
                            "symbol": it.get("symbol"),
                            "shortname": it.get("name") or it.get("symbol"),
                            "exchange": it.get("exchDisp") or it.get("exch") or "",
                            "score": 0,
                        })
                seen, uniq = set(), []
                for item in out:
                    if item["symbol"] not in seen:
                        uniq.append(item); seen.add(item["symbol"])
                return uniq
            except Exception:
                return []
    except Exception:
        return []

@st.cache_data(ttl=3600)
def fetch_symbol_metadata(symbol: str):
    """Kerninfo + balansitems via yfinance, met defensieve afhandeling."""
    tk = yf.Ticker(symbol)
    try:
        info = tk.info or {}
    except Exception:
        info = {}
    fast = getattr(tk, "fast_info", {}) or {}
    hist_ok = False
    try:
        hist = tk.history(period="1mo")
        hist_ok = len(hist) > 0
    except Exception:
        pass
    total_debt = total_assets = None
    try:
        bs = tk.balance_sheet
        if isinstance(bs, pd.DataFrame) and not bs.empty:
            if "Total Debt" in bs.index:
                total_debt = pd.to_numeric(bs.loc["Total Debt"].dropna().iloc[0], errors="coerce")
            if "Total Assets" in bs.index:
                total_assets = pd.to_numeric(bs.loc["Total Assets"].dropna().iloc[0], errors="coerce")
    except Exception:
        pass
    return {
        "symbol": symbol,
        "name": info.get("longName") or info.get("shortName"),
        "exchange": info.get("exchange") or fast.get("exchange"),
        "currency": info.get("currency") or fast.get("currency"),
        "country": info.get("country"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "marketCap": info.get("marketCap"),
        "totalDebt": None if pd.isna(total_debt) else total_debt,
        "totalAssets": None if pd.isna(total_assets) else total_assets,
        "is_valid": bool(info) or hist_ok
    }

def compute_debt_ratio(meta: dict):
    debt = meta.get("totalDebt"); mc = meta.get("marketCap"); assets = meta.get("totalAssets")
    if debt is None:
        return None, t("debt_unknown")
    if mc:
        return float(debt)/float(mc), t("debt_basis_mc")
    if assets:
        return float(debt)/float(assets), t("debt_basis_assets")
    return None, t("debt_unknown")

# ---------- Halal regels ----------
HARAM_SECTORS = {
    "Alcohol","Gambling","Pork","Conventional Banking","Insurance",
    "Adult Entertainment","Weapons","Tobacco"
}
# brede trefwoorden (naam, sector, industry) — let op: 'lending' (niet 'blending')
_HARAM_PAT = re.compile(
    r"(alcohol|brew|beer|wine|casino|gambl|pork|adult|porn|weapon|tobacco|cig|cannabis|marijuana|"
    r"\bbank(s|ing)?\b|\binsur(ance|er|ers)?\b|\breinsurance\b|\bmortgage\b|\bcredit\b|\blending\b|\blending\b|\blending\b|\blending\b|\blending\b|\blending\b)",
    re.IGNORECASE
)
# Oeps: hierboven te veel; vervang door exacte 1x 'lending':
_HARAM_PAT = re.compile(
    r"(alcohol|brew|beer|wine|casino|gambl|pork|adult|porn|weapon|tobacco|cig|cannabis|marijuana|"
    r"\bbank(s|ing)?\b|\binsur(ance|er|ers)?\b|\breinsurance\b|\bmortgage\b|\bcredit\b|\blending\b|\breit\b|\bcapital markets\b|\bconsumer finance\b|\bloans?\b)",
    re.IGNORECASE
)

def is_haram_activity(name: Optional[str], sector: Optional[str], industry: Optional[str]) -> Optional[str]:
    if sector in HARAM_SECTORS:
        return f"Excluded sector: {sector}"
    text = " ".join([str(name or ""), str(sector or ""), str(industry or "")]).lower()
    # uitzondering: islamic + bank/insurance → niet automatisch haram
    if "islamic" in text and ("bank" in text or "insur" in text):
        return None
    m = _HARAM_PAT.search(text)
    if m:
        return f"Conventional finance/haram activity detected ({m.group(0)})"
    return None

def classify_equity(meta: dict) -> Tuple[str, List[str]]:
    bad = is_haram_activity(meta.get("name"), meta.get("sector"), meta.get("industry"))
    if bad:
        return "not_halal", [bad]
    ratio, basis = compute_debt_ratio(meta)
    if ratio is None:
        return "unclassified", ["Insufficient data to compute debt ratio."]
    pct = ratio * 100.0
    if pct == 0:
        return "halal_full", ["No interest-bearing debt."]
    if pct <= 30:
        return "halal", [f"Debt ratio {pct:.2f}% (≤ 30%, {basis})."]
    if 30 < pct <= 33:
        return "doubt", [f"Debt ratio {pct:.2f}% (30–33%, {basis})."]
    return "not_halal", [f"Debt ratio {pct:.2f}% (> 33%, {basis})."]

def classify_etf(is_certified: bool, halal_pct: int, pur_pct: int) -> Tuple[str, List[str]]:
    if is_certified:
        return "halal", ["Externally Shariah-certified."]
    if halal_pct >= 95 and pur_pct < 5:
        return "halal", [f"Holdings ≈ {halal_pct}% halal. Purification {pur_pct}%."]
    if halal_pct == 0 and pur_pct == 0:
        return "unclassified", ["Insufficient info about holdings; cannot assess."]
    return "doubt", [f"Holdings {halal_pct}%, purification {pur_pct}% (needs review)."]

def classify_crypto(violates_use: bool, fixed_yield: bool, staking_service: bool, interest_like: bool) -> Tuple[str, List[str]]:
    if violates_use:
        return "not_halal", ["Use-case includes prohibited activities (e.g., gambling/interest/adult)."]
    if fixed_yield:
        return "not_halal", ["Fixed/guaranteed yield resembles riba (interest)."]
    if staking_service and not interest_like:
        return "halal", ["Staking rewards based on service/fees (not interest)."]
    return "unclassified", ["Insufficient structure/info → needs scholar review."]

LABELS = {
    "nl": {"halal_full":"✅ Volledig halal","halal":"✅ Halal","doubt":"⚠️ Twijfelachtig","not_halal":"❌ Niet halal","unclassified":"❓ Ongeclassificeerd"},
    "en": {"halal_full":"✅ Fully halal","halal":"✅ Halal","doubt":"⚠️ Doubtful","not_halal":"❌ Not halal","unclassified":"❓ Unclassified"},
}
def label(status: str) -> str:
    return LABELS.get(lang, LABELS["nl"]).get(status, status)

# ---------- Analytics helpers ----------
def get_session_id() -> str:
    if "cid" not in st.session_state:
        st.session_state.cid = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:16]
    return st.session_state.cid

def track_event_ga(event_name: str, params: dict):
    try:
        mid = st.secrets["ga"]["measurement_id"]
        sec = st.secrets["ga"]["api_secret"]
    except Exception:
        return
    try:
        body = {"client_id": get_session_id(), "events": [{"name": event_name, "params": params}]}
        requests.post(
            f"https://www.google-analytics.com/mp/collect?measurement_id={mid}&api_secret={sec}",
            data=json.dumps(body), timeout=5
        )
    except Exception:
        pass

def log_to_sheet(event: str, extra: dict):
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        sheet_id = st.secrets["logging"]["usage_sheet_id"]
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
        )
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(sheet_id)
        ws = sh.sheet1
        row = [datetime.utcnow().isoformat(), get_session_id(), lang, event, json.dumps(extra, ensure_ascii=False)]
        ws.append_row(row, value_input_option="USER_ENTERED")
    except Exception:
        pass

# page view
track_event_ga("page_view", {"page": "home", "build": APP_VERSION})
log_to_sheet("page_view", {"page": "home", "build": APP_VERSION})

# ---------- Tabs ----------
tab1, tab2, tab3, tab4 = st.tabs([T[lang]["tabs_equity"], T[lang]["tabs_etf"], T[lang]["tabs_crypto"], T[lang]["tabs_analytics"]])

# ====== EQUITY TAB ======
with tab1:
    query = st.text_input(T[lang]["search_ph"])
    if query:
        with st.spinner("Zoeken / Searching…"):
            try:
                results = yahoo_search(query)
            except Exception:
                st.warning("Zoekservice tijdelijk niet beschikbaar; probeer later opnieuw.")
                results = []
        if not results:
            st.error(T[lang]["no_results"])
        else:
            options = {f"{r['symbol']} — {r['shortname']} ({r['exchange']})": r for r in results}
            choice = st.selectbox(T[lang]["choose_listing"], list(options.keys()))
            chosen = options[choice]
            meta = fetch_symbol_metadata(chosen["symbol"])
            if not meta["is_valid"]:
                st.error("Listing kon niet gevalideerd worden / could not be validated.")
            else:
                st.success(T[lang]["valid_listing"])
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**{T[lang]['field_name']}:** {meta.get('name') or chosen['shortname']}")
                    st.markdown(f"**{T[lang]['field_ticker']}:** {meta['symbol']}")
                    st.markdown(f"**{T[lang]['field_exchange']}:** {meta.get('exchange') or chosen['exchange']}")
                    st.markdown(f"**{T[lang]['field_currency']}:** {meta.get('currency') or '-'}")
                with col2:
                    st.markdown(f"**{T[lang]['field_country']}:** {meta.get('country') or '-'}")
                    st.markdown(f"**{T[lang]['field_sector']}:** {meta.get('sector') or '-'}")
                    st.markdown(f"**{T[lang]['field_industry']}:** {meta.get('industry') or '-'}")
                    mc = meta.get("marketCap")
                    st.markdown(f"**{T[lang]['field_mcap']}:** {f'{mc:,.0f}' if mc else '-'}")
                ratio, basis = compute_debt_ratio(meta)
                if ratio is None:
                    st.info(f"{T[lang]['field_debt_ratio']}: {T[lang]['debt_unknown']}")
                else:
                    st.markdown(f"**{T[lang]['field_debt_ratio']}:** {ratio:.2%} ({basis})")
                if st.button(T[lang]["check_equity"]):
                    status, reasons = classify_equity(meta)
                    st.markdown(f"### {T[lang]['result']}: {label(status)}")
                    for r in reasons:
                        st.write("•", r)
                    st.markdown(f"**{T[lang]['equity_rules_title']}:**")
                    st.markdown(T[lang]["equity_rules"])
                    track_event_ga("check_equity", {"symbol": meta["symbol"], "status": status})
                    log_to_sheet("check_equity", {"symbol": meta["symbol"], "status": status})

# ====== ETF TAB ======
with tab2:
    name_etf = st.text_input(T[lang]["etf_name"])
    sharia_certified = st.checkbox(T[lang]["etf_cert"], value=False)
    halal_pct = st.slider(T[lang]["etf_halal_pct"], 0, 100, 100)
    purification_pct = st.slider(T[lang]["etf_pur_pct"], 0, 20, 0)
    if st.button(T[lang]["check_etf"]):
        status, reasons = classify_etf(sharia_certified, halal_pct, purification_pct)
        st.markdown(f"### {T[lang]['result']}: {label(status)}")
        for r in reasons:
            st.write("•", r)
        track_event_ga("check_etf", {"name": name_etf or "-", "status": status})
        log_to_sheet("check_etf", {"name": name_etf or "-", "status": status})

# ====== CRYPTO TAB ======
with tab3:
    name_crypto = st.text_input(T[lang]["crypto_name"])
    violates_usecase = st.checkbox(T[lang]["crypto_haram_use"], value=False)
    fixed_yield = st.checkbox(T[lang]["crypto_fixed_yield"], value=False)
    staking_service = st.checkbox(T[lang]["crypto_staking_service"], value=False)
    interest_like = st.checkbox(T[lang]["crypto_interest_like"], value=False)
    if st.button(T[lang]["check_crypto"]):
        status, reasons = classify_crypto(violates_usecase, fixed_yield, staking_service, interest_like)
        st.markdown(f"### {T[lang]['result']}: {label(status)}")
        for r in reasons:
            st.write("•", r)
        track_event_ga("check_crypto", {"name": name_crypto or "-", "status": status})
        log_to_sheet("check_crypto", {"name": name_crypto or "-", "status": status})

# ====== ANALYTICS TAB ======
with tab4:
    pin = st.text_input(T[lang]["admin_pin"], type="password")
    if pin and "admin" in st.secrets and pin == st.secrets["admin"]["pin"]:
        st.success(T[lang]["show_stats"])
        try:
            import gspread
            from google.oauth2.service_account import Credentials
            sheet_id = st.secrets["logging"]["usage_sheet_id"]
            creds = Credentials.from_service_account_info(
                st.secrets["gcp_service_account"],
                scopes=['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
            )
            gc = gspread.authorize(creds)
            sh = gc.open_by_key(sheet_id)
            ws = sh.sheet1
            rows = ws.get_all_records()
            df = pd.DataFrame(rows)
            st.write("Totaal events:", len(df))
            if "event" in df.columns and not df["event"].empty:
                st.bar_chart(df["event"].value_counts())
            if "extra" in df.columns:
                try:
                    extra_df = pd.json_normalize(df["extra"].apply(lambda x: json.loads(x) if x else {}))
                    st.write("Voorbeeld van extra gegevens:", extra_df.head(10))
                except Exception:
                    pass
        except Exception:
            st.info(T[lang]["stats_tip"])
    else:
        st.info(T[lang]["stats_tip"])

# ---------- Footer ----------
st.markdown("---")
st.caption(T[lang]["footer"])

st.caption(t("footer"))



