"""
KopiSeru — Executive Dashboard
================================
Layout: No-scroll · 2 charts per page · Minimalist · Sidebar navigation
Reference: Executive Summary Focus
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os, base64

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
#  HELPERS
# ═══════════════════════════════════════════════════════════
@st.cache_data
def load_data():
    d = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(os.path.join(d, "dataset_final.csv"))
    df["date"] = pd.to_datetime(df["date"])
    df["profit"] = df["total_revenue"] - df["operating_cost"]
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
    return df

def img_b64(fn):
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "asset", fn)
    if os.path.exists(p):
        with open(p, "rb") as f:
            return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
    return ""

def fmt(v):
    if abs(v) >= 1e12: return f"Rp {v/1e12:.2f} Triliun"
    if abs(v) >= 1e9: return f"Rp {v/1e9:.2f} Miliar"
    if abs(v) >= 1e6: return f"Rp {v/1e6:.0f} Juta"
    return f"Rp {v:,.0f}"

DF = load_data()

# Chart constants (Height greatly increased since we only have 1 row of charts)
CH = 320 
LAYOUT_BASE = dict(
    template="plotly_white",
    margin=dict(l=5, r=5, t=10, b=5),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Plus Jakarta Sans", color="#4E342E", size=12),
    hoverlabel=dict(bgcolor="#FFF", bordercolor="#C49A6C", font=dict(color="#4E342E", size=13)),
)
CFG = dict(displayModeBar=False)
PAL = ["#4E342E", "#8B5A2B", "#C49A6C", "#D7CCC8", "#EFEBE9", "#A1887F"]

# ═══════════════════════════════════════════════════════════
#  CSS
# ═══════════════════════════════════════════════════════════
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* ── NO-SCROLL ── */
html,body,.stApp,.main,.block-container{
    overflow:hidden!important;max-height:100vh!important;
    font-family:'Plus Jakarta Sans',sans-serif!important;
}
.block-container{padding:1rem 2rem 0 2rem!important}
div[data-testid="stVerticalBlock"]>div{gap:0.4rem!important}
div[data-testid="stHorizontalBlock"]{gap:1rem!important}

/* Keep header transparent so sidebar toggle works, hide clutter */
[data-testid="stHeader"] {background:transparent!important; height:0px!important}
#MainMenu,footer,[data-testid="stToolbar"]{display:none!important}
.stApp{background:#F5F2ED!important}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#3E2723,#4E342E);border:none}
section[data-testid="stSidebar"] [data-testid="stSidebarContent"]{padding-top:1rem}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span{color:#D7C8B8!important;font-size:0.9rem!important}
section[data-testid="stSidebar"] hr{border-color:rgba(196,154,108,0.2)!important;margin:10px 0!important}
section[data-testid="stSidebar"] .stRadio>div{flex-direction:column;gap:4px;background:transparent;border:none;padding:0}
section[data-testid="stSidebar"] .stRadio label{padding:10px 16px;border-radius:8px;transition:0.2s}
section[data-testid="stSidebar"] .stRadio label:hover{background:rgba(196,154,108,0.15)}
section[data-testid="stSidebar"] .stRadio label[data-checked="true"]{background:#C49A6C!important}
section[data-testid="stSidebar"] .stRadio label[data-checked="true"] p{color:#FFF!important;font-weight:700!important}
section[data-testid="stSidebar"] .stRadio label>div:first-child{display:none}

/* ── COMPACT WIDGETS (Global Filters) ── */
.stSelectbox label{font-size:0.75rem!important;color:#8D6E53!important;margin-bottom:0px!important;min-height:0!important}
.stSelectbox>div>div{min-height:36px!important;font-size:0.85rem!important;border-radius:8px!important;}
.stSelectbox{margin-bottom:0!important}

/* ── KPI ── */
.kpi{background:#FFF;border-radius:12px;padding:16px 20px;border:1px solid #EDE8E1;position:relative;height:95px;box-shadow:0 4px 10px rgba(0,0,0,0.03)}
.kpi-l{font-size:0.75rem;color:#8D6E53;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin:0}
.kpi-v{font-size:1.6rem;font-weight:800;color:#2C1A12;margin:2px 0 0;line-height:1.1}
.kpi-d{font-size:0.7rem;font-weight:700;margin:4px 0 0}
.kpi-d.u{color:#2E7D32}.kpi-d.d{color:#C62828}
.kpi-i{position:absolute;top:16px;right:16px;width:32px;height:32px;opacity:0.8}

/* ── CHART CARD ── */
.cc{background:#FFF;border-radius:12px;padding:16px 20px;border:1px solid #EDE8E1;box-shadow:0 4px 10px rgba(0,0,0,0.03)}
.cc h4{font-size:0.95rem;font-weight:800;color:#2C1A12;margin:0 0 10px}
.cc-ins{font-size:0.75rem;color:#6D4C41;margin:12px 0 0;padding:8px 12px;background:#FDF8F3;border-radius:6px;line-height:1.4}

/* ── TABS (as pagination) ── */
.stTabs [data-baseweb="tab-list"]{gap:0;background:#FFF;border-radius:10px;border:1px solid #EDE8E1;padding:4px;margin-top:8px}
.stTabs [data-baseweb="tab"]{padding:8px 24px;border-radius:8px;font-weight:700;font-size:0.85rem;color:#8D6E53}
.stTabs [aria-selected="true"]{background:#5D4037!important;color:#FFF!important;border-radius:8px}
.stTabs [data-baseweb="tab-panel"]{padding:0px!important}
.stTabs [data-baseweb="tab-border"]{display:none!important}
.stTabs [data-baseweb="tab-highlight"]{display:none!important}

</style>""", unsafe_allow_html=True)

