"""
KopiSeru — Executive Dashboard
================================
1-page executive dashboard with:
- Sidebar that works properly
- KPI row at top
- Page selector (radio pills) below KPI
- Per-chart filters aligned on the right of each chart title
- 2 charts per page in card containers
- Insight notes below each chart
- Coffee-themed, clean, executive aesthetic
"""

import base64
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# -------------------------------------------------------------------
# Page config
# -------------------------------------------------------------------
st.set_page_config(
    page_title="KopiSeru — Executive Dashboard",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "dataset_final.csv"
ASSET_DIR = BASE_DIR / "asset"


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]).copy()

    # Core derived columns
    df["profit"] = df["total_revenue"] - df["operating_cost"]
    df["profit_margin"] = (
        (df["profit"] / df["total_revenue"]).replace([pd.NA, pd.NaT], 0) * 100
    )
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
    df["month_name"] = df["date"].dt.strftime("%b %Y")
    return df


def img_b64(filename: str) -> str:
    p = ASSET_DIR / filename
    if not p.exists():
        return ""
    with open(p, "rb") as f:
        return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"


def fmt_rp(v: float) -> str:
    v = float(v)
    if abs(v) >= 1e12:
        return f"Rp {v/1e12:.2f} Triliun"
    if abs(v) >= 1e9:
        return f"Rp {v/1e9:.2f} Miliar"
    if abs(v) >= 1e6:
        return f"Rp {v/1e6:.2f} Juta"
    if abs(v) >= 1e3:
        return f"Rp {v/1e3:.0f} Ribu"
    return f"Rp {v:,.0f}"


def pct(v: float) -> str:
    return f"{v:.1f}%"


DF = load_data()

# -------------------------------------------------------------------
# CSS — Coffee Executive Theme
# -------------------------------------------------------------------
st.markdown(
    r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
    --bg:     #F5F1EB;
    --card:   #FFFFFF;
    --text:   #2A1A14;
    --muted:  #7C6154;
    --line:   #E9DED6;
    --brown:  #5C3A2E;
    --cream:  #FBF7F2;
    --shadow: 0 4px 18px rgba(63,42,31,.07);
}

/* ── Base ───────────────────────────────────────── */
html, body, .stApp, .main, .block-container {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background: var(--bg) !important;
}

/* Allow page to scroll naturally inside the viewport */
.stApp, .main {
    overflow-y: auto !important;
}
.block-container {
    max-width: 1440px !important;
    padding: 0.6rem 2.5rem 1rem 2.5rem !important;
}
div[data-testid="stVerticalBlock"] { gap: 0.7rem !important; }
div[data-testid="stHorizontalBlock"] { gap: 1.4rem !important; }

/* ── Header bar ─────────────────────────────────── */
/* Keep sidebar toggle visible by NOT hiding the header entirely.
   Instead we just remove the extra toolbar/menu items. */
#MainMenu, footer, [data-testid="stToolbar"] { display: none !important; }
header[data-testid="stHeader"] {
    background: transparent !important;
    backdrop-filter: none !important;
}

/* ── Sidebar ────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #3F261F 0%, #4E342E 100%) !important;
    border-right: none !important;
    z-index: 999 !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    padding-top: 0.6rem !important;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span {
    color: #F1E7DD !important;
    font-size: .85rem !important;
}

/* Sidebar collapse / expand button — black, pinned top-right of sidebar */
button[data-testid="stBaseButton-headerNoPadding"],
[data-testid="collapsedControl"] {
    color: #000000 !important;
    z-index: 9999 !important;
}
[data-testid="collapsedControl"] svg {
    fill: #000000 !important;
    stroke: #000000 !important;
}
/* When sidebar is open, put close button at top-right inside sidebar */
section[data-testid="stSidebar"] button[data-testid="stBaseButton-headerNoPadding"] {
    position: absolute !important;
    top: 10px !important;
    right: 10px !important;
    left: auto !important;
    color: #F1E7DD !important;
    z-index: 10000 !important;
}
section[data-testid="stSidebar"] button[data-testid="stBaseButton-headerNoPadding"] svg {
    fill: #F1E7DD !important;
    stroke: #F1E7DD !important;
}

