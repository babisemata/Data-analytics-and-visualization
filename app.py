"""
KopiSeru — Executive Dashboard (Redesigned)
=============================================
Single-page executive dashboard with:
- NO sidebar – horizontal filter bar instead
- KPI row with accent colors & non-overlapping icons
- Dropdown page navigation in filter bar
- Per-chart local filters on the right of each chart title
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
        return f"Rp {v/1e6:.0f} Juta"
    if abs(v) >= 1e3:
        return f"Rp {v/1e3:.0f} Ribu"
    return f"Rp {v:,.0f}"


def pct(v: float) -> str:
    return f"{v:.1f}%"


DF = load_data()

# -------------------------------------------------------------------
# CSS — Coffee Executive Theme (Redesigned)
# -------------------------------------------------------------------
st.markdown(
    r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
    --bg:       #F0EBE3;
    --card:     #FFFFFF;
    --text:     #2A1A14;
    --muted:    #7C6154;
    --line:     #D7C9BC;
    --brown:    #5C3A2E;
    --cream:    #FBF7F2;
    --accent-1: #6D4534;
    --accent-2: #2E7D4F;
    --accent-3: #C2762B;
    --accent-4: #3A6B8C;
    --shadow:   0 2px 12px rgba(63,42,31,.08);
    --shadow-lg: 0 4px 24px rgba(63,42,31,.10);
}

/* ── Base ───────────────────────────────────────── */
html, body, .stApp, .main, .block-container {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background: var(--bg) !important;
}
.stApp, .main {
    overflow-y: auto !important;
}
.block-container {
    max-width: 1440px !important;
    padding: 0rem 2.5rem 0rem 2.5rem !important;
}

/* ── Gaps between streamlit blocks ──────────────── */
div[data-testid="stVerticalBlock"] { gap: 0.75rem !important; }
div[data-testid="stHorizontalBlock"] { gap: 1.2rem !important; }

/* ── Hide sidebar completely ────────────────────── */
section[data-testid="stSidebar"] {
    display: none !important;
}
[data-testid="collapsedControl"] {
    display: none !important;
}

/* ── Header bar / toolbar ──────────────────────── */
#MainMenu, footer, [data-testid="stToolbar"] { display: none !important; }
header[data-testid="stHeader"] {
    background: transparent !important;
    backdrop-filter: none !important;
}

/* ── Typography ─────────────────────────────────── */
.hero-title {
    color: var(--text);
    font-size: 1.6rem;
    font-weight: 800;
    margin: 0;
    line-height: 1.15;
}
.hero-sub {
    color: var(--muted);
    font-size: 0.88rem;
    font-weight: 600;
    margin: 2px 0 0 0;
}

/* ── Filter bar label styling ──────────────────── */
.filter-label {
    font-size: .7rem;
    font-weight: 800;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: .4px;
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 5px;
}

/* ── Selectbox / Dropdown fixes ─────────────────── */
/* Outer container */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    min-height: 36px !important;
    max-height: 38px !important;
    border-radius: 10px !important;
    border: 1.5px solid var(--line) !important;
    background: #FFFFFF !important;
    box-shadow: none !important;
    font-size: .84rem !important;
    padding: 0 !important;
}

/* ★ Force all selectbox text to dark brown */
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
div[data-baseweb="popover"],
div[data-baseweb="popover"] * {
    color: var(--text) !important;
}
div[role="listbox"] li,
div[role="listbox"] li * {
    color: var(--text) !important;
    background-color: #ffffff !important;
}
div[role="listbox"] li:hover,
div[role="listbox"] li:hover * {
    background-color: var(--cream) !important;
}
ul[data-baseweb="menu"] li,
ul[data-baseweb="menu"] li * {
    color: var(--text) !important;
    background-color: #ffffff !important;
}
ul[data-baseweb="menu"] li:hover,
ul[data-baseweb="menu"] li:hover * {
    background-color: var(--cream) !important;
}
/* Dropdown arrow icon */
div[data-baseweb="select"] svg {
    fill: var(--muted) !important;
}

/* ── KPI cards ──────────────────────────────────── */
.kpi-card {
    background: var(--card);
    border: 1.5px solid var(--line);
    border-radius: 16px;
    padding: 20px 22px 16px 22px;
    min-height: 130px;
    box-shadow: var(--shadow);
    position: relative;
    text-align: left;
    transition: box-shadow .2s ease, transform .2s ease;
    overflow: hidden;
}
.kpi-card:hover {
    box-shadow: var(--shadow-lg);
    transform: translateY(-2px);
}
.kpi-title {
    font-size: .7rem;
    font-weight: 800;
    margin: 0 0 8px 0;
    text-transform: uppercase;
    letter-spacing: .6px;
}
.kpi-value {
    color: var(--text);
    font-size: 1.55rem;
    font-weight: 800;
    margin: 0;
    line-height: 1.1;
}
.kpi-delta {
    font-size: .75rem;
    font-weight: 700;
    margin: 8px 0 0 0;
    display: flex;
    align-items: center;
    gap: 4px;
}
.kpi-delta-positive { color: #1B8F2C; }
.kpi-delta-negative { color: #C62828; }
.kpi-delta-label {
    color: var(--muted);
    font-weight: 600;
    font-size: .72rem;
}
.kpi-icon {
    position: absolute;
    top: 16px;
    right: 16px;
    width: 38px;
    height: 38px;
    opacity: .75;
    border-radius: 10px;
    padding: 6px;
}

/* ── Chart card container ──────────────────────── */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--card) !important;
    border: 1.5px solid var(--line) !important;
    border-radius: 16px !important;
    box-shadow: var(--shadow-lg) !important;
    padding: 20px 22px 14px 22px !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] > div {
    background: transparent !important;
}
.chart-title {
    color: var(--text);
    font-size: 1rem;
    font-weight: 800;
    margin: 0;
    line-height: 1.2;
    display: flex;
    align-items: center;
    gap: 6px;
}
.chart-note {
    background: var(--cream);
    border: 1.5px solid #EDE3D8;
    border-radius: 10px;
    padding: 10px 16px;
    margin-top: 8px;
    color: var(--brown);
    font-size: .8rem;
    font-weight: 600;
    line-height: 1.45;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    text-align: center;
}

/* ── Plotly modebar hide ───────────────────────── */
.js-plotly-plot .plotly .modebar { display: none !important; }

/* ── Spacer utility ────────────────────────────── */
.spacer-sm { height: 8px; }
.spacer-md { height: 18px; }
.spacer-lg { height: 16px; }

/* ── Global filter selectbox labels ────────────── */
.stSelectbox label {
    font-size: .72rem !important;
    font-weight: 800 !important;
    color: var(--muted) !important;
    text-transform: uppercase !important;
    letter-spacing: .4px !important;
    margin-bottom: 2px !important;
}

/* Hide labels inside chart cards (per-chart filters) */
div[data-testid="stVerticalBlockBorderWrapper"] .stSelectbox label {
    display: none !important;
}

/* ── Data badge in header ──────────────────────── */
.data-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--card);
    border: 1.5px solid var(--line);
    border-radius: 10px;
    padding: 6px 14px;
    font-size: .78rem;
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
# Header & Filter Bar
# -------------------------------------------------------------------
# Available filter values
all_years = sorted(DF["year"].unique().tolist())
year_options = ["Semua Tahun"] + [str(y) for y in all_years]
branches = ["Semua Cabang"] + sorted(DF["branch_name"].unique().tolist())
branch_types = ["Semua Tipe"] + sorted(DF["branch_type"].unique().tolist())
pages = ["☕ Pertumbuhan", "📍 Lokasi & Channel", "⚡ Efisiensi & Promo"]

h_left, h_spacer, h_right = st.columns([0.33, 0.05, 0.62], vertical_alignment="center")

with h_left:
    # Logo + title side by side
    logo_col, title_col = st.columns([0.15, 0.85], vertical_alignment="center")
    with logo_col:
        if logo_b64:
            st.markdown(
                f'<img src="{logo_b64}" style="width:80px; height:80px; border-radius:10px; object-fit:contain;">',
                unsafe_allow_html=True,
            )
    with title_col:
        st.markdown(
            '<div class="hero-title" style="font-size: 1.4rem;">KopiSeru Executive Board</div>'
            '<div class="hero-sub" style="font-size: 0.8rem;">Ringkasan Performa & Profitabilitas Bisnis</div>',
            unsafe_allow_html=True,
        )

with h_right:
    fc1, fc2, fc3, fc4, fc5 = st.columns([1.1, 1.1, 0.9, 1.1, 1.0])

    with fc1:
        page = st.selectbox(
            "Tampilan Dashboard",
            pages,
            key="page_selector",
        )
    with fc2:
        sel_year = st.selectbox(
            "Rentang Waktu",
            year_options,
            key="filter_year",
        )
    with fc3:
        sel_period = st.selectbox(
            "Periode",
            ["Bulanan", "Tahunan"],
            key="filter_period",
        )
    with fc4:
        global_branch = st.selectbox(
            "Cabang",
            branches,
            key="filter_branch",
        )
    with fc5:
        sel_branch_type = st.selectbox(
            "Tipe Lokasi",
            branch_types,
            key="filter_branch_type",
        )

# -------------------------------------------------------------------
# Apply global filters
# -------------------------------------------------------------------
filtered_df = DF.copy()

if sel_year != "Semua Tahun":
    filtered_df = filtered_df[filtered_df["year"] == int(sel_year)]

if global_branch != "Semua Cabang":
    filtered_df = filtered_df[filtered_df["branch_name"] == global_branch]

if sel_branch_type != "Semua Tipe":
    filtered_df = filtered_df[filtered_df["branch_type"] == sel_branch_type]

# -------------------------------------------------------------------
# KPI Row
# -------------------------------------------------------------------
st.markdown('<div class="spacer-md"></div>', unsafe_allow_html=True)

total_revenue = float(filtered_df["total_revenue"].sum())
total_profit = float(
    (filtered_df["total_revenue"] - filtered_df["operating_cost"]).sum()
)
npm = (total_profit / total_revenue * 100) if total_revenue else 0.0
total_transactions = float(filtered_df["total_transactions"].sum())

# Delta calculation — compare with previous period
if sel_year != "Semua Tahun":
    current_year = int(sel_year)
    prev_year = current_year - 1
else:
    current_year = int(DF["year"].max())
    prev_year = current_year - 1


def year_sum(df, col, year):
    return float(df.loc[df["year"] == year, col].sum())


# Build a "previous" filtered_df to compute deltas
prev_df = DF.copy()
if global_branch != "Semua Cabang":
    prev_df = prev_df[prev_df["branch_name"] == global_branch]
if sel_branch_type != "Semua Tipe":
    prev_df = prev_df[prev_df["branch_type"] == sel_branch_type]

prev_rev = year_sum(prev_df, "total_revenue", prev_year)
prev_prof = float(
    (
        prev_df.loc[prev_df["year"] == prev_year, "total_revenue"]
        - prev_df.loc[prev_df["year"] == prev_year, "operating_cost"]
    ).sum()
)
prev_trx = year_sum(prev_df, "total_transactions", prev_year)
prev_npm = (prev_prof / prev_rev * 100) if prev_rev else npm


def delta_text(curr, prev, is_pct=False):
    if prev == 0:
        return None, True
    if is_pct:
        diff = curr - prev
        return f"{abs(diff):.1f} pt", diff >= 0
    diff_pct = (curr - prev) / prev * 100
    return f"{abs(diff_pct):.1f}%", diff_pct >= 0


d_rev, d_rev_pos = delta_text(total_revenue, prev_rev)
d_prof, d_prof_pos = delta_text(total_profit, prev_prof)
d_trx, d_trx_pos = delta_text(total_transactions, prev_trx)
d_npm, d_npm_pos = delta_text(npm, prev_npm, is_pct=True)


def kpi_html(title, value, icon_b64_src, delta, is_positive, accent_color):
    """Render a single KPI card with accent-colored title and delta."""
    arrow = "▲" if is_positive else "▼"
    delta_class = "kpi-delta-positive" if is_positive else "kpi-delta-negative"

    delta_html = ""
    if delta:
        delta_html = (
            f'<div class="kpi-delta">'
            f'<span class="{delta_class}">{arrow} {delta}</span>'
            f'<span class="kpi-delta-label">vs periode sebelumnya</span>'
            f"</div>"
        )

    icon_tag = ""
    if icon_b64_src:
        icon_tag = (
            f'<div style="position:absolute; top:14px; right:14px; '
            f"width:42px; height:42px; border-radius:12px; "
            f"background:{accent_color}15; display:flex; "
            f'align-items:center; justify-content:center;">'
            f'<img src="{icon_b64_src}" style="width:24px; height:24px; opacity:.85;">'
            f"</div>"
        )

    return f"""<div class="kpi-card">