# Icons
ic = {k: img_b64(v) for k, v in {
    "money": "money_ic.png", "ppl": "ic_people.png",
    "pie": "icon-pie-chart.png", "line": "icons_line-up.png",
    "logo": "logo.png"
}.items()}

# ═══════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════
with st.sidebar:
    if ic["logo"]:
        st.markdown(
            f'<div style="text-align:center;padding:10px 0">'
            f'<img src="{ic["logo"]}" style="max-width:130px"></div>',
            unsafe_allow_html=True)
    st.markdown("---")
    st.radio("Nav", [
        "📊  Dashboard Utama", 
        "⚙️  Pengaturan"
    ], label_visibility="collapsed")
    st.markdown("---")
    st.markdown(
        f'<div style="background:rgba(0,0,0,0.15);padding:12px 16px;'
        f'border-radius:10px;margin:0 12px">'
        f'<p style="margin:0;font-size:0.75rem!important;color:#C49A6C!important">'
        f'Data terakhir diperbarui:</p>'
        f'<p style="margin:4px 0 0;font-size:0.85rem!important;font-weight:700;'
        f'color:#E8DDD3!important">{DF["date"].max().strftime("%d %b %Y")}</p>'
        f'</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
#  HEADER
# ═══════════════════════════════════════════════════════════
st.markdown(
    '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">'
    '<div>'
    '<h2 style="margin:0;font-size:1.4rem;font-weight:800;color:#2C1A12">'
    'KopiSeru Executive Board</h2>'
    '<p style="margin:2px 0 0;font-size:0.85rem;color:#8D6E53;font-weight:500">'
    'Ringkasan Kinerja & Profitabilitas Bisnis</p>'
    '</div></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
#  GLOBAL FILTER BAR
# ═══════════════════════════════════════════════════════════
yrs = sorted(DF["year"].unique())
yr_all_label = f"Jan {min(yrs)} - Des {max(yrs)}"
yr_options = [yr_all_label] + [str(y) for y in yrs]

gf1, gf2, gf3, gf4 = st.columns(4)
with gf1: sel_yr = st.selectbox("📅 Rentang Waktu", yr_options, key="g_yr")
with gf2: sel_br = st.selectbox("🏢 Cabang", ["Semua Cabang"] + sorted(DF["branch_name"].unique().tolist()), key="g_br")
with gf3: sel_tp = st.selectbox("📍 Tipe Lokasi", ["Semua Tipe"] + sorted(DF["branch_type"].unique().tolist()), key="g_tp")
with gf4: sel_pd = st.selectbox("📆 Granularitas Data", ["Bulanan", "Tahunan"], key="g_pd")

# Apply global filters
df = DF.copy()
if sel_yr != yr_all_label: df = df[df["year"] == int(sel_yr)]
if sel_br != "Semua Cabang": df = df[df["branch_name"] == sel_br]
if sel_tp != "Semua Tipe": df = df[df["branch_type"] == sel_tp]
if df.empty:
    st.error("Data tidak ditemukan untuk kombinasi filter ini.")
    st.stop()

# ═══════════════════════════════════════════════════════════
#  KPI CARDS
# ═══════════════════════════════════════════════════════════
R = df["total_revenue"].sum()
P = df["profit"].sum()
M = (P / R * 100) if R else 0
T = df["total_transactions"].sum()

fy = sorted(df["year"].unique())
deltas = {}
if len(fy) >= 2:
    y0, y1 = fy[0], fy[-1]
    d0, d1 = df[df.year == y0], df[df.year == y1]
    r0, r1 = d0.total_revenue.sum(), d1.total_revenue.sum()
    p0, p1 = d0.profit.sum(), d1.profit.sum()
    t0, t1 = d0.total_transactions.sum(), d1.total_transactions.sum()
    m0, m1 = ((p0/r0*100) if r0 else 0), ((p1/r1*100) if r1 else 0)
    if r0: deltas["rev"] = (f"{abs((r1-r0)/r0*100):.1f}%", r1 >= r0)
    if p0: deltas["prof"] = (f"{abs((p1-p0)/p0*100):.1f}%", p1 >= p0)
    if t0: deltas["trx"] = (f"{abs((t1-t0)/t0*100):.1f}%", t1 >= t0)
    deltas["npm"] = (f"{abs(m1-m0):.1f} pt", m1 >= m0)

def kpi_card(label, val, dkey, icon_src):
    d_text, d_up = deltas.get(dkey, ("", True))
    arr = "▲" if d_up else "▼"
    cls = "u" if d_up else "d"
    dh = f'<p class="kpi-d {cls}">{arr} {d_text} <span style="color:#999;font-weight:400">vs periode sblmnya</span></p>' if d_text else ""
    ih = f'<img src="{icon_src}" class="kpi-i">' if icon_src else ""
    st.markdown(f'<div class="kpi"><p class="kpi-l">{label}</p><p class="kpi-v">{val}</p>{dh}{ih}</div>', unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)
with k1: kpi_card("Total Pendapatan", fmt(R), "rev", ic["money"])
with k2: kpi_card("Total Laba Bersih", fmt(P), "prof", ic["line"])
with k3: kpi_card("Net Profit Margin", f"{M:.2f}%", "npm", ic["pie"])
with k4: kpi_card("Total Transaksi", f"{T/1e6:.2f} Jt" if T >= 1e6 else f"{T:,.0f}", "trx", ic["ppl"])

st.write("") # slight spacer

# ═══════════════════════════════════════════════════════════
#  VIEW TABS (PAGINATION: 2 Charts per tab)
# ═══════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs(["Halaman 1: Pertumbuhan", "Halaman 2: Efisiensi & Lokasi", "Halaman 3: Produk & Promo"])

# ───────────────────────────────────────────────────────────
# TAB 1
# ───────────────────────────────────────────────────────────
with tab1:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="cc"><h4>Tren Pendapatan & Pertumbuhan</h4>', unsafe_allow_html=True)
        tr = df.groupby("month")[["total_revenue"]].sum().reset_index()
        fig1 = go.Figure(go.Scatter(x=tr["month"], y=tr["total_revenue"], mode="lines+markers", 
                                    line=dict(color="#4E342E", width=3, shape="spline"), marker=dict(size=6), 
                                    fill="tozeroy", fillcolor="rgba(78,52,46,0.08)", 
                                    hovertemplate="<b>%{x|%b %Y}</b><br>Pendapatan: Rp %{y:,.0f}<extra></extra>"))
        fig1.update_layout(**LAYOUT_BASE, height=CH, yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)", tickformat=".2s"), xaxis=dict(showgrid=False))
        st.plotly_chart(fig1, use_container_width=True, config=CFG, theme=None)
        
        pk = tr.loc[tr["total_revenue"].idxmax()]
        st.markdown(f'<p class="cc-ins">💡 <b>Puncak Pendapatan:</b> Tercatat pada bulan <b>{pk["month"].strftime("%B %Y")}</b> dengan total mencapai <b>{fmt(pk["total_revenue"])}</b>.</p></div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="cc"><h4>Komposisi Pendapatan Cabang Teratas (Top 5)</h4>', unsafe_allow_html=True)
        tops = df.groupby("branch_name")["total_revenue"].sum().nlargest(5).index
        bt = df[df["branch_name"].isin(tops)].groupby(["month", "branch_name"])["total_revenue"].sum().reset_index()
        bt["Cabang"] = bt["branch_name"].str.replace("KopiSeru ", "")
        
        fig2 = px.area(bt, x="month", y="total_revenue", color="Cabang", color_discrete_sequence=PAL)
        fig2.update_layout(**LAYOUT_BASE, height=CH, legend=dict(orientation="v", y=1, x=1.02, title=""), yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)", tickformat=".2s"), xaxis=dict(showgrid=False))
        st.plotly_chart(fig2, use_container_width=True, config=CFG, theme=None)
        
        best = tops[0].replace("KopiSeru ", "")
        st.markdown(f'<p class="cc-ins">💡 <b>Cabang Andalan:</b> <b>{best}</b> memberikan kontribusi pendapatan terbesar dan paling stabil secara keseluruhan.</p></div>', unsafe_allow_html=True)


# ───────────────────────────────────────────────────────────
# TAB 2
# ───────────────────────────────────────────────────────────
with tab2:
    c3, c4 = st.columns(2)

    with c3:
        st.markdown('<div class="cc"><h4>Efisiensi Operasional (Pendapatan vs Profit Margin)</h4>', unsafe_allow_html=True)
        sc = df.groupby("branch_name")[["total_revenue", "profit"]].sum().reset_index()
        sc["margin"] = (sc["profit"] / sc["total_revenue"] * 100).round(1)
        sc = sc.sort_values("total_revenue", ascending=False).head(8) # Show top 8
        sc["Cabang"] = sc["branch_name"].str.replace("KopiSeru ", "")
        
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=sc["Cabang"], y=sc["total_revenue"], name="Pendapatan (Rp)", marker_color="#D7CCC8", hovertemplate="<b>%{x}</b><br>Revenue: Rp %{y:,.0f}<extra></extra>"))
        fig3.add_trace(go.Scatter(x=sc["Cabang"], y=sc["margin"], name="Margin (%)", mode="lines+markers", yaxis="y2", line=dict(color="#4E342E", width=3), marker=dict(size=8), hovertemplate="Margin: %{y}%<extra></extra>"))
        
        fig3.update_layout(**LAYOUT_BASE, height=CH, showlegend=True, legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"),
                           yaxis=dict(showgrid=False, tickformat=".2s"),
                           yaxis2=dict(showgrid=False, overlaying="y", side="right", ticksuffix="%"),
                           xaxis=dict(showgrid=False, tickangle=-30))
        st.plotly_chart(fig3, use_container_width=True, config=CFG, theme=None)
        
        hm = sc.loc[sc["margin"].idxmax(), "Cabang"]
        st.markdown(f'<p class="cc-ins">💡 <b>Efisiensi Tertinggi:</b> Cabang <b>{hm}</b> mampu mencetak Net Profit Margin paling efisien dibandingkan cabang lain.</p></div>', unsafe_allow_html=True)

    with c4:
        st.markdown('<div class="cc"><h4>Kontribusi Pendapatan Berdasarkan Tipe Lokasi</h4>', unsafe_allow_html=True)
        loc = df.groupby("branch_type")["total_revenue"].sum().reset_index().sort_values("total_revenue", ascending=True)
        
        fig4 = px.bar(loc, y="branch_type", x="total_revenue", orientation="h", color="total_revenue", color_continuous_scale=["#E8DDD3", "#4E342E"])
        fig4.update_layout(**LAYOUT_BASE, height=CH, coloraxis_showscale=False, yaxis=dict(title=""), xaxis=dict(title="Total Pendapatan", tickformat=".2s"))
        st.plotly_chart(fig4, use_container_width=True, config=CFG, theme=None)
        
        tt = loc.iloc[-1]["branch_type"]
        st.markdown(f'<p class="cc-ins">💡 <b>Fokus Ekspansi:</b> Tipe lokasi <b>{tt}</b> membuktikan diri sebagai pendorong pendapatan (revenue driver) yang paling solid.</p></div>', unsafe_allow_html=True)