.sidebar-card {
    background: rgba(255,255,255,.10);
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 14px;
    padding: 12px 14px;
}

/* ── Typography ─────────────────────────────────── */
.hero-title {
    color: var(--text);
    font-size: 1.55rem;
    font-weight: 800;
    margin: 0;
    line-height: 1.15;
}
.hero-sub {
    color: var(--muted);
    font-size: 0.92rem;
    font-weight: 600;
    margin: 2px 0 0 0;
}

/* ── Selectbox / Dropdown fixes ─────────────────── */
/* Hide labels to keep compact look */
.stSelectbox label,
.stMultiSelect label {
    display: none !important;
}

/* Outer container */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    min-height: 36px !important;
    max-height: 38px !important;
    border-radius: 10px !important;
    border: 1px solid var(--line) !important;
    background: #FFFFFF !important;
    box-shadow: none !important;
    font-size: .85rem !important;
    padding: 0 !important;
}

/* ★ CRITICAL — force all selectbox text to dark brown */
div[data-baseweb="select"] {
    color: var(--text) !important;
}
div[data-baseweb="select"] * {
    color: var(--text) !important;
}
div[data-baseweb="select"] .css-1dimb5e-singleValue,
div[data-baseweb="select"] [data-testid="stMarkdownContainer"] p,
div[data-baseweb="select"] span,
div[data-baseweb="select"] div {
    color: var(--text) !important;
}
/* Placeholder */
div[data-baseweb="select"] [data-baseweb="tag"],
div[data-baseweb="select"] input::placeholder {
    color: var(--muted) !important;
}
/* Dropdown menu items */
ul[data-baseweb="menu"] li,
ul[data-baseweb="menu"] li *,
div[data-baseweb="popover"] ul li,
div[data-baseweb="popover"] ul li span {
    color: var(--text) !important;
    background: #fff !important;
}
ul[data-baseweb="menu"] li:hover,
ul[data-baseweb="menu"] li:hover * {
    background: var(--cream) !important;
}
/* Dropdown arrow icon */
div[data-baseweb="select"] svg {
    fill: var(--muted) !important;
}

/* ── Radio pills (page selector) ────────────────── */
div[data-testid="stRadio"] {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 8px 14px;
    box-shadow: var(--shadow);
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 0 auto;
    width: fit-content;
}
.stRadio > div {
    gap: .45rem !important;
    background: transparent !important;
    justify-content: center !important;
}
.stRadio label {
    padding: .45rem 1.15rem !important;
    border-radius: 999px !important;
    border: 1px solid var(--line) !important;
    background: rgba(255,255,255,.9) !important;
    margin: 0 !important;
    font-size: .86rem !important;
    font-weight: 700 !important;
    transition: all .2s ease !important;
    cursor: pointer !important;
}
.stRadio label p {
    color: #3E2A1E !important;
    font-weight: 700 !important;
}
.stRadio label[data-checked="true"] {
    background: var(--brown) !important;
    border-color: var(--brown) !important;
    box-shadow: 0 2px 8px rgba(92,58,46,.25) !important;
}
.stRadio label[data-checked="true"] p {
    color: #fff !important;
}

/* ── KPI cards ──────────────────────────────────── */
.kpi {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 18px 24px;
    height: 120px;
    box-shadow: var(--shadow);
    position: relative;
    text-align: left;
    transition: box-shadow .2s ease;
}
.kpi:hover {
    box-shadow: 0 6px 24px rgba(63,42,31,.12);
}
.kpi-t {
    color: var(--muted);
    font-size: .72rem;
    font-weight: 800;
    margin: 0;
    text-transform: uppercase;
    letter-spacing: .5px;
}
.kpi-v {
    color: var(--text);
    font-size: 1.5rem;
    font-weight: 800;
    margin: 6px 0 0 0;
    line-height: 1.05;
}
.kpi-s {
    color: var(--muted);
    font-size: .73rem;
    font-weight: 600;
    margin: 6px 0 0 0;
}
.kpi-i {
    position: absolute;
    top: 18px;
    right: 18px;
    width: 34px;
    height: 34px;
    opacity: .88;
}