<div class="kpi-title" style="color:{accent_color};">{title}</div>
<div class="kpi-value">{value}</div>
{delta_html}
{icon_tag}
</div>"""


trx_fmt = (
    f"{total_transactions/1e6:.2f} Jt"
    if total_transactions >= 1e6
    else f"{total_transactions:,.0f}"
)

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(
        kpi_html(
            "Total Pendapatan",
            fmt_rp(total_revenue),
            money_b64,
            d_rev,
            d_rev_pos,
            "#6D4534",
        ),
        unsafe_allow_html=True,
    )

with k2:
    st.markdown(
        kpi_html(
            "Laba Bersih (Net)",
            fmt_rp(total_profit),
            line_b64,
            d_prof,
            d_prof_pos,
            "#2E7D4F",
        ),
        unsafe_allow_html=True,
    )

with k3:
    st.markdown(
        kpi_html(
            "Net Profit Margin",
            pct(npm),
            pie_b64,
            d_npm,
            d_npm_pos,
            "#C2762B",
        ),
        unsafe_allow_html=True,
    )

with k4:
    st.markdown(
        kpi_html(
            "Total Transaksi",
            trx_fmt,
            people_b64,
            d_trx,
            d_trx_pos,
            "#3A6B8C",
        ),
        unsafe_allow_html=True,
    )

# -------------------------------------------------------------------
# Spacing before charts
# -------------------------------------------------------------------
st.markdown('<div class="spacer-lg"></div>', unsafe_allow_html=True)

# -------------------------------------------------------------------
# Plot defaults
# -------------------------------------------------------------------
CH_H = 300
LAYOUT = dict(
    template="plotly_white",
    margin=dict(l=10, r=10, t=10, b=10),
    paper_bgcolor="rgba(255,255,255,0)",
    plot_bgcolor="rgba(255,255,255,1)",
    font=dict(family="Plus Jakarta Sans", color="#4A352C", size=12),
    hoverlabel=dict(
        bgcolor="#FFFFFF",
        bordercolor="#C49A6C",
        font=dict(family="Plus Jakarta Sans", color="#4A352C", size=13),
    ),
)
CFG = dict(displayModeBar=False)
palette = ["#5C3A2E", "#8B5A2B", "#C49A6C", "#A1887F", "#D7CCC8", "#E6DCCF"]


def close_card(note: str):
    """Render insight note at the bottom of a chart card."""
    st.markdown(
        f'<div class="chart-note">{note}</div>',
        unsafe_allow_html=True,
    )


def card_header(title, filter_ratio=0.28):
    """Render chart title on the left & return the right column for the filter."""
    left_col, right_col = st.columns(
        [1 - filter_ratio, filter_ratio], vertical_alignment="center"
    )
    with left_col:
        st.markdown(
            f'<div class="chart-title">{title} <span style="color:#C49A6C; font-size:.85rem; cursor:help;" title="Hover pada chart untuk detail">ⓘ</span></div>',
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
            right_col = card_header("Tren Pendapatan Bulanan", filter_ratio=0.35)
            with right_col:
                metric_sel = st.selectbox(
                    "Metrik",
                    ["Pendapatan (Rp)", "Laba Bersih (Rp)"],
                    key="p1_metric",
                    label_visibility="collapsed",
                )

            col = (
                "total_revenue"
                if metric_sel == "Pendapatan (Rp)"
                else "profit"
            )
            metric_label = (
                "Pendapatan"
                if metric_sel == "Pendapatan (Rp)"
                else "Laba Bersih"
            )

            if sel_period == "Tahunan":
                d = (
                    filtered_df.groupby("year", as_index=False)[col]
                    .sum()
                    .sort_values("year")
                )
                x_col = "year"
                tick_fmt = "d"
                hover_fmt = "<b>%{x}</b><br>Rp %{y:,.0f}<extra></extra>"
            else:
                d = (
                    filtered_df.groupby("month", as_index=False)[col]
                    .sum()
                    .sort_values("month")
                )
                x_col = "month"
                tick_fmt = "%b %Y"
                hover_fmt = (
                    "<b>%{x|%b %Y}</b><br>Rp %{y:,.0f}<extra></extra>"
                )

            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=d[x_col],
                    y=d[col],
                    mode="lines",
                    line=dict(color="#5C3A2E", width=2.5, shape="spline"),
                    fill="tozeroy",
                    fillcolor="rgba(92,58,46,.06)",
                    hovertemplate=hover_fmt,
                    name=metric_label,
                )
            )
            fig.update_layout(**LAYOUT, height=CH_H, showlegend=False)
            fig.update_yaxes(
                showgrid=True,
                gridcolor="rgba(0,0,0,.07)",
                tickformat=".2s",
                title="",
            )
            fig.update_xaxes(
                showgrid=False,
                title="",
                tickangle=45 if sel_period != "Tahunan" else 0,
                tickformat=tick_fmt,
            )
            st.plotly_chart(
                fig, use_container_width=True, config=CFG, theme=None
            )

            if not d.empty:
                if sel_period == "Tahunan":
                    top_period = d.loc[d[col].idxmax(), "year"]
                    top_val = fmt_rp(d[col].max())
                    close_card(
                        f"📈 {metric_label} tertinggi pada tahun <b>{top_period}</b> sebesar <b>{top_val}</b>."
                    )
                else:
                    top_month = d.loc[d[col].idxmax(), "month"]
                    top_val = fmt_rp(d[col].max())
                    close_card(
                        f"📈 {metric_label} tertinggi di <b>{top_month.strftime('%B %Y')}</b> sebesar <b>{top_val}</b>."
                    )
            else:
                close_card("Data tidak tersedia untuk filter yang dipilih.")

    # ── Right chart: Branch performance multi-line ──────────────────
    with col_r:
        with st.container(border=True):
            right_col = card_header("Performa Penjualan per Cabang", filter_ratio=0.60)
            with right_col:
                fc_l, fc_r = st.columns(2)
                with fc_l:
                    branch_metric = st.selectbox(
                        "Metrik Cabang",
                        ["Pendapatan (Rp)", "Cups Sold"],
                        key="p1_branch_metric",
                        label_visibility="collapsed",
                    )
                with fc_r:
                    top_n = st.selectbox(
                        "Top N",
                        ["Top 5 Cabang", "Top 8 Cabang"],
                        key="p1_topn",
                        label_visibility="collapsed",
                    )

            n = 5 if "5" in top_n else 8
            b_col = (
                "total_revenue"
                if branch_metric == "Pendapatan (Rp)"
                else "total_cups_sold"
            )

            top_branches = (
                filtered_df.groupby("branch_name")[b_col]
                .sum()
                .sort_values(ascending=False)
                .head(n)
                .index.tolist()
            )

            d2 = (
                filtered_df[filtered_df["branch_name"].isin(top_branches)]
                .groupby("branch_name", as_index=False)[b_col]
                .sum()
                .sort_values(b_col, ascending=True)
            )

            d2["Cabang"] = d2["branch_name"].str.replace("KopiSeru ", "")

            fig2 = px.bar(
                d2,
                x=b_col,
                y="Cabang",
                orientation="h",
                color=b_col,
                color_continuous_scale=["#E8DCCF", "#5C3A2E"],
            )
            fig2.update_traces(
                hovertemplate="<b>%{y}</b><br>%{x:,.0f}<extra></extra>",
                marker_line_width=0,
                marker=dict(cornerradius=4),
            )
            fig2.update_layout(
                **LAYOUT,
                height=CH_H,
                coloraxis_showscale=False,
            )
            fig2.update_xaxes(
                title="",
                tickformat=".2s",
                showgrid=True,
                gridcolor="rgba(0,0,0,.07)",
            )
            fig2.update_yaxes(title="", showgrid=False)
            st.plotly_chart(
                fig2, use_container_width=True, config=CFG, theme=None
            )

            if top_branches:
                best_branch = top_branches[0].replace("KopiSeru ", "")
                close_card(
                    f"🏆 <b>{best_branch}</b> selalu menjadi kontributor {branch_metric.lower()} tertinggi."
                )
            else:
                close_card("Data tidak tersedia untuk filter yang dipilih.")

# ===================================================================
# PAGE 2 — Lokasi & Channel
# ===================================================================
elif page == "📍 Lokasi & Channel":
    col_l, col_r = st.columns(2)

    # ── Left: Revenue by branch type ────────────────────────────────
    with col_l:
        with st.container(border=True):
            right_col = card_header("Pendapatan per Tipe Lokasi", filter_ratio=0.40)
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
                marker=dict(cornerradius=4),
            )
            fig.update_layout(
                **LAYOUT, height=CH_H, coloraxis_showscale=False
            )
            fig.update_xaxes(
                title="",
                tickformat=".2s",
                showgrid=True,
                gridcolor="rgba(0,0,0,.07)",
            )
            fig.update_yaxes(title="", showgrid=False)
            st.plotly_chart(
                fig, use_container_width=True, config=CFG, theme=None
            )

            if not loc.empty:
                best_type = loc.iloc[-1]["branch_type"]
                best_val = fmt_rp(loc.iloc[-1]["total_revenue"])
                close_card(
                    f"📍 Tipe lokasi <b>{best_type}</b> menjadi penyumbang terbesar ({loc_agg.lower()}: <b>{best_val}</b>)."
                )
            else:
                close_card("Data tidak tersedia.")

    # ── Right: Channel donut ────────────────────────────────────────
    with col_r:
        with st.container(border=True):
            right_col = card_header("Distribusi Channel Penjualan", filter_ratio=0.40)
            with right_col:
                ch_metric = st.selectbox(
                    "Metrik",
                    ["Persentase (%)", "Total Revenue"],
                    key="p2_ch_metric",
                    label_visibility="collapsed",
                )

            d = filtered_df.copy()

            if ch_metric == "Persentase (%)":
                chd = pd.DataFrame(
                    {
                        "Channel": ["Dine-in", "Delivery", "Takeaway"],
                        "Value": [
                            d.dine_in_percent.mean(),
                            d.delivery_percent.mean(),
                            d.takeaway_percent.mean(),
                        ],
                    }
                )
                hover_tmpl = "<b>%{label}</b><br>%{value:.1f}%<extra></extra>"
            else:
                # Approximate: use percentages * revenue
                chd = pd.DataFrame(
                    {
                        "Channel": ["Dine-in", "Delivery", "Takeaway"],
                        "Value": [
                            (d["dine_in_percent"] / 100 * d["total_revenue"]).sum(),
                            (d["delivery_percent"] / 100 * d["total_revenue"]).sum(),
                            (d["takeaway_percent"] / 100 * d["total_revenue"]).sum(),
                        ],
                    }
                )
                hover_tmpl = "<b>%{label}</b><br>Rp %{value:,.0f}<extra></extra>"

            fig2 = px.pie(
                chd,
                values="Value",
                names="Channel",
                hole=0.55,
                color_discrete_sequence=["#5C3A2E", "#C49A6C", "#D7CCC8"],
            )
            fig2.update_traces(
                textposition="inside",
                textinfo="percent+label",
                textfont=dict(size=13, color="#FFFFFF"),
                hovertemplate=hover_tmpl,
            )
            fig2.update_layout(**LAYOUT, height=CH_H, showlegend=True,
                legend=dict(
                    orientation="h",
                    y=-0.08,
                    x=0.5,
                    xanchor="center",
                    font=dict(size=12),
                ),
            )
            st.plotly_chart(
                fig2, use_container_width=True, config=CFG, theme=None
            )

            if not chd.empty and not chd["Value"].isna().all():
                dom = chd.loc[chd["Value"].idxmax()]
                if ch_metric == "Persentase (%)":
                    close_card(
                        f"🎯 <b>{dom['Channel']}</b> mendominasi ({dom['Value']:.1f}%) perilaku pembelian."
                    )
                else:
                    close_card(
                        f"🎯 <b>{dom['Channel']}</b> menjadi channel dengan pendapatan tertinggi."
                    )
            else:
                close_card("Data tidak tersedia.")

# ===================================================================
# PAGE 3 — Efisiensi & Promo
# ===================================================================
elif page == "⚡ Efisiensi & Promo":
    col_l, col_r = st.columns(2)

    # ── Left: Biaya vs Pendapatan dual-line ─────────────────────────
    with col_l:
        with st.container(border=True):
            right_col = card_header("Efisiensi: Biaya vs Pendapatan", filter_ratio=0.35)
            with right_col:
                eff_period = st.selectbox(
                    "Periode",
                    ["Bulanan", "Tahunan"],
                    key="p3_period",
                    label_visibility="collapsed",
                )

            if eff_period == "Tahunan":
                eff = (
                    filtered_df.groupby("year", as_index=False)[
                        ["total_revenue", "operating_cost"]
                    ]
                    .sum()
                    .sort_values("year")
                )
                x_eff = "year"
                tick_eff = "d"
            else:
                eff = (
                    filtered_df.groupby("month", as_index=False)[
                        ["total_revenue", "operating_cost"]
                    ]
                    .sum()
                    .sort_values("month")
                )
                x_eff = "month"
                tick_eff = "%b %Y"

            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=eff[x_eff],
                    y=eff["total_revenue"],
                    mode="lines",
                    name="Pendapatan (Rp)",
                    line=dict(
                        color="#5C3A2E", width=2.5, shape="spline"
                    ),
                    hovertemplate="Pendapatan: Rp %{y:,.0f}<extra></extra>",
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=eff[x_eff],
                    y=eff["operating_cost"],
                    mode="lines",
                    name="Operating Cost (Rp)",
                    line=dict(
                        color="#C62828", width=2.5, dash="dot", shape="spline"
                    ),
                    hovertemplate="Biaya: Rp %{y:,.0f}<extra></extra>",
                )
            )
            fig.update_layout(
                **LAYOUT,
                height=CH_H,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    y=1.08,
                    x=0.5,
                    xanchor="center",
                    font_size=11,
                ),
            )
            fig.update_yaxes(
                showgrid=True,
                gridcolor="rgba(0,0,0,.07)",
                tickformat=".2s",
                title="",
            )
            fig.update_xaxes(
                showgrid=False,
                title="",
                tickangle=45 if eff_period != "Tahunan" else 0,
                tickformat=tick_eff,
            )
            st.plotly_chart(
                fig, use_container_width=True, config=CFG, theme=None
            )

            if not eff.empty:
                total_rev_eff = eff["total_revenue"].sum()
                total_cost_eff = eff["operating_cost"].sum()
                ratio = (
                    (total_cost_eff / total_rev_eff * 100)
                    if total_rev_eff
                    else 0
                )
                close_card(
                    f"💡 Biaya operasional terjaga stabil di <b>{ratio:.1f}%</b> dari total pendapatan."
                )
            else:
                close_card("Data tidak tersedia.")

    # ── Right: Distribusi Pendapatan per Kategori Produk ────────────
    with col_r:
        with st.container(border=True):
            right_col = card_header(
                "Distribusi Pendapatan per Kategori Produk", filter_ratio=0.40
            )
            with right_col:
                cat_metric = st.selectbox(
                    "Metrik",
                    ["Persentase (%)", "Total Revenue"],
                    key="p3_cat_metric",
                    label_visibility="collapsed",
                )

            # top_selling_category counts
            cat_counts = (
                filtered_df.groupby("top_selling_category")["total_revenue"]
                .sum()
                .reset_index()
                .sort_values("total_revenue", ascending=False)
            )

            if cat_metric == "Persentase (%)":
                cat_counts["pct"] = (
                    cat_counts["total_revenue"]
                    / cat_counts["total_revenue"].sum()
                    * 100
                )
                cat_fig = px.pie(
                    cat_counts,
                    values="pct",
                    names="top_selling_category",
                    hole=0.55,
                    color_discrete_sequence=[
                        "#5C3A2E",
                        "#8B5A2B",
                        "#C49A6C",
                        "#A1887F",
                        "#D7CCC8",
                        "#E6DCCF",
                    ],
                )
                cat_fig.update_traces(
                    textposition="inside",
                    textinfo="percent+label",
                    textfont=dict(size=11, color="#FFFFFF"),
                    hovertemplate="<b>%{label}</b><br>%{value:.1f}%<extra></extra>",
                )
            else:
                cat_fig = px.pie(
                    cat_counts,
                    values="total_revenue",
                    names="top_selling_category",
                    hole=0.55,
                    color_discrete_sequence=[
                        "#5C3A2E",
                        "#8B5A2B",
                        "#C49A6C",
                        "#A1887F",
                        "#D7CCC8",
                        "#E6DCCF",
                    ],
                )
                cat_fig.update_traces(
                    textposition="inside",
                    textinfo="percent+label",
                    textfont=dict(size=11, color="#FFFFFF"),
                    hovertemplate="<b>%{label}</b><br>Rp %{value:,.0f}<extra></extra>",
                )

            cat_fig.update_layout(
                **LAYOUT,
                height=CH_H,
                showlegend=True,
                legend=dict(
                    orientation="v",
                    y=0.5,
                    x=1.02,
                    title="",
                    font=dict(size=11),
                ),
            )
            st.plotly_chart(
                cat_fig, use_container_width=True, config=CFG, theme=None
            )

            if not cat_counts.empty:
                top_cat = cat_counts.iloc[0]["top_selling_category"]
                top_pct = (
                    cat_counts.iloc[0]["total_revenue"]
                    / cat_counts["total_revenue"].sum()
                    * 100
                )
                close_card(
                    f"☕ <b>{top_cat}</b> menjadi penyumbang pendapatan terbesar ({top_pct:.1f}%)."
                )
            else:
                close_card("Data tidak tersedia.")

# -------------------------------------------------------------------
# Footer
# -------------------------------------------------------------------
st.markdown('<div class="spacer-lg"></div>', unsafe_allow_html=True)
st.markdown(
    f'<div style="text-align:center; color:#B09A88; font-size:.75rem; font-weight:600; padding:8px 0 16px 0;">'
    f"KopiSeru Executive Dashboard • Data terakhir diperbarui: "
    f'{DF["date"].max().strftime("%d %B %Y")}'
    f"</div>",
    unsafe_allow_html=True,
)