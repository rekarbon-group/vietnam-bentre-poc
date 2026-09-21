#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REKARBON × BẾN TRE / MEKONG — VIETNAM AGRI-BIOMASS POC
3 POCs in 1: Coconut • Rice • Cashew
Languages: Français • English • Tiếng Việt

Status: POC / demonstrator. Public data and regulatory references are separated
from user-adjustable technical/economic assumptions. Nothing in this app is a
credit issuance guarantee, a legal opinion, or an investment recommendation.

Geographic note (2026): the former Bến Tre Province was merged in 2025 into the
new Vĩnh Long Province. "Bến Tre" is retained here as a geographic/agricultural
identity for the coconut cluster and demonstration area.
"""

from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# =============================================================================
# PAGE CONFIG
# =============================================================================

st.set_page_config(
    page_title="Bến Tre / Mekong × Rekarbon | 3-Feedstock MRV POC",
    page_icon="🌴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# DESIGN
# =============================================================================

st.markdown(
    """
<style>
:root {
    --vn-red:#DA251D;
    --vn-gold:#FFCD00;
    --coconut:#16865A;
    --rice:#82A928;
    --cashew:#B66B2E;
    --mekong:#087EA4;
    --ink:#17212B;
    --muted:#65727E;
    --paper:#F5F8F6;
    --success:#00A878;
}
html, body, [class*="css"] {font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;}
.stApp {background:linear-gradient(180deg,#F8FBF8 0%,#EEF5F2 100%);}
#MainMenu {visibility:hidden;} footer {visibility:hidden;} .stDeployButton {display:none;}
.hero {background:radial-gradient(circle at 88% 15%,rgba(255,205,0,.22),transparent 25%),linear-gradient(135deg,#8D160F 0%,#DA251D 35%,#087EA4 100%);padding:2.3rem 2.6rem;border-radius:22px;color:white;margin-bottom:1.25rem;box-shadow:0 18px 55px rgba(60,40,30,.18);}
.hero h1 {margin:0;font-size:2.35rem;line-height:1.08;font-weight:900;}
.hero .sub {margin-top:.7rem;font-size:1.02rem;opacity:.94;max-width:1100px;}
.hero .tag {display:inline-block;margin-top:.9rem;padding:.38rem .75rem;background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.28);border-radius:999px;font-size:.78rem;font-weight:750;}
.panel,.metric-card,.feed-card {background:white;border-radius:16px;box-shadow:0 8px 28px rgba(15,35,50,.07);border:1px solid rgba(8,126,164,.08);}
.panel {padding:1.25rem 1.45rem;margin:.45rem 0 1rem 0;}
.metric-card {padding:1.15rem 1.25rem;border-left:5px solid var(--vn-red);min-height:132px;}
.metric-card.green {border-left-color:var(--coconut)} .metric-card.rice {border-left-color:var(--rice)} .metric-card.cashew {border-left-color:var(--cashew)} .metric-card.blue {border-left-color:var(--mekong)} .metric-card.gold {border-left-color:var(--vn-gold)}
.metric-label {font-size:.75rem;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);font-weight:800;}
.metric-value {margin-top:.25rem;font-size:1.9rem;font-weight:900;color:var(--ink);line-height:1.05;}
.metric-note {margin-top:.45rem;color:var(--muted);font-size:.79rem;line-height:1.35;}
.feed-grid {display:grid;grid-template-columns:repeat(auto-fit,minmax(245px,1fr));gap:1rem;margin:.8rem 0 1.2rem;}
.feed-card {padding:1.35rem 1.4rem;min-height:215px;}
.feed-card h3 {margin:.25rem 0 .5rem;}
.coconut {border-top:5px solid var(--coconut)} .rice {border-top:5px solid var(--rice)} .cashew {border-top:5px solid var(--cashew)}
.pill {display:inline-flex;align-items:center;gap:.3rem;padding:.38rem .72rem;border-radius:999px;font-size:.76rem;font-weight:800;margin:.14rem;}
.pill.green {background:rgba(22,134,90,.12);color:#0D6845}.pill.blue {background:rgba(8,126,164,.12);color:#075D78}.pill.gold {background:rgba(255,205,0,.18);color:#765D00}.pill.orange {background:rgba(182,107,46,.13);color:#824618}.pill.red {background:rgba(218,37,29,.10);color:#9B1B15}
.official {background:rgba(8,126,164,.07);border-left:4px solid var(--mekong);padding:.95rem 1.05rem;border-radius:10px;margin:.7rem 0;font-size:.88rem;}
.scenario {background:rgba(255,205,0,.12);border-left:4px solid #D7A900;padding:.95rem 1.05rem;border-radius:10px;margin:.7rem 0;font-size:.88rem;}
.risk {background:rgba(218,37,29,.065);border-left:4px solid var(--vn-red);padding:.95rem 1.05rem;border-radius:10px;margin:.7rem 0;font-size:.88rem;}
.success {background:rgba(0,168,120,.08);border-left:4px solid var(--success);padding:.95rem 1.05rem;border-radius:10px;margin:.7rem 0;font-size:.88rem;}
.arch-grid {display:grid;grid-template-columns:repeat(auto-fit,minmax(215px,1fr));gap:1rem;margin:1rem 0;}
.arch {border-radius:15px;padding:1.2rem;color:white;min-height:150px;box-shadow:0 8px 25px rgba(0,0,0,.12)}
.sidebar-brand{text-align:center;padding:1rem .5rem .7rem}.sidebar-brand .city{font-size:1.15rem;font-weight:950;color:#DA251D;letter-spacing:.05em}.sidebar-brand .rk{font-size:.73rem;color:#65727E;font-weight:750;margin-top:.2rem}
small.source {color:#65727E;line-height:1.35;}
</style>
""",
    unsafe_allow_html=True,
)

# =============================================================================
# LANGUAGE
# =============================================================================

LANGS = {"fr": "Français", "en": "English", "vi": "Tiếng Việt"}
if "lang" not in st.session_state:
    st.session_state.lang = "fr"


def tr(fr: str, en: str, vi: str) -> str:
    return {"fr": fr, "en": en, "vi": vi}[st.session_state.lang]


def fmt_int(v: float | int) -> str:
    sep = " " if st.session_state.lang == "fr" else ","
    s = f"{int(round(v)):,}"
    return s.replace(",", sep)


def fmt_dec(v: float, nd: int = 1) -> str:
    s = f"{v:.{nd}f}"
    return s.replace(".", ",") if st.session_state.lang == "fr" else s


def fmt_money(v: float, currency: str = "€") -> str:
    return f"{currency}{fmt_int(v)}" if currency == "$" else f"{fmt_int(v)} {currency}"

# =============================================================================
# PUBLIC / PUBLISHED DATA
# =============================================================================

DATA = {
    "bentre_coconut_area_2024_ha": 80_000,
    "bentre_coconut_fruits_2024": 708_000_000,
    "bentre_coconut_share_vietnam_pct": 42,
    "bentre_coconut_share_mekong_pct": 88,
    "bentre_coconut_organic_2024_ha": 20_400,
    "bentre_coconut_certified_2024_ha": 13_000,
    "vietnam_coconut_area_2025_ha": 200_000,
    "vietnam_coconut_output_tyr": 2_260_000,
    "vietnam_coconut_factories": 145,
    "vietnam_rice_2025_t": 43_540_000,
    "mekong_rice_share_vietnam_pct": 50,
    "mekong_rice_export_share_pct": 90,
    "vietnam_rice_residue_straw_husk_tyr": 52_000_000,
    "mekong_straw_burned_pct": 70,
    "cashew_raw_import_2025_t": 3_120_000,
    "cashew_kernel_export_2025_t": 766_585,
    "cashew_export_2025_usd": 5_220_000_000,
}

SOURCES = {
    "admin": "https://en.baochinhphu.vn/names-and-administrative-centers-of-34-provinces-and-centrally-run-cities-specified-111250415094350491.htm",
    "coconut_bentre": "https://moit.gov.vn/tin-tuc/xuc-tien-thuong-mai/ket-noi-giao-thuong-xuc-tien-thuong-mai-san-pham-dua-ben-tre.html",
    "coconut_vn": "https://en.mae.gov.vn/Pages/chi-tiet-tin-Eng.aspx?ItemID=9146",
    "rice_2025": "https://www.nso.gov.vn/en/data-and-statistics/2026/01/press-release-social-economic-situation-in-the-fourth-quarter-and-2025/",
    "rice_mekong": "https://en.mae.gov.vn/Pages/chi-tiet-tin-Eng.aspx?ItemID=8801",
    "rice_residue": "https://www.undp.org/vietnam/speeches/high-level-policy-dialogue-promoting-multi-stakeholder-collaboration-circular-agriculture",
    "cashew_2025": "https://en.vietnordic.com/2026/05/cashew-industry-under-pressure-to-move-up-value-chain/",
    "vn_decree_119": "https://chinhphu.vn/?classid=1&docid=213875&pageid=27160",
    "vn_decision_232": "https://en.mae.gov.vn/Pages/chi-tiet-tin-Eng.aspx?ItemID=8745",
    "vn_decree_29": "https://chinhphu.vn/?classid=1&docid=216694&pageid=27160&typegroupid=4",
    "vn_exchange": "https://en.baochinhphu.vn/viet-nam-pilots-domestic-carbon-trading-exchange-111260121104218671.htm",
    "verra": "https://verra.org/methodologies/vm0044-biochar-utilization-in-soil-and-non-soil-applications-v1-2/",
    "puro": "https://puro.earth/cdr-infrastructure/methodologies/document-library/",
}

# =============================================================================
# POC ASSUMPTIONS — NOT OFFICIAL DATA
# =============================================================================

FEEDSTOCKS = {
    "coconut": {
        "emoji": "🥥",
        "name": {"fr": "Noix de coco", "en": "Coconut", "vi": "Dừa"},
        "scope": {"fr": "Bến Tre / Vĩnh Long", "en": "Bến Tre / Vĩnh Long", "vi": "Bến Tre / Vĩnh Long"},
        "default_feed_t": 10_000,
        "default_yield": 30,
        "default_cdr": 1.9,
        "color": "#16865A",
    },
    "rice": {
        "emoji": "🌾",
        "name": {"fr": "Riz", "en": "Rice", "vi": "Lúa gạo"},
        "scope": {"fr": "Delta du Mékong", "en": "Mekong Delta", "vi": "Đồng bằng sông Cửu Long"},
        "default_feed_t": 10_000,
        "default_yield": 28,
        "default_cdr": 1.8,
        "color": "#82A928",
    },
    "cashew": {
        "emoji": "🥜",
        "name": {"fr": "Noix de cajou", "en": "Cashew", "vi": "Hạt điều"},
        "scope": {"fr": "Corridor industriel Sud Vietnam", "en": "Southern Vietnam processing corridor", "vi": "Hành lang chế biến miền Nam Việt Nam"},
        "default_feed_t": 10_000,
        "default_yield": 28,
        "default_cdr": 1.9,
        "color": "#B66B2E",
    },
}

POC_DEFAULTS = {
    "eligible_share_pct": 25,
    "cdr_price_eur_t": 250,
    "biochar_value_eur_t": 200,
    "usable_heat_mwh_per_t_feedstock": 0.8,
    "heat_value_eur_mwh": 35,
    "pilot_capex_eur": 600_000,
    "annual_opex_eur": 180_000,
}

# =============================================================================
# HELPERS
# =============================================================================


def hero(title: str, subtitle: str, tag: str):
    st.markdown(
        f'<div class="hero"><h1>{title}</h1><div class="sub">{subtitle}</div><div class="tag">{tag}</div></div>',
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, note: str = "", cls: str = ""):
    st.markdown(
        f'<div class="metric-card {cls}"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>',
        unsafe_allow_html=True,
    )


def official_note(text: str):
    st.markdown(f'<div class="official"><b>{tr("Base publiée", "Published basis", "Cơ sở dữ liệu công bố")}:</b> {text}</div>', unsafe_allow_html=True)


def scenario_note(text: str):
    st.markdown(f'<div class="scenario"><b>{tr("Hypothèse POC", "POC assumption", "Giả định POC")}:</b> {text}</div>', unsafe_allow_html=True)


def risk_note(text: str):
    st.markdown(f'<div class="risk"><b>{tr("Point de vigilance", "Risk / gate", "Điểm cần kiểm soát")}:</b> {text}</div>', unsafe_allow_html=True)


def success_note(text: str):
    st.markdown(f'<div class="success"><b>{tr("Objectif", "Objective", "Mục tiêu")}:</b> {text}</div>', unsafe_allow_html=True)


def calc_scenario(feedstock_t: float, share_pct: float, yield_pct: float, cdr_factor: float,
                  cdr_price: float, biochar_value: float, heat_mwh_t: float, heat_value: float):
    feed = feedstock_t * share_pct / 100.0
    biochar = feed * yield_pct / 100.0
    cdr = biochar * cdr_factor
    cdr_value = cdr * cdr_price
    biochar_product_value = biochar * biochar_value
    heat = feed * heat_mwh_t
    heat_value_total = heat * heat_value
    return {
        "feed": feed,
        "biochar": biochar,
        "cdr": cdr,
        "cdr_value": cdr_value,
        "biochar_value": biochar_product_value,
        "heat": heat,
        "heat_value": heat_value_total,
        "gross": cdr_value + biochar_product_value + heat_value_total,
    }


def demo_hash(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()

# =============================================================================
# SESSION
# =============================================================================

PAGE_IDS = ["dashboard", "coconut", "rice", "cashew", "live", "pilot", "business", "mrv", "compliance", "sources"]
PAGE_LABELS = {
    "dashboard": ("🏠 Vue d'ensemble", "🏠 Overview", "🏠 Tổng quan"),
    "coconut": ("🥥 POC Coco", "🥥 Coconut POC", "🥥 POC Dừa"),
    "rice": ("🌾 POC Riz", "🌾 Rice POC", "🌾 POC Lúa gạo"),
    "cashew": ("🥜 POC Cajou", "🥜 Cashew POC", "🥜 POC Hạt điều"),
    "live": ("📡 MRV Démo", "📡 MRV Demo", "📡 MRV Demo"),
    "pilot": ("🧪 POC 6 mois", "🧪 6-month POC", "🧪 POC 6 tháng"),
    "business": ("📊 Business Case", "📊 Business Case", "📊 Hiệu quả kinh tế"),
    "mrv": ("🔐 Architecture MRV", "🔐 MRV Architecture", "🔐 Kiến trúc MRV"),
    "compliance": ("📋 Carbone & conformité", "📋 Carbon & compliance", "📋 Carbon & tuân thủ"),
    "sources": ("📚 Données & sources", "📚 Data & sources", "📚 Dữ liệu & nguồn"),
}

if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "demo_tick" not in st.session_state:
    st.session_state.demo_tick = 0

# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
          <div style="font-size:2.25rem">🇻🇳🌴</div>
          <div class="city">BẾN TRE / MEKONG</div>
          <div class="rk">× REKARBON • AGRI-BIOMASS MRV</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    lang_choice = st.radio(
        tr("Langue", "Language", "Ngôn ngữ"),
        options=list(LANGS.keys()),
        format_func=lambda k: LANGS[k],
        index=list(LANGS.keys()).index(st.session_state.lang),
        horizontal=True,
        key="lang_radio",
    )
    if lang_choice != st.session_state.lang:
        st.session_state.lang = lang_choice
        st.rerun()

    st.caption(tr(
        "3 filières • Biochar • CDR • MRV • Économie circulaire",
        "3 feedstocks • Biochar • CDR • MRV • Circular economy",
        "3 nguồn nguyên liệu • Biochar • CDR • MRV • Kinh tế tuần hoàn",
    ))
    st.markdown("---")
    for pid in PAGE_IDS:
        label = tr(*PAGE_LABELS[pid])
        if st.button(label, key=f"nav_{pid}", use_container_width=True,
                     type="primary" if st.session_state.page == pid else "secondary"):
            st.session_state.page = pid
            st.rerun()
    st.markdown("---")
    st.markdown(
        f"""
        <div style="font-size:.80rem;color:#5B6770;line-height:1.55">
          <strong>{tr('Zone', 'Area', 'Khu vực')}:</strong> Bến Tre / Mekong<br>
          <strong>{tr('Statut administratif', 'Administrative status', 'Tình trạng hành chính')}:</strong> Vĩnh Long Province (2026)<br>
          <strong>MRV:</strong> Edge + signed proof pack<br>
          <strong>{tr('Statut', 'Status', 'Trạng thái')}:</strong> <span style="color:#00A878;font-weight:850">POC READY</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

PAGE = st.session_state.page

# =============================================================================
# DASHBOARD
# =============================================================================

if PAGE == "dashboard":
    hero(
        tr("🇻🇳 BẾN TRE / MEKONG × REKARBON", "🇻🇳 BẾN TRE / MEKONG × REKARBON", "🇻🇳 BẾN TRE / MEKONG × REKARBON"),
        tr(
            "Un démonstrateur, trois filières agricoles : coco local à Bến Tre, résidus du riz dans le delta du Mékong et coques de cajou issues du corridor industriel du Sud Vietnam.",
            "One demonstrator, three agricultural value chains: local coconut in Bến Tre, rice residues across the Mekong Delta, and cashew shells from Southern Vietnam's processing corridor.",
            "Một mô hình trình diễn, ba chuỗi giá trị nông nghiệp: dừa tại Bến Tre, phụ phẩm lúa gạo ở Đồng bằng sông Cửu Long và vỏ hạt điều từ hành lang chế biến miền Nam Việt Nam.",
        ),
        tr("3 POC EN 1 • DONNÉES + MRV + CARBONE", "3 POCs IN 1 • DATA + MRV + CARBON", "3 POC TRONG 1 • DỮ LIỆU + MRV + CARBON"),
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card(tr("Cocotiers Bến Tre 2024", "Bến Tre coconut area 2024", "Diện tích dừa Bến Tre 2024"),
                    f"{fmt_int(DATA['bentre_coconut_area_2024_ha'])} ha",
                    tr("≈42 % de la surface nationale publiée", "≈42% of published national area", "≈42% diện tích dừa cả nước theo số liệu công bố"), "green")
    with c2:
        metric_card(tr("Production coco Bến Tre", "Bến Tre coconut output", "Sản lượng dừa Bến Tre"),
                    f"{fmt_int(DATA['bentre_coconut_fruits_2024']/1_000_000)} M",
                    tr("fruits en 2024", "fruits in 2024", "trái năm 2024"), "green")
    with c3:
        metric_card(tr("Riz Vietnam 2025", "Vietnam rice 2025", "Lúa Việt Nam 2025"),
                    f"{DATA['vietnam_rice_2025_t']/1_000_000:.2f} Mt",
                    tr("production nationale publiée", "published national production", "sản lượng quốc gia công bố"), "rice")
    with c4:
        metric_card(tr("Cajou brut importé 2025", "Raw cashew imported 2025", "Điều thô nhập khẩu 2025"),
                    f"{DATA['cashew_raw_import_2025_t']/1_000_000:.2f} Mt",
                    tr("échelle de la transformation vietnamienne", "scale of Vietnamese processing", "quy mô ngành chế biến Việt Nam"), "cashew")

    st.markdown("### " + tr("Pourquoi trois filières ?", "Why three value chains?", "Vì sao chọn ba chuỗi giá trị?"))
    st.markdown(
        f"""
        <div class="feed-grid">
          <div class="feed-card coconut"><div style="font-size:2rem">🥥</div><h3>{tr('Coco — Bến Tre','Coconut — Bến Tre','Dừa — Bến Tre')}</h3>
          <p>{tr('Gisement identitaire et local : bourres, fibres et coques issues de la transformation. Le POC doit mesurer la quantité réellement disponible, son humidité et les usages existants.','A local flagship feedstock: husks, fibre and shells from processing. The POC must measure genuinely available volume, moisture and existing uses.','Nguồn nguyên liệu đặc trưng địa phương: xơ, vỏ dừa từ chế biến. POC phải đo khối lượng thực sự sẵn có, độ ẩm và các mục đích sử dụng hiện tại.')}</p>
          <span class="pill green">Bến Tre</span><span class="pill blue">Circular economy</span></div>
          <div class="feed-card rice"><div style="font-size:2rem">🌾</div><h3>{tr('Riz — Mékong','Rice — Mekong','Lúa gạo — Mekong')}</h3>
          <p>{tr('Flux massif et saisonnier. Priorité POC aux balles et aux pailles collectables, avec preuve de leur devenir de référence pour éviter le double comptage.','Large, seasonal flow. POC priority is collectable husk and straw, with evidence of baseline fate to prevent double counting.','Dòng phụ phẩm lớn và theo mùa. Ưu tiên POC cho trấu và rơm có thể thu gom, đồng thời chứng minh kịch bản cơ sở để tránh tính trùng.')}</p>
          <span class="pill green">Mekong Delta</span><span class="pill gold">Low-carbon rice</span></div>
          <div class="feed-card cashew"><div style="font-size:2rem">🥜</div><h3>{tr('Cajou — Sud Vietnam','Cashew — Southern Vietnam','Hạt điều — Miền Nam Việt Nam')}</h3>
          <p>{tr('Le Vietnam est une plateforme mondiale de transformation. Les coques peuvent être concentrées sur site, mais elles ont déjà des usages : leur statut de “déchet” ne doit jamais être présumé.','Vietnam is a global processing hub. Shells can be concentrated at processing sites, but already have uses: “waste” status must never be assumed.','Việt Nam là trung tâm chế biến điều lớn của thế giới. Vỏ điều tập trung tại nhà máy nhưng đã có các mục đích sử dụng khác, vì vậy không được mặc định là “chất thải”.')}</p>
          <span class="pill orange">Processing hubs</span><span class="pill red">Additionality gate</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    official_note(tr(
        "Les chiffres en tête de page sont des données publiées. Les tonnes de résidus réellement mobilisables pour REKARBON ne sont pas encore connues : elles doivent être mesurées auprès des transformateurs, rizeries, coopératives et opérateurs locaux.",
        "Headline figures are published data. The tonnes of residues genuinely available to REKARBON are not yet known and must be measured with processors, rice mills, cooperatives and local operators.",
        "Các số liệu chính là dữ liệu đã công bố. Khối lượng phụ phẩm thực sự có thể huy động cho REKARBON hiện chưa được xác định và phải được đo đếm cùng các nhà chế biến, nhà máy xay xát, hợp tác xã và đơn vị địa phương.",
    ))
    risk_note(tr(
        "Bến Tre n'est plus une province autonome depuis la réorganisation de 2025 : le territoire historique appartient désormais à la nouvelle province de Vĩnh Long. Le nom Bến Tre est conservé ici comme identité géographique/agricole du POC.",
        "Bến Tre is no longer a standalone province after the 2025 reorganisation; the historic territory now belongs to the new Vĩnh Long Province. Bến Tre is retained here as the geographic/agricultural identity of the POC.",
        "Sau sắp xếp hành chính năm 2025, Bến Tre không còn là một tỉnh độc lập; khu vực lịch sử này hiện thuộc tỉnh Vĩnh Long mới. Tên Bến Tre vẫn được sử dụng trong POC như một định danh địa lý/nông nghiệp.",
    ))

# =============================================================================
# FEEDSTOCK PAGES
# =============================================================================

elif PAGE == "coconut":
    hero("🥥 " + tr("POC COCO — BẾN TRE", "COCONUT POC — BẾN TRE", "POC DỪA — BẾN TRE"),
         tr("Transformer un coproduit agricole emblématique en biochar traçable et en retrait carbone mesurable.",
            "Turn an iconic agricultural co-product into traceable biochar and measurable carbon removal.",
            "Chuyển phụ phẩm nông nghiệp đặc trưng thành biochar có thể truy xuất và lượng loại bỏ carbon có thể đo lường."),
         tr("LOCAL • CIRCULAIRE • TRAÇABLE", "LOCAL • CIRCULAR • TRACEABLE", "ĐỊA PHƯƠNG • TUẦN HOÀN • TRUY XUẤT"))
    c1,c2,c3,c4=st.columns(4)
    with c1: metric_card(tr("Surface 2024","Area 2024","Diện tích 2024"),f"{fmt_int(DATA['bentre_coconut_area_2024_ha'])} ha","Bến Tre","green")
    with c2: metric_card(tr("Production 2024","Output 2024","Sản lượng 2024"),f"{fmt_int(DATA['bentre_coconut_fruits_2024']/1_000_000)} M",tr("fruits","fruits","trái"),"green")
    with c3: metric_card(tr("Bio/organique","Organic area","Diện tích hữu cơ"),f"{fmt_int(DATA['bentre_coconut_organic_2024_ha'])} ha",tr("zone publiée","published area","diện tích công bố"),"green")
    with c4: metric_card(tr("Part Mékong","Mekong share","Tỷ trọng Mekong"),f"{DATA['bentre_coconut_share_mekong_pct']}%",tr("de la surface coco régionale publiée","of published regional coconut area","diện tích dừa khu vực theo số liệu công bố"),"blue")

    st.markdown("### " + tr("Flux à mesurer pendant le POC","Flows to measure during the POC","Dòng vật chất cần đo trong POC"))
    for item in [
        tr("Origine du lot et transformateur","Batch origin and processor","Nguồn gốc lô hàng và đơn vị chế biến"),
        tr("Masse de bourre/fibre/coque réellement disponible","Actually available husk/fibre/shell mass","Khối lượng xơ/vỏ dừa thực sự sẵn có"),
        tr("Humidité, contamination et stockage","Moisture, contamination and storage","Độ ẩm, tạp chất và lưu kho"),
        tr("Usages existants et coût d'opportunité","Existing uses and opportunity cost","Mục đích sử dụng hiện tại và chi phí cơ hội"),
        tr("Biochar produit, carbone organique, H/Corg et destination finale","Biochar output, organic carbon, H/Corg and final fate","Biochar tạo ra, carbon hữu cơ, H/Corg và nơi sử dụng cuối cùng"),
    ]:
        st.markdown(f'<span class="pill green">✓ {item}</span>', unsafe_allow_html=True)
    scenario_note(tr("Aucun tonnage de résidus de coco n'est déduit automatiquement des 708 millions de fruits. Le POC mesure le gisement réellement disponible avant tout dimensionnement.",
                     "No coconut-residue tonnage is automatically inferred from the 708 million fruits. The POC measures genuinely available feedstock before sizing.",
                     "Không tự động suy ra khối lượng phụ phẩm từ 708 triệu trái dừa. POC sẽ đo nguồn nguyên liệu thực sự sẵn có trước khi xác định quy mô."))
    risk_note(tr("Pour le crédit carbone, il faudra démontrer que la biomasse est admissible selon la méthodologie choisie et documenter son usage de référence. Un coproduit déjà valorisé n'est pas automatiquement un 'déchet'.",
                 "For carbon crediting, biomass eligibility under the chosen methodology and its baseline use must be demonstrated. A co-product already used elsewhere is not automatically 'waste'.",
                 "Để tạo tín chỉ carbon, phải chứng minh sinh khối đủ điều kiện theo phương pháp được chọn và xác định cách sử dụng trong kịch bản cơ sở. Phụ phẩm đã được tận dụng không tự động được coi là 'chất thải'."))

elif PAGE == "rice":
    hero("🌾 " + tr("POC RIZ — DELTA DU MÉKONG", "RICE POC — MEKONG DELTA", "POC LÚA GẠO — ĐỒNG BẰNG SÔNG CỬU LONG"),
         tr("Valoriser trấu et paille collectable sans concurrencer les usages agricoles utiles ni doubler un autre projet carbone.",
            "Valorise collectable rice husk and straw without displacing beneficial uses or double counting another carbon project.",
            "Tận dụng trấu và rơm có thể thu gom mà không cạnh tranh với các mục đích nông nghiệp hữu ích hoặc tính trùng với dự án carbon khác."),
         tr("RIZ BAS-CARBONE • RÉSIDUS • MRV", "LOW-CARBON RICE • RESIDUES • MRV", "LÚA PHÁT THẢI THẤP • PHỤ PHẨM • MRV"))
    c1,c2,c3,c4=st.columns(4)
    with c1: metric_card(tr("Vietnam 2025","Vietnam 2025","Việt Nam 2025"),f"{DATA['vietnam_rice_2025_t']/1_000_000:.2f} Mt",tr("riz produit","rice produced","sản lượng lúa"),"rice")
    with c2: metric_card(tr("Part Mékong","Mekong share","Tỷ trọng Mekong"),f"≈{DATA['mekong_rice_share_vietnam_pct']}%",tr("de la production nationale","of national output","sản lượng quốc gia"),"rice")
    with c3: metric_card(tr("Part des exportations","Export share","Tỷ trọng xuất khẩu"),f"≈{DATA['mekong_rice_export_share_pct']}%",tr("du riz vietnamien selon le MAE","of Vietnamese rice according to MAE","gạo xuất khẩu Việt Nam theo MAE"),"blue")
    with c4: metric_card(tr("Paille + balle (Vietnam)","Straw + husk (Vietnam)","Rơm + trấu (Việt Nam)"),f"≈{DATA['vietnam_rice_residue_straw_husk_tyr']/1_000_000:.0f} Mt/an",tr("estimation UNDP","UNDP estimate","ước tính UNDP"),"gold")

    official_note(tr("Le ministère vietnamien indique qu'environ 70 % de la paille après récolte est encore brûlée et qu'environ 10 % est réutilisée dans le contexte du renforcement de la chaîne de valeur de la paille du riz dans le Mékong.",
                     "Vietnam's ministry reports that about 70% of post-harvest rice straw is still burned and around 10% reused in the context of strengthening the Mekong rice-straw value chain.",
                     "Bộ quản lý của Việt Nam cho biết khoảng 70% rơm sau thu hoạch vẫn bị đốt và khoảng 10% được tái sử dụng trong bối cảnh phát triển chuỗi giá trị rơm ở Đồng bằng sông Cửu Long."))
    st.markdown("### " + tr("Deux routes POC","Two POC routes","Hai hướng POC"))
    st.markdown(f"""
    <div class="arch-grid">
      <div class="arch" style="background:linear-gradient(135deg,#82A928,#4E6E11)"><div style="font-size:2rem">🌾</div><h4>{tr('Balle de riz','Rice husk','Trấu')}</h4><small>{tr('Concentrée aux rizeries • logistique plus simple • mesurer humidité, cendres et usages existants','Concentrated at rice mills • simpler logistics • measure moisture, ash and existing uses','Tập trung tại nhà máy xay xát • logistics đơn giản hơn • đo độ ẩm, tro và mục đích sử dụng hiện tại')}</small></div>
      <div class="arch" style="background:linear-gradient(135deg,#A7B82B,#6E7C13)"><div style="font-size:2rem">🚜</div><h4>{tr('Paille collectable','Collectable straw','Rơm có thể thu gom')}</h4><small>{tr('Flux dispersé et saisonnier • collecte • prétraitement • baseline brûlage/incorporation/réemploi','Dispersed seasonal flow • collection • preprocessing • baseline burning/incorporation/reuse','Dòng phân tán theo mùa • thu gom • tiền xử lý • kịch bản cơ sở đốt/vùi/tái sử dụng')}</small></div>
    </div>""", unsafe_allow_html=True)
    risk_note(tr("Le riz est déjà au cœur de programmes de réduction du méthane et de riz bas-carbone. Un même bénéfice climatique ne peut pas être crédité deux fois. Le MRV doit identifier parcelle, lot, baseline et éventuel programme carbone existant.",
                 "Rice is already covered by methane-reduction and low-carbon rice programs. The same climate benefit cannot be credited twice. MRV must identify field, batch, baseline and any existing carbon program.",
                 "Lúa gạo đã nằm trong các chương trình giảm methane và lúa phát thải thấp. Không được cấp tín chỉ hai lần cho cùng một lợi ích khí hậu. MRV phải xác định ruộng, lô nguyên liệu, kịch bản cơ sở và chương trình carbon hiện có."))

elif PAGE == "cashew":
    hero("🥜 " + tr("POC CAJOU — CORRIDOR INDUSTRIEL DU SUD", "CASHEW POC — SOUTHERN PROCESSING CORRIDOR", "POC HẠT ĐIỀU — HÀNH LANG CHẾ BIẾN MIỀN NAM"),
         tr("Capter un flux concentré de coques de transformation, tout en traitant correctement l'additionalité et les usages existants.",
            "Capture a concentrated processing-shell stream while correctly addressing additionality and existing uses.",
            "Khai thác dòng vỏ điều tập trung tại cơ sở chế biến, đồng thời xử lý đúng yêu cầu về tính bổ sung và các mục đích sử dụng hiện tại."),
         tr("INDUSTRIEL • CONCENTRÉ • ADDITIONALITÉ", "INDUSTRIAL • CONCENTRATED • ADDITIONALITY", "CÔNG NGHIỆP • TẬP TRUNG • TÍNH BỔ SUNG"))
    c1,c2,c3=st.columns(3)
    with c1: metric_card(tr("Import brut 2025","Raw imports 2025","Nhập khẩu điều thô 2025"),f"{DATA['cashew_raw_import_2025_t']/1_000_000:.2f} Mt",tr("noix de cajou brutes","raw cashew nuts","hạt điều thô"),"cashew")
    with c2: metric_card(tr("Export 2025","Exports 2025","Xuất khẩu 2025"),f"{fmt_int(DATA['cashew_kernel_export_2025_t'])} t",tr("amandes de cajou","cashew kernels","nhân điều"),"cashew")
    with c3: metric_card(tr("Valeur export 2025","2025 export value","Giá trị xuất khẩu 2025"),f"${DATA['cashew_export_2025_usd']/1_000_000_000:.2f}B",tr("ordre de grandeur filière","industry scale","quy mô ngành"),"gold")
    official_note(tr("Ces données décrivent la filière nationale de transformation, pas un gisement local de Bến Tre. Le module cajou doit donc être traité comme un corridor d'approvisionnement du Sud Vietnam et rattaché à un transformateur partenaire identifié.",
                     "These figures describe the national processing industry, not a local Bến Tre feedstock pool. The cashew module must therefore be treated as a Southern Vietnam supply corridor anchored to an identified processing partner.",
                     "Các số liệu này phản ánh ngành chế biến cấp quốc gia, không phải nguồn nguyên liệu cục bộ tại Bến Tre. Vì vậy mô-đun hạt điều phải được xem là hành lang cung ứng miền Nam Việt Nam gắn với một đối tác chế biến cụ thể."))
    st.markdown("### " + tr("Ce que le POC doit prouver","What the POC must prove","POC phải chứng minh"))
    for item in [
        tr("Masse de coques générée par site et par campagne","Shell mass generated per site and campaign","Khối lượng vỏ điều theo từng nhà máy và mùa vụ"),
        tr("Utilisation actuelle : énergie, extraction, vente ou élimination","Current use: energy, extraction, sale or disposal","Mục đích hiện tại: năng lượng, chiết xuất, bán hoặc thải bỏ"),
        tr("Propriété du flux et droit de l'affecter au projet carbone","Feedstock ownership and right to allocate it to the carbon project","Quyền sở hữu dòng nguyên liệu và quyền đưa vào dự án carbon"),
        tr("Prétraitement, humidité, qualité et sécurité process","Pre-treatment, moisture, quality and process safety","Tiền xử lý, độ ẩm, chất lượng và an toàn quá trình"),
        tr("LCA complète incluant transport et alternative de référence","Full LCA including transport and baseline alternative","LCA đầy đủ gồm vận chuyển và phương án cơ sở"),
    ]:
        st.markdown(f'<span class="pill orange">✓ {item}</span>', unsafe_allow_html=True)
    risk_note(tr("La coque de cajou peut avoir une valeur économique et des usages industriels existants. L'additionalité et la baseline sont donc un gate carbone majeur : le POC ne l'étiquette pas automatiquement comme déchet admissible.",
                 "Cashew shell can have economic value and existing industrial uses. Additionality and baseline are therefore major carbon gates: the POC does not automatically label it as eligible waste.",
                 "Vỏ điều có thể có giá trị kinh tế và các mục đích công nghiệp hiện hữu. Vì vậy tính bổ sung và kịch bản cơ sở là điều kiện carbon quan trọng: POC không tự động coi đây là chất thải đủ điều kiện."))

# =============================================================================
# LIVE MRV DEMO
# =============================================================================

elif PAGE == "live":
    hero("📡 " + tr("MRV EDGE — DÉMONSTRATEUR", "EDGE MRV — DEMONSTRATOR", "MRV EDGE — MÔ HÌNH TRÌNH DIỄN"),
         tr("Télémétrie synthétique illustrant le dossier de preuve par lot. Ce ne sont pas des données réelles d'un site vietnamien.",
            "Synthetic telemetry illustrating a batch proof pack. These are not live data from a Vietnamese site.",
            "Dữ liệu mô phỏng minh họa hồ sơ bằng chứng theo lô. Đây không phải dữ liệu trực tiếp từ một địa điểm tại Việt Nam."),
         tr("DEMO • DONNÉES SYNTHÉTIQUES", "DEMO • SYNTHETIC DATA", "DEMO • DỮ LIỆU MÔ PHỎNG"))

    feed_key = st.selectbox(tr("Filière", "Feedstock", "Nguồn nguyên liệu"), list(FEEDSTOCKS.keys()),
                            format_func=lambda k: FEEDSTOCKS[k]["emoji"] + " " + FEEDSTOCKS[k]["name"][st.session_state.lang])
    if st.button(tr("🔄 Actualiser la démo", "🔄 Refresh demo", "🔄 Làm mới demo")):
        st.session_state.demo_tick += 1
        st.rerun()
    rng = np.random.default_rng(20260916 + st.session_state.demo_tick + list(FEEDSTOCKS).index(feed_key))
    now = datetime.now()
    times = [now - timedelta(minutes=5*(35-i)) for i in range(36)]
    mass = np.clip(rng.normal(4.6, .35, 36), 3.5, 5.6)
    moisture = np.clip(rng.normal(14 if feed_key != "rice" else 12, 1.6, 36), 8, 20)
    temp = np.clip(rng.normal(525, 14, 36), 480, 565)
    uptime = np.clip(rng.normal(99.94, .03, 36), 99.75, 100)
    df = pd.DataFrame({"time":times,"feed_t_h":mass,"moisture_pct":moisture,"reactor_c":temp,"integrity_pct":uptime})
    c1,c2,c3,c4=st.columns(4)
    with c1: metric_card(tr("Débit feedstock","Feedstock rate","Lưu lượng nguyên liệu"),f"{df.feed_t_h.iloc[-1]:.2f} t/h",FEEDSTOCKS[feed_key]["name"][st.session_state.lang],"green")
    with c2: metric_card(tr("Humidité","Moisture","Độ ẩm"),f"{df.moisture_pct.iloc[-1]:.1f}%",tr("mesure démo","demo measurement","dữ liệu demo"),"blue")
    with c3: metric_card(tr("Réacteur","Reactor","Lò phản ứng"),f"{df.reactor_c.iloc[-1]:.0f} °C",tr("mesure démo","demo measurement","dữ liệu demo"),"gold")
    with c4: metric_card(tr("Intégrité chaîne","Chain integrity","Tính toàn vẹn chuỗi"),f"{df.integrity_pct.iloc[-1]:.2f}%",tr("événements signés simulés","simulated signed events","sự kiện ký số mô phỏng"),"blue")
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=df.time,y=df.reactor_c,name=tr("Température °C","Temperature °C","Nhiệt độ °C")))
    fig.add_trace(go.Scatter(x=df.time,y=df.moisture_pct,name=tr("Humidité %","Moisture %","Độ ẩm %"),yaxis="y2"))
    fig.update_layout(height=390,margin=dict(l=20,r=20,t=45,b=20),yaxis=dict(title="°C"),yaxis2=dict(title="%",overlaying="y",side="right"))
    st.plotly_chart(fig,use_container_width=True)
    payload={"feedstock":feed_key,"timestamp":now.isoformat(),"mass_t_h":round(float(df.feed_t_h.iloc[-1]),3),"moisture_pct":round(float(df.moisture_pct.iloc[-1]),2),"reactor_c":round(float(df.reactor_c.iloc[-1]),1)}
    st.code(json.dumps(payload,ensure_ascii=False,indent=2)+"\nsha256: "+demo_hash(payload), language="json")
    scenario_note(tr("Dans le vrai POC, les données doivent venir d'instruments identifiés, calibrés et reliés à un lot physique avec provenance, masse, humidité, paramètres process et destination du biochar.",
                     "In the real POC, data must come from identified and calibrated instruments linked to a physical batch with provenance, mass, moisture, process parameters and biochar end-use.",
                     "Trong POC thực tế, dữ liệu phải đến từ thiết bị được nhận dạng và hiệu chuẩn, gắn với từng lô vật lý gồm nguồn gốc, khối lượng, độ ẩm, thông số quá trình và nơi sử dụng biochar."))

# =============================================================================
# 6-MONTH PILOT
# =============================================================================

elif PAGE == "pilot":
    hero("🧪 " + tr("POC VIETNAM — 6 MOIS", "VIETNAM POC — 6 MONTHS", "POC VIỆT NAM — 6 THÁNG"),
         tr("Un seul programme de 24 semaines, trois filières testées sous le même cadre MRV.",
            "One 24-week program, three value chains tested under the same MRV framework.",
            "Một chương trình 24 tuần, thử nghiệm ba chuỗi giá trị trong cùng một khung MRV."),
         tr("24 SEMAINES • 3 FILIÈRES • 1 PROOF PACK", "24 WEEKS • 3 FEEDSTOCKS • 1 PROOF PACK", "24 TUẦN • 3 NGUỒN NGUYÊN LIỆU • 1 HỒ SƠ BẰNG CHỨNG"))
    phases = [
        (tr("Phase 1 • S1–S4","Phase 1 • W1–W4","Giai đoạn 1 • Tuần 1–4"), tr("Cartographie & contrats","Mapping & contracting","Lập bản đồ & hợp đồng"), tr("Identifier transformateurs coco, rizeries, acteurs cajou; propriété des flux; usages actuels; périmètre MRV.","Identify coconut processors, rice mills and cashew actors; feedstock ownership; current uses; MRV boundary.","Xác định nhà chế biến dừa, nhà máy xay xát và doanh nghiệp điều; quyền sở hữu dòng nguyên liệu; mục đích hiện tại; ranh giới MRV.")),
        (tr("Phase 2 • S5–S8","Phase 2 • W5–W8","Giai đoạn 2 • Tuần 5–8"), tr("Caractérisation feedstock","Feedstock characterization","Đặc tính nguyên liệu"), tr("Masse, humidité, contaminants, saisonnalité, logistique et baseline pour les trois filières.","Mass, moisture, contaminants, seasonality, logistics and baseline for all three value chains.","Khối lượng, độ ẩm, tạp chất, tính mùa vụ, logistics và kịch bản cơ sở cho cả ba chuỗi.")),
        (tr("Phase 3 • S9–S16","Phase 3 • W9–W16","Giai đoạn 3 • Tuần 9–16"), tr("Campagnes de production","Production campaigns","Chiến dịch sản xuất"), tr("Lots séparés coco/riz/cajou, télémétrie edge, bilans massiques et échantillonnage laboratoire.","Separate coconut/rice/cashew batches, edge telemetry, mass balances and laboratory sampling.","Các lô dừa/lúa/điều riêng biệt, dữ liệu edge, cân bằng khối lượng và lấy mẫu phòng thí nghiệm.")),
        (tr("Phase 4 • S17–S20","Phase 4 • W17–W20","Giai đoạn 4 • Tuần 17–20"), tr("LCA & usage final","LCA & end use","LCA & sử dụng cuối"), tr("Émissions transport/process, qualité biochar, destination, permanence et impacts sols/eau à documenter sans sur-promesse.","Transport/process emissions, biochar quality, end-use, permanence and soil/water impacts documented without overclaiming.","Phát thải vận chuyển/quá trình, chất lượng biochar, nơi sử dụng, độ bền và tác động đất/nước được ghi nhận mà không phóng đại.")),
        (tr("Phase 5 • S21–S24","Phase 5 • W21–W24","Giai đoạn 5 • Tuần 21–24"), tr("Audit pack & scale-up","Audit pack & scale-up","Hồ sơ kiểm toán & mở rộng"), tr("Gap analysis Verra/Puro + règles Vietnam, proof pack par filière, décision de scale-up et choix de la voie de certification.","Verra/Puro + Vietnam rules gap analysis, proof pack per feedstock, scale-up decision and certification pathway selection.","Phân tích khoảng cách theo Verra/Puro + quy định Việt Nam, hồ sơ bằng chứng theo từng nguyên liệu, quyết định mở rộng và lựa chọn lộ trình chứng nhận.")),
    ]
    for p, title, desc in phases:
        st.markdown(f'<div class="panel"><span class="pill blue">{p}</span><h3>{title}</h3><p>{desc}</p></div>', unsafe_allow_html=True)
    success_note(tr("Livrable final : trois dossiers feedstock comparables, un modèle MRV commun et une recommandation de voie carbone par filière — sans prétendre à une certification avant validation indépendante.",
                    "Final deliverable: three comparable feedstock dossiers, one common MRV model and a carbon-pathway recommendation per value chain — without claiming certification before independent validation.",
                    "Sản phẩm cuối: ba bộ hồ sơ nguyên liệu có thể so sánh, một mô hình MRV chung và khuyến nghị lộ trình carbon cho từng chuỗi — không tuyên bố chứng nhận trước khi có thẩm định độc lập."))

# =============================================================================
# BUSINESS CASE
# =============================================================================

elif PAGE == "business":
    hero("📊 " + tr("BUSINESS CASE — SIMULATION", "BUSINESS CASE — SIMULATION", "HIỆU QUẢ KINH TẾ — MÔ PHỎNG"),
         tr("Tester une filière ou agréger les trois. Tous les paramètres économiques et techniques ci-dessous sont modifiables et ne sont pas des données officielles vietnamiennes.",
            "Test one value chain or aggregate all three. All technical and economic parameters below are adjustable and are not official Vietnamese data.",
            "Thử nghiệm từng chuỗi hoặc gộp cả ba. Tất cả thông số kỹ thuật và kinh tế dưới đây có thể điều chỉnh và không phải dữ liệu chính thức của Việt Nam."),
         tr("SCÉNARIO • PAS UNE PRÉVISION", "SCENARIO • NOT A FORECAST", "KỊCH BẢN • KHÔNG PHẢI DỰ BÁO"))

    selected = st.radio(tr("Filière simulée","Simulated feedstock","Nguồn nguyên liệu mô phỏng"), ["coconut","rice","cashew","all"], horizontal=True,
                        format_func=lambda k: tr("🌐 Les 3 filières","🌐 All 3 feedstocks","🌐 Cả 3 nguồn") if k=="all" else FEEDSTOCKS[k]["emoji"]+" "+FEEDSTOCKS[k]["name"][st.session_state.lang])
    default_feed = 30_000 if selected=="all" else FEEDSTOCKS[selected]["default_feed_t"]
    default_yield = 29 if selected=="all" else FEEDSTOCKS[selected]["default_yield"]
    default_cdr = 1.9 if selected=="all" else FEEDSTOCKS[selected]["default_cdr"]
    a,b,c=st.columns(3)
    with a:
        feedstock=st.number_input(tr("Gisement sec disponible [t/an]","Available dry feedstock [t/yr]","Nguyên liệu khô sẵn có [tấn/năm]"), min_value=100, max_value=5_000_000, value=int(default_feed), step=1000)
        share=st.slider(tr("Part réellement mobilisable [%]","Actually mobilisable share [%]","Tỷ lệ thực sự có thể huy động [%]"),5,100,POC_DEFAULTS["eligible_share_pct"],5)
    with b:
        yld=st.slider(tr("Rendement biochar [%]","Biochar yield [%]","Hiệu suất biochar [%]"),15,40,int(default_yield),1)
        cdr=st.slider(tr("CDR net [tCO₂e/t biochar]","Net CDR [tCO₂e/t biochar]","CDR ròng [tCO₂e/t biochar]"),1.0,2.6,float(default_cdr),0.1)
    with c:
        price=st.slider(tr("Prix CDR [€/tCO₂e]","CDR price [€/tCO₂e]","Giá CDR [€/tCO₂e]"),100,600,POC_DEFAULTS["cdr_price_eur_t"],25)
        capex=st.number_input("CAPEX [€]",min_value=100_000,max_value=20_000_000,value=POC_DEFAULTS["pilot_capex_eur"],step=50_000)
        opex=st.number_input("OPEX [€/an]",min_value=20_000,max_value=5_000_000,value=POC_DEFAULTS["annual_opex_eur"],step=10_000)

    sc=calc_scenario(feedstock,share,yld,cdr,price,POC_DEFAULTS["biochar_value_eur_t"],POC_DEFAULTS["usable_heat_mwh_per_t_feedstock"],POC_DEFAULTS["heat_value_eur_mwh"])
    annual_net=sc["gross"]-opex
    payback=capex/annual_net if annual_net>0 else math.inf
    c1,c2,c3,c4=st.columns(4)
    with c1: metric_card(tr("Feedstock traité","Feedstock processed","Nguyên liệu xử lý"),f"{fmt_int(sc['feed'])} t/an",tr("après part mobilisable","after mobilisable share","sau tỷ lệ huy động"),"blue")
    with c2: metric_card("Biochar",f"{fmt_int(sc['biochar'])} t/an",tr("simulation","simulation","mô phỏng"),"green")
    with c3: metric_card("Net CDR",f"{fmt_int(sc['cdr'])} tCO₂e/an",tr("facteur scénario, pas crédit certifié","scenario factor, not certified credits","hệ số kịch bản, không phải tín chỉ đã chứng nhận"),"gold")
    with c4: metric_card(tr("Payback simplifié","Simplified payback","Hoàn vốn đơn giản"),f"{fmt_dec(payback)} {tr('ans','years','năm')}" if math.isfinite(payback) else "n/a",tr("hors financement/impôts","excl. financing/tax","không gồm tài chính/thuế"),"cashew")

    years=np.arange(0,6)
    cash=[-capex]+[annual_net]*5
    cumulative=np.cumsum(cash)
    fig=go.Figure()
    fig.add_trace(go.Bar(x=years,y=cash,name=tr("Cash-flow annuel","Annual cash flow","Dòng tiền hàng năm")))
    fig.add_trace(go.Scatter(x=years,y=cumulative,mode="lines+markers",name=tr("Cumulé","Cumulative","Lũy kế")))
    fig.update_layout(height=410,margin=dict(l=20,r=20,t=50,b=20),xaxis_title=tr("Année","Year","Năm"),yaxis_title="€")
    st.plotly_chart(fig,use_container_width=True)
    scenario_note(tr("Non inclus : collecte réelle, broyage/séchage, foncier, permis, raccordement, laboratoire, validation/vérification, registry, financement, fiscalité, indisponibilité, valeur alternative des résidus et risque de prix. Un TEA local est requis avant investissement.",
                     "Not included: actual collection, grinding/drying, land, permits, interconnection, laboratory, validation/verification, registry, financing, tax, downtime, alternative residue value and price risk. A local TEA is required before investment.",
                     "Chưa bao gồm: thu gom thực tế, nghiền/sấy, đất, giấy phép, đấu nối, phòng thí nghiệm, thẩm định/xác minh, registry, tài chính, thuế, thời gian dừng máy, giá trị thay thế của phụ phẩm và rủi ro giá. Cần TEA tại địa phương trước khi đầu tư."))

# =============================================================================
# MRV ARCHITECTURE
# =============================================================================

elif PAGE == "mrv":
    hero("🔐 " + tr("ARCHITECTURE MRV REKARBON", "REKARBON MRV ARCHITECTURE", "KIẾN TRÚC MRV REKARBON"),
         tr("Une architecture commune pour les trois filières, du lot physique au dossier d'audit.",
            "One common architecture for all three feedstocks, from physical batch to audit pack.",
            "Một kiến trúc chung cho cả ba nguồn nguyên liệu, từ lô vật lý đến hồ sơ kiểm toán."),
         tr("EDGE • SIGNATURES • HASH CHAIN • PROOF PACK", "EDGE • SIGNATURES • HASH CHAIN • PROOF PACK", "EDGE • CHỮ KÝ • HASH CHAIN • PROOF PACK"))
    st.markdown(f"""
    <div class="arch-grid">
      <div class="arch" style="background:linear-gradient(135deg,#16865A,#0A5D3D)"><div style="font-size:2rem">🌿</div><h4>{tr('1. Feedstock','1. Feedstock','1. Nguyên liệu')}</h4><small>{tr('Origine • propriétaire • type • masse • humidité • baseline','Origin • owner • type • mass • moisture • baseline','Nguồn gốc • chủ sở hữu • loại • khối lượng • độ ẩm • baseline')}</small></div>
      <div class="arch" style="background:linear-gradient(135deg,#DA251D,#8D160F)"><div style="font-size:2rem">🔥</div><h4>{tr('2. Process','2. Process','2. Quá trình')}</h4><small>{tr('Lot • température • temps • énergie • gaz • biochar','Batch • temperature • time • energy • gas • biochar','Lô • nhiệt độ • thời gian • năng lượng • khí • biochar')}</small></div>
      <div class="arch" style="background:linear-gradient(135deg,#087EA4,#04526C)"><div style="font-size:2rem">🧪</div><h4>{tr('3. Qualité','3. Quality','3. Chất lượng')}</h4><small>{tr('Carbone organique • H/Corg • humidité • contaminants • labo','Organic carbon • H/Corg • moisture • contaminants • lab','Carbon hữu cơ • H/Corg • độ ẩm • tạp chất • phòng lab')}</small></div>
      <div class="arch" style="background:linear-gradient(135deg,#6B4FA3,#3D2868)"><div style="font-size:2rem">🔏</div><h4>{tr('4. Intégrité','4. Integrity','4. Tính toàn vẹn')}</h4><small>Ed25519 • hash chain • timestamp • batch ID • access log</small></div>
      <div class="arch" style="background:linear-gradient(135deg,#B66B2E,#784018)"><div style="font-size:2rem">🌱</div><h4>{tr('5. Usage final','5. End use','5. Sử dụng cuối')}</h4><small>{tr('Destination • quantité • application • stockage • preuve','Destination • quantity • application • storage • evidence','Nơi sử dụng • khối lượng • ứng dụng • lưu giữ • bằng chứng')}</small></div>
      <div class="arch" style="background:linear-gradient(135deg,#17212B,#000)"><div style="font-size:2rem">📦</div><h4>{tr('6. Proof Pack','6. Proof Pack','6. Proof Pack')}</h4><small>{tr('Mass balance • LCA • audit trail • exports registry','Mass balance • LCA • audit trail • registry exports','Cân bằng khối lượng • LCA • audit trail • xuất dữ liệu registry')}</small></div>
    </div>""", unsafe_allow_html=True)
    st.markdown("### " + tr("Audit gates communs","Common audit gates","Các cổng kiểm toán chung"))
    gates=[
        tr("G1 — Provenance et droit sur le feedstock","G1 — Feedstock provenance and rights","G1 — Nguồn gốc và quyền đối với nguyên liệu"),
        tr("G2 — Statut waste/residue et baseline documentés","G2 — Waste/residue status and baseline documented","G2 — Tình trạng chất thải/phụ phẩm và baseline được ghi nhận"),
        tr("G3 — Masse, humidité, calibration et chaîne de custody","G3 — Mass, moisture, calibration and chain of custody","G3 — Khối lượng, độ ẩm, hiệu chuẩn và chain of custody"),
        tr("G4 — Qualité biochar et permanence mesurées","G4 — Biochar quality and permanence measured","G4 — Chất lượng biochar và độ bền được đo"),
        tr("G5 — LCA nette incluant prétraitement et transport","G5 — Net LCA including preprocessing and transport","G5 — LCA ròng gồm tiền xử lý và vận chuyển"),
        tr("G6 — Usage final et non-double comptage","G6 — End-use and no double counting","G6 — Sử dụng cuối và không tính trùng"),
        tr("G7 — Validation/vérification et voie registry","G7 — Validation/verification and registry pathway","G7 — Thẩm định/xác minh và lộ trình registry"),
    ]
    for gate in gates: st.markdown(f'<span class="pill blue">🔎 {gate}</span>',unsafe_allow_html=True)

# =============================================================================
# CARBON / COMPLIANCE
# =============================================================================

elif PAGE == "compliance":
    hero("📋 " + tr("CARBONE & CONFORMITÉ — VIETNAM", "CARBON & COMPLIANCE — VIETNAM", "CARBON & TUÂN THỦ — VIỆT NAM"),
         tr("Le POC prépare les preuves. La certification, l'enregistrement et la négociabilité dépendent ensuite de la méthodologie, du registre et des règles vietnamiennes applicables.",
            "The POC prepares evidence. Certification, registration and tradability then depend on the methodology, registry and applicable Vietnamese rules.",
            "POC chuẩn bị bằng chứng. Việc chứng nhận, đăng ký và khả năng giao dịch sau đó phụ thuộc vào phương pháp, registry và các quy định áp dụng tại Việt Nam."),
         tr("RÈGLES 2026 • À VALIDER PROJET PAR PROJET", "2026 RULES • VALIDATE PROJECT BY PROJECT", "QUY ĐỊNH 2026 • XÁC NHẬN THEO TỪNG DỰ ÁN"))

    rows=[
        ["Vietnam — Decree 06/2022 + 119/2025", tr("Réduction GES, mécanismes de crédits et Article 6; amendement 119 effectif depuis le 01/08/2025.","GHG mitigation, credit mechanisms and Article 6; Decree 119 amendment effective 1 Aug 2025.","Giảm phát thải KNK, cơ chế tín chỉ và Điều 6; Nghị định 119 có hiệu lực từ 01/08/2025."), tr("Cadre national à respecter","National framework to comply with","Khung quốc gia phải tuân thủ")],
        ["Decision 232/QD-TTg (2025)", tr("Schéma de création et développement du marché carbone vietnamien; phase pilote jusqu'à fin 2028.","Scheme establishing and developing Vietnam's carbon market; pilot phase through end-2028.","Đề án thành lập và phát triển thị trường carbon Việt Nam; giai đoạn thí điểm đến hết 2028."), tr("Contexte marché domestique","Domestic market context","Bối cảnh thị trường trong nước")],
        ["Decree 29/2026/ND-CP", tr("Règles de la plateforme carbone domestique : enregistrement, code, transfert de propriété, dépôt, transaction et règlement.","Domestic carbon platform rules: registration, coding, ownership transfer, custody, trading and settlement.","Quy định sàn giao dịch carbon trong nước: đăng ký, cấp mã, chuyển quyền sở hữu, lưu ký, giao dịch và thanh toán."), tr("Gate si marché domestique","Gate for domestic market","Điều kiện nếu tham gia thị trường trong nước")],
        ["Verra VCS VM0044 v1.2", tr("Méthodologie biochar active, applicable mondialement, pour biomasse résiduelle convertie en biochar; additionalité et monitoring requis.","Active global biochar methodology for waste biomass converted to biochar; additionality and monitoring required.","Phương pháp biochar đang hoạt động toàn cầu cho sinh khối thải/phụ phẩm chuyển thành biochar; yêu cầu tính bổ sung và giám sát."), tr("Voie volontaire potentielle","Potential voluntary pathway","Lộ trình tự nguyện tiềm năng")],
        ["Puro Biochar Methodology — Edition 2025 v2", tr("Voie CDR durable avec critères de sourcing biomasse, LCA, validation/vérification et CORC200+ selon la méthodologie en vigueur.","Durable CDR pathway with biomass-sourcing criteria, LCA, validation/verification and CORC200+ under the current methodology.","Lộ trình CDR bền vững với tiêu chí nguồn sinh khối, LCA, thẩm định/xác minh và CORC200+ theo phương pháp hiện hành."), tr("Voie CDR potentielle","Potential CDR pathway","Lộ trình CDR tiềm năng")],
        ["ISO 14064-2", tr("Cadre de quantification et reporting GES au niveau projet; utile pour structurer le MRV mais ne crée pas un crédit à lui seul.","Project-level GHG quantification and reporting framework; useful for MRV structure but does not itself issue a credit.","Khung định lượng và báo cáo KNK cấp dự án; hữu ích cho MRV nhưng tự nó không tạo tín chỉ."), tr("Alignement MRV","MRV alignment","Căn chỉnh MRV")],
    ]
    st.dataframe(pd.DataFrame(rows,columns=[tr("Règle / standard","Rule / standard","Quy định / tiêu chuẩn"),tr("Ce que cela signifie","What it means","Ý nghĩa"),tr("Rôle dans le POC","Role in POC","Vai trò trong POC")]),use_container_width=True,hide_index=True)

    st.warning(tr(
        "Un dashboard MRV ne crée pas de crédits certifiables. Pour chaque filière, il faut démontrer l'éligibilité du feedstock, la baseline, l'additionalité, le bilan de masse, la qualité du biochar, la LCA nette, la permanence, l'usage final, l'absence de double comptage et passer validation/vérification selon la voie choisie.",
        "An MRV dashboard does not create certifiable credits. For each feedstock, the project must demonstrate feedstock eligibility, baseline, additionality, mass balance, biochar quality, net LCA, permanence, end-use, no double counting, and complete validation/verification under the selected pathway.",
        "Một dashboard MRV không tự tạo ra tín chỉ có thể chứng nhận. Với từng nguồn nguyên liệu, dự án phải chứng minh tính đủ điều kiện, baseline, tính bổ sung, cân bằng khối lượng, chất lượng biochar, LCA ròng, độ bền, sử dụng cuối, không tính trùng và hoàn thành thẩm định/xác minh theo lộ trình đã chọn.",
    ))

    st.markdown("### " + tr("Gates spécifiques aux trois filières","Feedstock-specific carbon gates","Điều kiện carbon riêng cho từng nguồn"))
    matrix=[
        [tr("Coco","Coconut","Dừa"), tr("Identifier coque/bourre comme résidu admissible; documenter usages existants et propriété du flux.","Establish shell/husk as eligible residue; document existing uses and feedstock rights.","Xác định vỏ/xơ dừa là phụ phẩm đủ điều kiện; ghi nhận mục đích sử dụng hiện tại và quyền đối với nguyên liệu.")],
        [tr("Riz","Rice","Lúa gạo"), tr("Baseline de la paille/trấu + contrôle du double comptage avec programmes méthane/riz bas-carbone.","Straw/husk baseline + double-counting control against methane/low-carbon-rice programs.","Baseline rơm/trấu + kiểm soát tính trùng với các chương trình methane/lúa phát thải thấp.")],
        [tr("Cajou","Cashew","Hạt điều"), tr("Usages industriels existants potentiellement significatifs : additionalité, déplacement et baseline à documenter en priorité.","Potentially significant existing industrial uses: additionality, displacement and baseline are priority evidence.","Có thể có các mục đích công nghiệp hiện hữu đáng kể: ưu tiên chứng minh tính bổ sung, dịch chuyển và baseline.")],
    ]
    st.dataframe(pd.DataFrame(matrix,columns=[tr("Filière","Feedstock","Nguồn"),tr("Gate carbone prioritaire","Priority carbon gate","Điều kiện carbon ưu tiên")]),use_container_width=True,hide_index=True)
    risk_note(tr("L'éligibilité d'un crédit vietnamien à la plateforme domestique, ou son transfert international sous l'Article 6, ne doit pas être présumée. Une revue juridique/réglementaire locale et les autorisations applicables sont un gate séparé du standard volontaire.",
                 "Eligibility of a Vietnamese credit for the domestic platform, or international transfer under Article 6, must not be assumed. Local legal/regulatory review and applicable authorisations are a separate gate from voluntary-standard certification.",
                 "Không được mặc định rằng tín chỉ tại Việt Nam đủ điều kiện giao dịch trên sàn trong nước hoặc chuyển giao quốc tế theo Điều 6. Việc rà soát pháp lý/quy định tại Việt Nam và các phê duyệt cần thiết là điều kiện riêng, tách biệt với chứng nhận theo tiêu chuẩn tự nguyện."))

# =============================================================================
# SOURCES
# =============================================================================

elif PAGE == "sources":
    hero("📚 " + tr("DONNÉES, SOURCES & HYPOTHÈSES", "DATA, SOURCES & ASSUMPTIONS", "DỮ LIỆU, NGUỒN & GIẢ ĐỊNH"),
         tr("Traçabilité des chiffres utilisés dans le POC et séparation explicite entre source publique et scénario.",
            "Traceability of the figures used in the POC and explicit separation between public sources and scenarios.",
            "Truy xuất nguồn của các số liệu dùng trong POC và phân tách rõ dữ liệu công bố với kịch bản."),
         tr("SOURCÉ • AUDITABLE • PAS DE FAUX OFFICIEL", "SOURCED • AUDITABLE • NO FALSE OFFICIAL CLAIMS", "CÓ NGUỒN • CÓ THỂ KIỂM TOÁN • KHÔNG GÁN NHÃN CHÍNH THỨC SAI"))

    source_rows=[
        [tr("Réorganisation administrative","Administrative reorganisation","Sắp xếp hành chính"),"Government of Vietnam","2025",SOURCES["admin"]],
        [tr("Coco Bến Tre","Bến Tre coconut","Dừa Bến Tre"),"Ministry of Industry and Trade","2024",SOURCES["coconut_bentre"]],
        [tr("Coco Vietnam","Vietnam coconut","Dừa Việt Nam"),"Ministry of Agriculture and Environment","2025/2026",SOURCES["coconut_vn"]],
        [tr("Riz Vietnam","Vietnam rice","Lúa Việt Nam"),"National Statistics Office","2025",SOURCES["rice_2025"]],
        [tr("Riz / paille Mékong","Mekong rice / straw","Lúa / rơm Mekong"),"Ministry of Agriculture and Environment","2025",SOURCES["rice_mekong"]],
        [tr("Résidus riz","Rice residues","Phụ phẩm lúa"),"UNDP Viet Nam","published estimate",SOURCES["rice_residue"]],
        [tr("Cajou 2025","Cashew 2025","Hạt điều 2025"),"Vietnam Trade Office / MAE / VINACAS reporting","2025",SOURCES["cashew_2025"]],
        ["Decree 119/2025/ND-CP","Government of Vietnam","2025",SOURCES["vn_decree_119"]],
        ["Decision 232/QD-TTg","Government / MAE","2025",SOURCES["vn_decision_232"]],
        ["Decree 29/2026/ND-CP","Government of Vietnam","2026",SOURCES["vn_decree_29"]],
        ["Vietnam carbon exchange pilot","Government News","2026",SOURCES["vn_exchange"]],
        ["Verra VM0044 v1.2","Verra","active 2025–",SOURCES["verra"]],
        ["Puro Biochar Edition 2025 v2","Puro.earth","current docs 2026",SOURCES["puro"]],
    ]
    for title, publisher, year, url in source_rows:
        st.markdown(f'<div class="panel"><b>{title}</b><br><small class="source">{publisher} • {year}<br><a href="{url}" target="_blank">{url}</a></small></div>',unsafe_allow_html=True)

    st.markdown("### " + tr("Hypothèses POC qui nécessitent une mesure locale","POC assumptions requiring local measurement","Giả định POC cần đo tại địa phương"))
    assumptions=[
        tr("Tonnes/an de résidus coco réellement accessibles","Actually accessible coconut residues t/yr","Tấn/năm phụ phẩm dừa thực sự tiếp cận được"),
        tr("Tonnes/an de balle/paille de riz collectables sans déplacer un usage utile","Collectable rice husk/straw t/yr without displacing beneficial use","Tấn/năm trấu/rơm có thể thu gom mà không thay thế mục đích hữu ích"),
        tr("Tonnes/an de coques de cajou disponibles par transformateur","Cashew shell t/yr available per processor","Tấn/năm vỏ điều sẵn có theo từng nhà chế biến"),
        tr("Rendements biochar par feedstock et conditions process","Biochar yields by feedstock and process conditions","Hiệu suất biochar theo nguyên liệu và điều kiện quá trình"),
        tr("Facteur CDR net après LCA","Net CDR factor after LCA","Hệ số CDR ròng sau LCA"),
        tr("Prix, CAPEX, OPEX, chaleur valorisable et valeur produit","Price, CAPEX, OPEX, usable heat and product value","Giá, CAPEX, OPEX, nhiệt có thể sử dụng và giá trị sản phẩm"),
    ]
    for a in assumptions: st.markdown(f'<span class="pill gold">⚙️ {a}</span>',unsafe_allow_html=True)
    scenario_note(tr("Le code conserve volontairement ces variables comme hypothèses modifiables. Elles devront être remplacées par les mesures du partenaire vietnamien avant toute présentation comme données de projet.",
                     "The code deliberately keeps these variables as adjustable assumptions. They must be replaced by measurements from the Vietnamese partner before being presented as project data.",
                     "Mã nguồn cố ý giữ các biến này ở dạng giả định có thể điều chỉnh. Chúng phải được thay bằng số đo từ đối tác Việt Nam trước khi được trình bày như dữ liệu của dự án."))