/* ── Chart card container — style Streamlit's native bordered container ── */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--card) !important;
    border: 1px solid var(--line) !important;
    border-radius: 16px !important;
    box-shadow: var(--shadow) !important;
    padding: 16px 18px 12px 18px !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: transparent !important;
}
.chart-title {
    color: var(--text);
    font-size: 1.02rem;
    font-weight: 800;
    margin: 0;
    line-height: 1.2;
}
.chart-note {
    background: var(--cream);
    border: 1px solid #F0E6DE;
    border-radius: 10px;
    padding: 9px 14px;
    margin-top: 6px;
    color: var(--brown);
    font-size: .8rem;
    font-weight: 600;
    line-height: 1.4;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    text-align: center;
}

/* ── Plotly tweaks ──────────────────────────────── */
.js-plotly-plot .plotly .modebar { display: none !important; }

/* ── Global filter badge ────────────────────────── */
.filter-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 6px 14px;
    font-size: .82rem;
    font-weight: 700;
    color: var(--brown);
    box-shadow: var(--shadow);
}
</style>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------------------------
# Image assets
# -------------------------------------------------------------------
logo_b64 = img_b64("logo.png")
money_b64 = img_b64("money_ic.png")
people_b64 = img_b64("ic_people.png")
line_b64 = img_b64("icons_line-up.png")
pie_b64 = img_b64("icon-pie-chart.png")

