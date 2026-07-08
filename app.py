"""
KopiSeru — Executive Dashboard
================================
Dashboard interaktif untuk Pemilik Bisnis / Pemegang Saham KopiSeru.
Menampilkan gambaran besar kesehatan bisnis: profitabilitas, pertumbuhan, dan efisiensi biaya.

Jalankan: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# ═══════════════════════════════════════════════════════════
#  PAGE CONFIG
# ═══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="KopiSeru — Executive Dashboard",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════
#  CUSTOM CSS — Dark Coffee Theme + Glassmorphism + No Scroll
# ═══════════════════════════════════════════════════════════
st.markdown(
    """
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* ══ NO SCROLL — viewport lock ══ */
section.main > div.block-container {
    padding: 1rem 2rem 0 2rem !important;
    max-height: 100vh;
    overflow: hidden !important;
}
.stAppViewContainer, .main {
    overflow: hidden !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stHeader"] { display: none; }
[data-testid="stToolbar"] { display: none; }
[data-testid="stDecoration"] { display: none; }

/* ═══ SIDEBAR ═══ */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1C1410 0%, #100C09 100%);
    border-right: 1px solid rgba(212, 165, 116, 0.12);
}
section[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.2rem;
}

/* Sidebar title */
section[data-testid="stSidebar"] h2 {
    color: #D4A574 !important;
    font-weight: 800 !important;
    letter-spacing: -0.5px;
}

/* ═══ KPI METRIC CARDS (Glassmorphism) ═══ */
[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(50, 38, 28, 0.75) 0%, rgba(28, 20, 14, 0.55) 100%);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(212, 165, 116, 0.18);
    border-radius: 14px;
    padding: 14px 18px;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.25);
    transition: transform 0.28s cubic-bezier(.4,0,.2,1),
                border-color 0.28s ease,
                box-shadow 0.28s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    border-color: rgba(212, 165, 116, 0.45);
    box-shadow: 0 8px 36px rgba(212, 165, 116, 0.10);
}