# ───────────────────────────────────────────────────────────
# TAB 3
# ───────────────────────────────────────────────────────────
with tab3:
    c5, c6 = st.columns(2)

    with c5:
        st.markdown('<div class="cc"><h4>Distribusi Pendapatan Kategori Produk</h4>', unsafe_allow_html=True)
        cat = df.groupby("top_selling_category")["total_revenue"].sum().reset_index()
        
        fig5 = px.pie(cat, values="total_revenue", names="top_selling_category", hole=0.5, color_discrete_sequence=PAL)
        fig5.update_traces(textposition="inside", textinfo="percent", hovertemplate="<b>%{label}</b><br>Rp %{value:,.0f}<br>%{percent}<extra></extra>")
        fig5.update_layout(**LAYOUT_BASE, height=CH, legend=dict(orientation="v", y=0.5, x=1.05))
        st.plotly_chart(fig5, use_container_width=True, config=CFG, theme=None)
        
        tc = cat.loc[cat["total_revenue"].idxmax(), "top_selling_category"]
        st.markdown(f'<p class="cc-ins">💡 <b>Kategori Unggulan:</b> Penjualan didominasi oleh kategori <b>{tc}</b>, menjadikannya prioritas untuk dijaga ketersediaannya.</p></div>', unsafe_allow_html=True)

    with c6:
        st.markdown('<div class="cc"><h4>Efektivitas Tipe Promo terhadap Laba Bersih</h4>', unsafe_allow_html=True)
        pt = df[df["promo_active"] == True].groupby("promo_type")["profit"].mean().reset_index().sort_values("profit", ascending=True)
        
        fig6 = px.bar(pt, y="promo_type", x="profit", orientation="h", color="profit", color_continuous_scale=["#E8DDD3", "#4E342E"])
        fig6.update_layout(**LAYOUT_BASE, height=CH, coloraxis_showscale=False, yaxis=dict(title=""), xaxis=dict(title="Rata-rata Laba Harian (Rp)", tickformat=".2s"))
        st.plotly_chart(fig6, use_container_width=True, config=CFG, theme=None)
        
        if not pt.empty:
            bp = pt.iloc[-1]["promo_type"]
            st.markdown(f'<p class="cc-ins">💡 <b>Strategi Pemasaran:</b> Tipe promosi <b>{bp}</b> menghasilkan rata-rata laba bersih harian tertinggi.</p></div>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="cc-ins">💡 Tidak ada data promo aktif untuk rentang yang dipilih.</p></div>', unsafe_allow_html=True)