# -------------------------------------------------------------------
# Sidebar
# -------------------------------------------------------------------
with st.sidebar:
    if logo_b64:
        st.markdown(
            f'<div style="text-align:center; padding: 6px 0 14px 0;">'
            f'<img src="{logo_b64}" style="max-width: 130px; opacity:.95;"></div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="sidebar-card" style="margin: 0 8px 10px 8px;">
            <div style="font-weight:800; color:#F3E7DA; margin-bottom:6px;">KOPISERU</div>
            <div style="font-size:.85rem; line-height:1.45; color:#E8DCCF;">
                Dashboard executive ringkas untuk membaca pertumbuhan,
                lokasi, channel, efisiensi, dan promo.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="sidebar-card" style="margin: 0 8px 10px 8px;">
            <div style="font-size:.75rem; color:#D8BFA6; font-weight:800;">DATA TERAKHIR DIPERBARUI</div>
            <div style="font-size:.9rem; color:#FFF; font-weight:700; margin-top:6px;">
                {DF["date"].max().strftime("%d %b %Y")}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sidebar-card" style="margin: 0 8px;">
            <div style="font-size:.75rem; color:#D8BFA6; font-weight:800;">NAVIGASI</div>
            <div style="font-size:.85rem; color:#FFF; font-weight:700; margin-top:8px; line-height:1.8;">
                • Dashboard Utama<br>
                • Pengaturan
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -------------------------------------------------------------------
# Header row
# -------------------------------------------------------------------
h_left, h_right = st.columns([0.55, 0.45], vertical_alignment="bottom")

with h_left:
    st.markdown(
        '<div class="hero-title">KopiSeru Executive Board</div>'
        '<div class="hero-sub">Ringkasan Performa & Profitabilitas Bisnis</div>',
        unsafe_allow_html=True,
    )

with h_right:
    # Inline filter — branch selector + period badge
    f1, f2 = st.columns([0.55, 0.45], vertical_alignment="center")
    with f1:
        st.markdown(
            '<div style="text-align:right; font-size:.82rem; color:#5C3A2E; font-weight:700;">'
            "Data model: 2021–2023<br>"
            '<span style="color:#7C6154; font-weight:600;">Filter Cabang:</span></div>',
            unsafe_allow_html=True,
        )
    with f2:
        branches = ["Semua Cabang"] + sorted(DF["branch_name"].unique().tolist())
        global_branch = st.selectbox(
            "Global Branch",
            branches,
            key="global_branch",
            label_visibility="collapsed",
        )

# Apply global filter
filtered_df = DF.copy()
if global_branch != "Semua Cabang":
    filtered_df = filtered_df[filtered_df["branch_name"] == global_branch]

# -------------------------------------------------------------------
# KPI Row
# -------------------------------------------------------------------
total_revenue = float(filtered_df["total_revenue"].sum())
total_profit = float(
    (filtered_df["total_revenue"] - filtered_df["operating_cost"]).sum()
)
npm = (total_profit / total_revenue * 100) if total_revenue else 0.0
total_transactions = float(filtered_df["total_transactions"].sum())

latest_year = int(DF["year"].max())
prev_year = latest_year - 1


def year_sum(df, col, year):
    return float(df.loc[df["year"] == year, col].sum())


prev_rev = year_sum(filtered_df, "total_revenue", prev_year)
prev_prof = float(
    (
        filtered_df.loc[filtered_df["year"] == prev_year, "total_revenue"]
        - filtered_df.loc[filtered_df["year"] == prev_year, "operating_cost"]
    ).sum()
)
prev_trx = year_sum(filtered_df, "total_transactions", prev_year)
prev_npm = (prev_prof / prev_rev * 100) if prev_rev else npm


def delta_text(curr, prev, is_pct=False):
    if prev == 0:
        return None
    if is_pct:
        diff = curr - prev
        return f"{diff:+.1f} pt"
    diff = (curr - prev) / prev * 100
    return f"{diff:+.1f}%"


d_rev = delta_text(total_revenue, prev_rev)
d_prof = delta_text(total_profit, prev_prof)
d_trx = delta_text(total_transactions, prev_trx)
d_npm = delta_text(npm, prev_npm, is_pct=True)


def kpi_html(title, value, subtitle, icon_b64_src, delta=None):
    delta_html = ""
    if delta:
        delta_html = (
            '<div class="kpi-s" style="color:#1B8F2C; font-weight:800;">'
            f'▲ {delta} <span style="color:#7C6154; font-weight:600;">'
            "vs tahun sebelumnya</span></div>"
        )
    else:
        delta_html = f'<div class="kpi-s">{subtitle}</div>'
    icon_tag = (
        f'<img class="kpi-i" src="{icon_b64_src}">' if icon_b64_src else ""
    )
    return f"""<div class="kpi">
<div class="kpi-t">{title}</div>
<div class="kpi-v">{value}</div>
{delta_html}
{icon_tag}
</div>"""


trx_fmt = (
    f"{total_transactions/1e6:.2f} Jt"
    if total_transactions >= 1e6
    else f"{total_transactions:,.0f}"
)

kpi_row_html = f"""<div style="display:flex; gap:1.6rem; width:100%;">
{kpi_html("Total Pendapatan", fmt_rp(total_revenue), "Omzet kotor", money_b64, d_rev)}
{kpi_html("Laba Bersih", fmt_rp(total_profit), "Keuntungan setelah biaya", line_b64, d_prof)}
{kpi_html("Net Profit Margin", pct(npm), "Rasio efisiensi profit", pie_b64, d_npm)}
{kpi_html("Total Transaksi", trx_fmt, "Indikator volume", people_b64, d_trx)}
</div>"""

st.markdown(kpi_row_html, unsafe_allow_html=True)

# -------------------------------------------------------------------
# Page selector
# -------------------------------------------------------------------
st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
page = st.radio(
    "Pilih tampilan",
    ["☕ Pertumbuhan", "📍 Lokasi & Channel", "⚡ Efisiensi & Promo"],
    horizontal=True,
    label_visibility="collapsed",
)
st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------------------
# Plot defaults
# -------------------------------------------------------------------
CH_H = 330
LAYOUT = dict(
    template="plotly_white",
    margin=dict(l=5, r=5, t=10, b=5),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(255,255,255,0)",
    font=dict(family="Plus Jakarta Sans", color="#4A352C", size=12),
    hoverlabel=dict(
        bgcolor="#FFFFFF",
        bordercolor="#C49A6C",
        font=dict(family="Plus Jakarta Sans", color="#4A352C", size=13),
    ),
)
CFG = dict(displayModeBar=False)
palette = ["#5C3A2E", "#8B5A2B", "#C49A6C", "#D7CCC8", "#A1887F", "#E6DCCF"]


def close_card(note: str):
    """Render insight note at the bottom of a chart card."""
    st.markdown(
        f'<div class="chart-note">{note}</div>',
        unsafe_allow_html=True,
    )


def card_header(title, filter_ratio=0.30):
    """Render chart title on the left & return the right column for the filter."""
    left_col, right_col = st.columns(
        [1 - filter_ratio, filter_ratio], vertical_alignment="center"
    )
    with left_col:
        st.markdown(
            f'<div class="chart-title">{title}</div>',
            unsafe_allow_html=True,
        )
    return right_col


# ===================================================================
# PAGE 1 — Pertumbuhan
# ===================================================================
if page == "☕ Pertumbuhan":
    col_l, col_r = st.columns(2)

    # ── Left chart: Revenue / Profit trend ──────────────────────────
    with col_l:
      with st.container(border=True):
        right_col = card_header("Tren Pendapatan Bulanan")
        with right_col:
            metric_sel = st.selectbox(
                "Metrik",
                ["Pendapatan", "Laba Bersih"],
                key="p1_metric",
                label_visibility="collapsed",
            )

        col = "total_revenue" if metric_sel == "Pendapatan" else "profit"
        d = (
            filtered_df.groupby("month", as_index=False)[col]
            .sum()
            .sort_values("month")
        )
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=d["month"],
                y=d[col],
                mode="lines",
                line=dict(color="#5C3A2E", width=3, shape="spline"),
                fill="tozeroy",
                fillcolor="rgba(92,58,46,.08)",
                hovertemplate=(
                    "<b>%{x|%b %Y}</b><br>Rp %{y:,.0f}<extra></extra>"
                ),
                name=metric_sel,
            )
        )
        fig.update_layout(**LAYOUT, height=CH_H, showlegend=False)
        fig.update_yaxes(
            showgrid=True,
            gridcolor="rgba(0,0,0,.05)",
            tickformat=".2s",
            title="",
        )
        fig.update_xaxes(
            showgrid=False, title="", tickangle=45, tickformat="%b %Y"
        )
        st.plotly_chart(fig, use_container_width=True, config=CFG, theme=None)

        if not d.empty:
            top_month = d.loc[d[col].idxmax(), "month"]
            close_card(
                f"📈 Puncak {metric_sel.lower()} terjadi pada "
                f"<b>{top_month.strftime('%B %Y')}</b>."
            )
        else:
            close_card("Data tidak tersedia.")

    # ── Right chart: Branch composition stacked area ────────────────
    with col_r:
      with st.container(border=True):
        right_col = card_header("Komposisi Cabang Teratas")
        with right_col:
            top_n = st.selectbox(
                "Top N",
                [3, 5, 8],
                index=1,
                key="p1_topn",
                label_visibility="collapsed",
            )

        top_branches = (
            filtered_df.groupby("branch_name")["total_revenue"]
            .sum()
            .sort_values(ascending=False)
            .head(top_n)
            .index.tolist()
        )
        d2 = (
            filtered_df[filtered_df["branch_name"].isin(top_branches)]
            .groupby(["month", "branch_name"], as_index=False)["total_revenue"]
            .sum()
        )
        d2["Cabang"] = d2["branch_name"].str.replace("KopiSeru ", "")

        fig2 = px.area(
            d2,
            x="month",
            y="total_revenue",
            color="Cabang",
            color_discrete_sequence=palette,
        )
        fig2.update_traces(
            hovertemplate=(
                "<b>%{fullData.name}</b><br>"
                "%{x|%b %Y}<br>Rp %{y:,.0f}<extra></extra>"
            )
        )
        fig2.update_layout(
            **LAYOUT,
            height=CH_H,
            legend=dict(
                orientation="v",
                y=1.02,
                x=1.02,
                title="",
                font=dict(size=11),
            ),
        )
        fig2.update_yaxes(
            showgrid=True,
            gridcolor="rgba(0,0,0,.05)",
            tickformat=".2s",
            title="",
        )
        fig2.update_xaxes(
            showgrid=False, title="", tickangle=45, tickformat="%b %Y"
        )
        st.plotly_chart(fig2, use_container_width=True, config=CFG, theme=None)

        if top_branches:
            best_branch = top_branches[0].replace("KopiSeru ", "")
            close_card(
                f"🏆 Cabang andalan secara konsisten adalah <b>{best_branch}</b>."
            )
        else:
            close_card("Data tidak tersedia.")