[data-testid="stMetricLabel"] {
    color: #9E8E7E !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}
[data-testid="stMetricValue"] {
    color: #FAF5F0 !important;
    font-weight: 700 !important;
    font-size: 1.3rem !important;
}
[data-testid="stMetricDelta"] {
    font-size: 0.72rem !important;
    font-weight: 500 !important;
}

/* ═══ DIVIDER ═══ */
hr {
    border-color: rgba(212, 165, 116, 0.12) !important;
    margin: 0.5rem 0 !important;
}

/* ═══ MULTISELECT TAGS ═══ */
.stMultiSelect [data-baseweb="tag"] {
    background-color: rgba(212, 165, 116, 0.18) !important;
    border: 1px solid rgba(212, 165, 116, 0.25) !important;
    color: #D4A574 !important;
}
.stMultiSelect [data-baseweb="tag"] span {
    color: #D4A574 !important;
}

/* ═══ RADIO NAV ═══ */
section[data-testid="stSidebar"] .stRadio [role="radiogroup"] {
    gap: 6px;
}

/* ═══ CAPTION ═══ */
section[data-testid="stSidebar"] .stCaption {
    color: #7A6A5A !important;
}
</style>
""",
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════════════════════
#  DATA LOADING (cached)
# ═══════════════════════════════════════════════════════════
@st.cache_data
def load_data():
    """Load and prepare dataset_final.csv."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(script_dir, "dataset_final.csv")
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    df["profit"] = df["total_revenue"] - df["operating_cost"]
    df["year"] = df["date"].dt.year
    df["month_start"] = df["date"].dt.to_period("M").dt.to_timestamp()
    return df


df_all = load_data()


# ═══════════════════════════════════════════════════════════
#  SIDEBAR — Navigation + Filters
# ═══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ☕ KopiSeru")
    st.caption("Executive Dashboard · 2021–2023")
    st.divider()

    # ── Page Navigation ──
    page = st.radio(
        "Navigasi",
        ["📊 Overview Bisnis", "🏪 Detail Cabang"],
        index=0,
        label_visibility="collapsed",
    )
    st.divider()

    # ── Filters ──
    st.markdown("##### 🔍 Filter Data")

    sel_years = st.multiselect(
        "📅 Tahun",
        sorted(df_all["year"].unique()),
        default=sorted(df_all["year"].unique()),
    )

    sel_cities = st.multiselect(
        "🏙️ Kota",
        sorted(df_all["branch_city"].unique()),
        default=sorted(df_all["branch_city"].unique()),
    )

    sel_types = st.multiselect(
        "🏢 Tipe Cabang",
        sorted(df_all["branch_type"].unique()),
        default=sorted(df_all["branch_type"].unique()),
    )

    # ── Sidebar footer ──
    st.divider()
    st.caption(
        f"📋 Data: {df_all['date'].min().strftime('%d %b %Y')} — "
        f"{df_all['date'].max().strftime('%d %b %Y')}"
    )
    st.caption(f"🏪 Total cabang: {df_all['branch_id'].nunique()} | 🌆 {df_all['branch_city'].nunique()} kota")


# ═══════════════════════════════════════════════════════════
#  FILTER APPLICATION
# ═══════════════════════════════════════════════════════════
if not sel_years or not sel_cities or not sel_types:
    st.warning("⚠️ Pilih minimal satu opsi di setiap filter pada sidebar.")
    st.stop()

mask = (
    df_all["year"].isin(sel_years)
    & df_all["branch_city"].isin(sel_cities)
    & df_all["branch_type"].isin(sel_types)
)
df = df_all[mask].copy()

if df.empty:
    st.warning("⚠️ Tidak ada data untuk kombinasi filter yang dipilih.")
    st.stop()


# ═══════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════
def rp(v):
    """Format number as Rupiah with SI suffix."""
    if abs(v) >= 1e12:
        return f"Rp {v / 1e12:.1f}T"
    if abs(v) >= 1e9:
        return f"Rp {v / 1e9:.1f}M"
    if abs(v) >= 1e6:
        return f"Rp {v / 1e6:.0f}Jt"
    if abs(v) >= 1e3:
        return f"Rp {v / 1e3:.0f}Rb"
    return f"Rp {v:.0f}"


def fmt(v):
    """Format large number with SI suffix."""
    if abs(v) >= 1e6:
        return f"{v / 1e6:.1f}M"
    if abs(v) >= 1e3:
        return f"{v / 1e3:.1f}K"
    return f"{v:,.0f}"


def yoy_delta(col, agg="sum"):
    """Calculate Year-over-Year delta for the latest selected year vs previous."""
    if not sel_years:
        return None
    latest = max(sel_years)
    prev = latest - 1
    curr_mask = mask & (df_all["year"] == latest)
    prev_mask = (
        (df_all["year"] == prev)
        & df_all["branch_city"].isin(sel_cities)
        & df_all["branch_type"].isin(sel_types)
    )
    c = df_all.loc[curr_mask, col].agg(agg)
    p = df_all.loc[prev_mask, col].agg(agg)
    if p and p != 0:
        pct = (c - p) / abs(p) * 100
        return f"{pct:+.1f}% vs {prev}"
    return None


# ═══════════════════════════════════════════════════════════
#  PLOTLY DEFAULTS
# ═══════════════════════════════════════════════════════════
BASE_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Plus Jakarta Sans, sans-serif", color="#9E8E7E", size=12),
    margin=dict(l=8, r=8, t=44, b=8),
    hoverlabel=dict(
        bgcolor="rgba(30, 22, 16, 0.96)",
        bordercolor="#D4A574",
        font=dict(family="Plus Jakarta Sans", size=13, color="#F5E6D3"),
    ),
)
PCFG = dict(displayModeBar=False, responsive=True)
CHART_H = 320  # chart height in px — sized to fit viewport without scroll