# ===================================================================
# PAGE 2 — Lokasi & Channel
# ===================================================================
elif page == "📍 Lokasi & Channel":
    col_l, col_r = st.columns(2)

    # ── Left: Revenue by branch type ────────────────────────────────
    with col_l:
      with st.container(border=True):
        right_col = card_header("Pendapatan per Tipe Lokasi")
        with right_col:
            loc_agg = st.selectbox(
                "Agregasi",
                ["Total Keseluruhan", "Rata-rata per Cabang"],
                key="p2_loc_agg",
                label_visibility="collapsed",
            )

        agg = "sum" if loc_agg == "Total Keseluruhan" else "mean"
        loc = (
            filtered_df.groupby("branch_type")["total_revenue"]
            .agg(agg)
            .reset_index()
            .sort_values("total_revenue", ascending=True)
        )

        fig = px.bar(
            loc,
            y="branch_type",
            x="total_revenue",
            orientation="h",
            color="total_revenue",
            color_continuous_scale=["#E8DCCF", "#5C3A2E"],
        )
        fig.update_traces(
            hovertemplate="<b>%{y}</b><br>Rp %{x:,.0f}<extra></extra>",
            marker_line_width=0,
        )
        fig.update_layout(
            **LAYOUT, height=CH_H, coloraxis_showscale=False
        )
        fig.update_xaxes(
            title="",
            tickformat=".2s",
            showgrid=True,
            gridcolor="rgba(0,0,0,.05)",
        )
        fig.update_yaxes(title="", showgrid=False)
        st.plotly_chart(fig, use_container_width=True, config=CFG, theme=None)

        if not loc.empty:
            close_card(
                f"📍 Tipe lokasi <b>{loc.iloc[-1]['branch_type']}</b> "
                "menjadi penyumbang terbesar."
            )
        else:
            close_card("Data tidak tersedia.")

    # ── Right: Channel donut ────────────────────────────────────────
    with col_r:
      with st.container(border=True):
        right_col = card_header("Distribusi Channel Penjualan")
        with right_col:
            if global_branch == "Semua Cabang":
                ch_branches = ["Semua Cabang"] + sorted(
                    DF["branch_name"].unique().tolist()
                )
                ch_sel = st.selectbox(
                    "Cabang",
                    ch_branches,
                    key="p2_ch_branch",
                    label_visibility="collapsed",
                )
                d = DF.copy()
                if ch_sel != "Semua Cabang":
                    d = d[d["branch_name"] == ch_sel]
            else:
                st.markdown(
                    f'<div style="text-align:right; font-size:.82rem; '
                    f'color:#8B6B5D; font-weight:600;">{global_branch}</div>',
                    unsafe_allow_html=True,
                )
                d = filtered_df.copy()

        chd = pd.DataFrame(
            {
                "Channel": ["Dine-in", "Delivery", "Takeaway"],
                "Persentase (%)": [
                    d.dine_in_percent.mean(),
                    d.delivery_percent.mean(),
                    d.takeaway_percent.mean(),
                ],
            }
        )

        fig2 = px.pie(
            chd,
            values="Persentase (%)",
            names="Channel",
            hole=0.55,
            color_discrete_sequence=palette,
        )
        fig2.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>%{value:.1f}%<extra></extra>",
        )
        fig2.update_layout(**LAYOUT, height=CH_H, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True, config=CFG, theme=None)

        if not chd.empty and not chd["Persentase (%)"].isna().all():
            dom = chd.loc[chd["Persentase (%)"].idxmax()]
            close_card(
                f"🎯 <b>{dom['Channel']}</b> mendominasi "
                f"({dom['Persentase (%)']:.1f}%) perilaku pembelian."
            )
        else:
            close_card("Data tidak tersedia.")