# ═══════════════════════════════════════════════════════════
#  PAGE 1 — OVERVIEW BISNIS
# ═══════════════════════════════════════════════════════════
if page == "📊 Overview Bisnis":

    # ── Title ──
    st.markdown(
        f"<h3 style='color:#D4A574; margin:0 0 2px 0; font-weight:800; letter-spacing:-0.5px'>"
        f"📊 Overview Bisnis KopiSeru</h3>"
        f"<p style='color:#7A6A5A; font-size:0.8rem; margin:0 0 10px 0'>"
        f"Periode {min(sel_years)}–{max(sel_years)} · {len(sel_cities)} kota · "
        f"{df['branch_id'].nunique()} cabang aktif</p>",
        unsafe_allow_html=True,
    )

    # ── KPI Row (5 cards) ──
    total_rev = df["total_revenue"].sum()
    total_prof = df["profit"].sum()
    margin_pct = (total_prof / total_rev * 100) if total_rev else 0
    total_trx = int(df["total_transactions"].sum())
    avg_ticket = df["avg_ticket_size"].mean()
    avg_csat = df["customer_satisfaction"].mean()

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("💰 Total Revenue", rp(total_rev), yoy_delta("total_revenue"))
    k2.metric("📈 Net Profit", rp(total_prof), f"Margin {margin_pct:.1f}%")
    k3.metric("🧾 Total Transaksi", fmt(total_trx), yoy_delta("total_transactions"))
    k4.metric("🎫 Avg Ticket Size", rp(avg_ticket), yoy_delta("avg_ticket_size", "mean"))
    k5.metric("⭐ Kepuasan", f"{avg_csat:.2f}/5", yoy_delta("customer_satisfaction", "mean"))

    # ── Spacer ──
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # ── Chart Row ──
    col_line, col_bar = st.columns([3, 2])

    # ── LINE CHART: Tren Revenue Bulanan ──
    with col_line:
        monthly = (
            df.groupby("month_start")
            .agg(
                revenue=("total_revenue", "sum"),
                profit=("profit", "sum"),
                trx=("total_transactions", "sum"),
            )
            .reset_index()
            .sort_values("month_start")
        )

        fig_line = go.Figure()

        # Subtle area fill
        fig_line.add_trace(
            go.Scatter(
                x=monthly["month_start"],
                y=monthly["revenue"],
                fill="tozeroy",
                fillcolor="rgba(212, 165, 116, 0.07)",
                line=dict(width=0),
                showlegend=False,
                hoverinfo="skip",
            )
        )

        # Main line
        fig_line.add_trace(
            go.Scatter(
                x=monthly["month_start"],
                y=monthly["revenue"],
                mode="lines+markers",
                line=dict(color="#D4A574", width=2.5, shape="spline"),
                marker=dict(
                    size=5,
                    color="#D4A574",
                    line=dict(width=1.5, color="#1C1410"),
                ),
                customdata=monthly[["profit", "trx"]].values,
                hovertemplate=(
                    "<b>%{x|%B %Y}</b><br><br>"
                    "💰 Revenue: <b>Rp %{y:,.0f}</b><br>"
                    "📈 Profit: Rp %{customdata[0]:,.0f}<br>"
                    "🧾 Transaksi: %{customdata[1]:,.0f}<br>"
                    "<extra></extra>"
                ),
                showlegend=False,
            )
        )

        fig_line.update_layout(
            **BASE_LAYOUT,
            height=CHART_H,
            title=dict(
                text="📈 Tren Revenue Bulanan",
                font=dict(size=14, color="#D4A574"),
            ),
            xaxis=dict(
                showgrid=False,
                dtick="M3",
                tickformat="%b '%y",
                tickfont=dict(size=10),
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="rgba(212, 165, 116, 0.06)",
                tickprefix="Rp ",
                separatethousands=True,
                tickfont=dict(size=10),
            ),
        )
        st.plotly_chart(fig_line, use_container_width=True, config=PCFG)

    # ── BAR CHART: Top 10 Cabang ──
    with col_bar:
        branch_rev = (
            df.groupby(["branch_name", "branch_city", "branch_type"])
            .agg(
                revenue=("total_revenue", "sum"),
                profit=("profit", "sum"),
                csat=("customer_satisfaction", "mean"),
            )
            .reset_index()
            .nlargest(10, "revenue")
            .sort_values("revenue")
        )
        short_names = branch_rev["branch_name"].str.replace(
            "KopiSeru ", "", regex=False
        )

        fig_bar = go.Figure(
            go.Bar(
                y=short_names,
                x=branch_rev["revenue"],
                orientation="h",
                marker=dict(
                    color=branch_rev["revenue"].values,
                    colorscale=[[0, "#6F4E37"], [1, "#D4A574"]],
                    cornerradius=4,
                ),
                customdata=branch_rev[
                    ["branch_city", "branch_type", "profit", "csat"]
                ].values,
                hovertemplate=(
                    "<b>KopiSeru %{y}</b><br><br>"
                    "🏙️ %{customdata[0]} · %{customdata[1]}<br>"
                    "💰 Revenue: <b>Rp %{x:,.0f}</b><br>"
                    "📈 Profit: Rp %{customdata[2]:,.0f}<br>"
                    "⭐ Kepuasan: %{customdata[3]:.1f}/5<br>"
                    "<extra></extra>"
                ),
            )
        )

        fig_bar.update_layout(
            **BASE_LAYOUT,
            height=CHART_H,
            title=dict(
                text="🏆 Top 10 Cabang (Revenue)",
                font=dict(size=14, color="#D4A574"),
            ),
            xaxis=dict(
                showgrid=True,
                gridcolor="rgba(212, 165, 116, 0.06)",
                tickprefix="Rp ",
                separatethousands=True,
                tickfont=dict(size=10),
            ),
            yaxis=dict(showgrid=False, tickfont=dict(size=10)),
        )
        st.plotly_chart(fig_bar, use_container_width=True, config=PCFG)