# ===================================================================
# PAGE 3 — Efisiensi & Promo
# ===================================================================
elif page == "⚡ Efisiensi & Promo":
    col_l, col_r = st.columns(2)

    # ── Left: Revenue vs Margin combo ───────────────────────────────
    with col_l:
      with st.container(border=True):
        right_col = card_header("Efisiensi Pendapatan vs Margin")
        with right_col:
            grp = st.selectbox(
                "Top N",
                ["Top 5 Cabang", "Top 8 Cabang"],
                key="p3_topn",
                label_visibility="collapsed",
            )

        n_top = 5 if "5" in grp else 8
        if global_branch != "Semua Cabang":
            n_top = 1

        sc = (
            filtered_df.groupby("branch_name")[["total_revenue", "profit"]]
            .sum()
            .reset_index()
        )
        sc["margin"] = (sc["profit"] / sc["total_revenue"] * 100).round(1)
        sc = sc.sort_values("total_revenue", ascending=False).head(n_top)
        sc["Cabang"] = sc["branch_name"].str.replace("KopiSeru ", "")

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=sc["Cabang"],
                y=sc["total_revenue"],
                name="Pendapatan (Rp)",
                marker_color="#E8DCCF",
                marker_line_width=0,
                hovertemplate=(
                    "<b>%{x}</b><br>Revenue: Rp %{y:,.0f}<extra></extra>"
                ),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=sc["Cabang"],
                y=sc["margin"],
                name="Margin (%)",
                mode="lines+markers",
                yaxis="y2",
                line=dict(color="#5C3A2E", width=3),
                marker=dict(size=9, color="#5C3A2E"),
                hovertemplate="Margin: %{y}%<extra></extra>",
            )
        )
        fig.update_layout(
            **LAYOUT,
            height=CH_H,
            showlegend=True,
            legend=dict(
                orientation="h", y=1.14, x=0.5, xanchor="center", font_size=11
            ),
            yaxis=dict(showgrid=False, tickformat=".2s"),
            yaxis2=dict(
                showgrid=False, overlaying="y", side="right", ticksuffix="%"
            ),
            xaxis=dict(showgrid=False),
        )
        st.plotly_chart(fig, use_container_width=True, config=CFG, theme=None)

        if not sc.empty:
            hm = sc.loc[sc["margin"].idxmax(), "Cabang"]
            close_card(
                f"💡 Cabang <b>{hm}</b> mencetak Net Profit Margin paling efisien."
            )
        else:
            close_card("Data tidak tersedia.")

    # ── Right: Promo effectiveness ──────────────────────────────────
    with col_r:
      with st.container(border=True):
        right_col = card_header("Efektivitas Tipe Promo")
        with right_col:
            promo_metric = st.selectbox(
                "Metrik",
                ["Laba Bersih", "Pendapatan"],
                key="p3_promo_metric",
                label_visibility="collapsed",
            )

        pc = "profit" if promo_metric == "Laba Bersih" else "total_revenue"
        pt = (
            filtered_df[filtered_df["promo_active"] == True]  # noqa: E712
            .groupby("promo_type")[pc]
            .mean()
            .reset_index()
            .sort_values(pc, ascending=True)
        )

        fig2 = px.bar(
            pt,
            y="promo_type",
            x=pc,
            orientation="h",
            color=pc,
            color_continuous_scale=["#E8DCCF", "#5C3A2E"],
        )
        fig2.update_traces(marker_line_width=0)
        fig2.update_layout(
            **LAYOUT,
            height=CH_H,
            coloraxis_showscale=False,
            yaxis=dict(title=""),
            xaxis=dict(
                title=f"Rata-rata {promo_metric} (Rp)", tickformat=".2s"
            ),
        )
        st.plotly_chart(fig2, use_container_width=True, config=CFG, theme=None)

        if not pt.empty:
            bp = pt.iloc[-1]["promo_type"]
            close_card(
                f"🚀 Promo <b>{bp}</b> memberikan rata-rata "
                f"{promo_metric.lower()} tertinggi."
            )
        else:
            close_card("💡 Tidak ada data promo aktif.")