# ═══════════════════════════════════════════════════════════
#  PAGE 2 — DETAIL CABANG
# ═══════════════════════════════════════════════════════════
elif page == "🏪 Detail Cabang":

    # ── Title ──
    st.markdown(
        "<h3 style='color:#D4A574; margin:0 0 2px 0; font-weight:800; letter-spacing:-0.5px'>"
        "🏪 Detail Performa Cabang</h3>"
        "<p style='color:#7A6A5A; font-size:0.8rem; margin:0 0 10px 0'>"
        "Analisis performa per kota & distribusi channel penjualan</p>",
        unsafe_allow_html=True,
    )

    # ── KPI Row (4 cards) ──
    n_branches = df["branch_id"].nunique()
    avg_rev_branch = df.groupby("branch_id")["total_revenue"].sum().mean()
    best_type = df.groupby("branch_type")["profit"].sum().idxmax()
    total_cups = int(df["total_cups_sold"].sum())

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("🏪 Jumlah Cabang Aktif", n_branches)
    k2.metric("💰 Avg Revenue / Cabang", rp(avg_rev_branch))
    k3.metric("🏆 Tipe Paling Profitable", best_type)
    k4.metric("☕ Total Cup Terjual", fmt(total_cups))

    # ── Spacer ──
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # ── Chart Row ──
    col_city, col_channel = st.columns([3, 2])

    # ── BAR CHART: Revenue per Kota ──
    with col_city:
        city_data = (
            df.groupby("branch_city")
            .agg(
                revenue=("total_revenue", "sum"),
                profit=("profit", "sum"),
                branches=("branch_id", "nunique"),
                csat=("customer_satisfaction", "mean"),
            )
            .reset_index()
            .sort_values("revenue")
        )

        fig_city = go.Figure(
            go.Bar(
                y=city_data["branch_city"],
                x=city_data["revenue"],
                orientation="h",
                marker=dict(
                    color=city_data["revenue"].values,
                    colorscale=[[0, "#6F4E37"], [0.5, "#C08552"], [1, "#D4A574"]],
                    cornerradius=4,
                ),
                customdata=city_data[["profit", "branches", "csat"]].values,
                hovertemplate=(
                    "<b>%{y}</b><br><br>"
                    "💰 Revenue: <b>Rp %{x:,.0f}</b><br>"
                    "📈 Profit: Rp %{customdata[0]:,.0f}<br>"
                    "🏪 Jumlah Cabang: %{customdata[1]}<br>"
                    "⭐ Kepuasan Rata-rata: %{customdata[2]:.1f}/5<br>"
                    "<extra></extra>"
                ),
            )
        )

        fig_city.update_layout(
            **BASE_LAYOUT,
            height=CHART_H,
            title=dict(
                text="🏙️ Revenue per Kota",
                font=dict(size=14, color="#D4A574"),
            ),
            xaxis=dict(
                showgrid=True,
                gridcolor="rgba(212, 165, 116, 0.06)",
                tickprefix="Rp ",
                separatethousands=True,
                tickfont=dict(size=10),
            ),
            yaxis=dict(showgrid=False, tickfont=dict(size=11)),
        )
        st.plotly_chart(fig_city, use_container_width=True, config=PCFG)

    # ── DONUT CHART: Distribusi Channel ──
    with col_channel:
        ch_pct = pd.DataFrame(
            {
                "Channel": ["🍽️ Dine-in", "🛵 Delivery", "🥤 Takeaway"],
                "Pct": [
                    df["dine_in_percent"].mean(),
                    df["delivery_percent"].mean(),
                    df["takeaway_percent"].mean(),
                ],
            }
        )

        fig_donut = go.Figure(
            go.Pie(
                labels=ch_pct["Channel"],
                values=ch_pct["Pct"],
                hole=0.58,
                marker=dict(
                    colors=["#D4A574", "#8B6914", "#F5DEB3"],
                    line=dict(color="#1C1410", width=2),
                ),
                textinfo="label+percent",
                textfont=dict(size=12, color="#FAF5F0"),
                hovertemplate=(
                    "<b>%{label}</b><br><br>"
                    "Proporsi: <b>%{percent}</b><br>"
                    "Rata-rata: %{value:.1f}%<br>"
                    "<extra></extra>"
                ),
                rotation=90,
            )
        )

        fig_donut.update_layout(
            **BASE_LAYOUT,
            height=CHART_H,
            showlegend=False,
            title=dict(
                text="📊 Distribusi Channel Penjualan",
                font=dict(size=14, color="#D4A574"),
            ),
            annotations=[
                dict(
                    text="Channel",
                    x=0.5,
                    y=0.5,
                    font=dict(size=13, color="#9E8E7E", family="Plus Jakarta Sans"),
                    showarrow=False,
                )
            ],
        )
        st.plotly_chart(fig_donut, use_container_width=True, config=PCFG)
