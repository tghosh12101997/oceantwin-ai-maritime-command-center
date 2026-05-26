from __future__ import annotations

import sys
import math
from pathlib import Path
from typing import Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from kg.graph_builder import build_route_graph, export_graph
from services.copilot import answer_question
from services.risk_engine import assess_route
from utils.data_loader import load_demo_vessels, load_fleet, load_live_positions, load_ports

ROOT = Path(__file__).resolve().parents[1]
EXPORTS = ROOT / "exports"
EXPORTS.mkdir(exist_ok=True)

st.set_page_config(
    page_title="OceanTwin AI Command Center",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Styling: futuristic Grafana/PowerBI inspired UI
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp {
        background: radial-gradient(circle at top left, rgba(34, 211, 238, 0.18), transparent 32%),
                    radial-gradient(circle at top right, rgba(168, 85, 247, 0.16), transparent 30%),
                    linear-gradient(135deg, #07111f 0%, #0b1020 48%, #111827 100%);
        color: #e5eefb;
    }
    section[data-testid="stSidebar"] {
        background: rgba(3, 7, 18, 0.78);
        border-right: 1px solid rgba(148, 163, 184, 0.18);
    }
    .block-container { padding-top: 1.1rem; padding-bottom: 2rem; }
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.92), rgba(30, 41, 59, 0.72));
        border: 1px solid rgba(125, 211, 252, 0.22);
        box-shadow: 0 18px 45px rgba(0,0,0,0.26);
        border-radius: 22px;
        padding: 18px 18px;
    }
    div[data-testid="stMetricValue"] { font-size: 1.75rem; font-weight: 800; }
    div[data-testid="stMetricLabel"] { color: #93c5fd; font-weight: 700; }
    .glass-card {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.82), rgba(30, 41, 59, 0.58));
        border: 1px solid rgba(148, 163, 184, 0.20);
        border-radius: 24px;
        padding: 20px;
        box-shadow: 0 18px 45px rgba(0,0,0,0.28);
        margin-bottom: 16px;
    }
    .hero-title {
        font-size: 2.5rem;
        font-weight: 900;
        letter-spacing: -0.06em;
        margin-bottom: 0.15rem;
        background: linear-gradient(90deg, #e0f2fe, #67e8f9, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle { color: #a8b3c7; font-size: 1rem; margin-bottom: 1rem; }
    .pill {
        display:inline-block;
        padding: 7px 11px;
        border-radius: 999px;
        border: 1px solid rgba(125,211,252,0.25);
        background: rgba(8,47,73,0.35);
        color: #bae6fd;
        margin-right: 7px;
        margin-bottom: 7px;
        font-weight: 700;
        font-size: 0.8rem;
    }
    .section-title { font-size:1.2rem; font-weight:800; color:#e0f2fe; margin: 0.3rem 0 0.8rem 0; }
    .small-muted { color:#94a3b8; font-size:0.9rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background: rgba(15, 23, 42, 0.72);
        border-radius: 14px;
        border: 1px solid rgba(148,163,184,0.18);
        padding: 10px 14px;
    }
    .stDataFrame, div[data-testid="stDataFrame"] { border-radius: 18px; overflow: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Data loading and synthetic analytics helpers
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_events() -> pd.DataFrame:
    path = ROOT / "data" / "operational_events.csv"
    if path.exists():
        df = pd.read_csv(path)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df
    return pd.DataFrame()


def build_route_dataset(ports: pd.DataFrame, origins: List[str], destinations: List[str], teu: int, speed: float) -> pd.DataFrame:
    rows = []
    for o in origins:
        for d in destinations:
            if o == d:
                continue
            a = assess_route(ports, o, d, vessel_teu=teu, speed_knots=speed)
            rows.append({
                "origin": o,
                "destination": d,
                "route": f"{o} → {d}",
                "distance_nm": a.distance_nm,
                "eta_days": a.eta_days,
                "risk_score": a.eta_risk_score,
                "risk_label": a.eta_risk_label,
                "carbon_tco2": a.carbon_tco2,
                "eu_exposure": a.eu_regulation_exposure,
            })
    return pd.DataFrame(rows)


def risk_color(label: str) -> str:
    return {"High": "#fb7185", "Medium": "#facc15", "Low": "#34d399"}.get(label, "#38bdf8")


def kpi_card(title: str, value: str, note: str = "") -> None:
    st.markdown(
        f"""
        <div class="glass-card">
            <div class="small-muted">{title}</div>
            <div style="font-size:2rem;font-weight:900;color:#f8fafc;line-height:1.1;">{value}</div>
            <div class="small-muted">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def make_gauge(score: float, label: str) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score * 100,
        number={"suffix": "%", "font": {"size": 36}},
        title={"text": f"ETA Risk: {label}", "font": {"size": 18}},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": risk_color(label)},
            "bgcolor": "rgba(15,23,42,0.4)",
            "borderwidth": 1,
            "bordercolor": "rgba(148,163,184,0.25)",
            "steps": [
                {"range": [0, 45], "color": "rgba(52,211,153,0.28)"},
                {"range": [45, 70], "color": "rgba(250,204,21,0.26)"},
                {"range": [70, 100], "color": "rgba(251,113,133,0.26)"},
            ],
        },
    ))
    fig.update_layout(height=290, margin=dict(l=20, r=20, t=50, b=10), paper_bgcolor="rgba(0,0,0,0)", font_color="#e5eefb")
    return fig


def style_fig(fig: go.Figure, height: int = 430) -> go.Figure:
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.42)",
        font=dict(color="#dbeafe"),
        margin=dict(l=20, r=20, t=44, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(gridcolor="rgba(148,163,184,0.14)"),
        yaxis=dict(gridcolor="rgba(148,163,184,0.14)"),
    )
    return fig


def chart_builder(df: pd.DataFrame, key: str) -> None:
    st.markdown("<div class='section-title'>Build your own chart</div>", unsafe_allow_html=True)
    if df.empty:
        st.warning("Selected dataset is empty.")
        return

    chart_type = st.selectbox("Chart type", ["Bar", "Line", "Scatter", "Area", "Pie", "Heatmap", "Table"], key=f"{key}_type")
    columns = df.columns.tolist()
    numeric = df.select_dtypes(include="number").columns.tolist()
    categorical = [c for c in columns if c not in numeric]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        x = st.selectbox("X / category", columns, key=f"{key}_x")
    with c2:
        y = st.selectbox("Y / value", numeric or columns, key=f"{key}_y")
    with c3:
        color = st.selectbox("Color / split", ["None"] + columns, key=f"{key}_color")
    with c4:
        agg = st.selectbox("Aggregation", ["sum", "mean", "max", "min", "count"], key=f"{key}_agg")

    working = df.copy()
    if chart_type != "Table" and y in working.columns and x in working.columns:
        if agg == "count":
            group_cols = [x] + ([] if color == "None" or color == x else [color])
            working = working.groupby(group_cols, dropna=False).size().reset_index(name="count")
            y = "count"
        elif y in numeric:
            group_cols = [x] + ([] if color == "None" or color == x else [color])
            working = getattr(working.groupby(group_cols, dropna=False)[y], agg)().reset_index()

    if chart_type == "Table":
        st.dataframe(df, use_container_width=True, height=440)
        return
    if chart_type == "Bar":
        fig = px.bar(working, x=x, y=y, color=None if color == "None" else color, title=f"{agg.title()} {y} by {x}")
    elif chart_type == "Line":
        fig = px.line(working, x=x, y=y, color=None if color == "None" else color, markers=True, title=f"{y} trend by {x}")
    elif chart_type == "Scatter":
        fig = px.scatter(working, x=x, y=y, color=None if color == "None" else color, size=y if y in numeric else None, title=f"{y} vs {x}")
    elif chart_type == "Area":
        fig = px.area(working, x=x, y=y, color=None if color == "None" else color, title=f"{y} area view")
    elif chart_type == "Pie":
        fig = px.pie(working, names=x, values=y if y in working.columns else None, title=f"Share of {y} by {x}")
    else:
        pivot = pd.pivot_table(df, index=x, columns=color if color != "None" else None, values=y, aggfunc=agg if agg != "count" else "count", fill_value=0)
        fig = px.imshow(pivot, aspect="auto", title=f"Heatmap: {y} by {x}" + (f" and {color}" if color != "None" else ""))
    st.plotly_chart(style_fig(fig, 470), use_container_width=True)

# -----------------------------------------------------------------------------
# App state and sidebar scenario
# -----------------------------------------------------------------------------
ports = load_ports()
fleet = load_fleet()
demo_vessels = load_demo_vessels()
live_positions = load_live_positions()
events = load_events()

st.sidebar.markdown("### OceanTwin AI")
page = st.sidebar.radio(
    "Workspace",
    ["Command Center", "FleetPulse Live", "Route Intelligence", "Chart Studio", "Knowledge Graph", "Reports"],
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Scenario controls")
company = st.sidebar.selectbox("Company watchlist", sorted(fleet["company"].dropna().unique().tolist()))
company_fleet = fleet[fleet["company"] == company]
vessel_name = st.sidebar.selectbox("Watched vessel", company_fleet["vessel_name"].tolist())
origin = st.sidebar.selectbox("Origin port", ports["port_name"].tolist(), index=0)
destination = st.sidebar.selectbox("Destination port", ports["port_name"].tolist(), index=3)
speed = st.sidebar.slider("Assumed vessel speed, knots", 8.0, 24.0, 16.0, 0.5)
teu_default = int(company_fleet.loc[company_fleet["vessel_name"] == vessel_name, "capacity_teu"].fillna(15000).iloc[0])
teu = st.sidebar.number_input("Vessel capacity, TEU", min_value=1000, max_value=30000, value=teu_default, step=500)

assessment = assess_route(ports, origin, destination, vessel_teu=teu, speed_knots=speed)
route_df = build_route_dataset(ports, [origin, "Hamburg", "Rotterdam", "Singapore", "Shanghai"], [destination, "Singapore", "Shanghai", "Los Angeles", "Jebel Ali"], teu, speed)
map_df = live_positions if not live_positions.empty else demo_vessels.copy()
if "company" in map_df.columns:
    map_df = map_df[map_df["company"].fillna(company).eq(company) | map_df["company"].isna()]
if map_df.empty:
    map_df = demo_vessels.copy()

st.markdown("<div class='hero-title'>OceanTwin AI Command Center</div>", unsafe_allow_html=True)
st.markdown("<div class='hero-subtitle'>Grafana-style operations cockpit + PowerBI-style self-service analytics for maritime route, fleet, carbon and risk intelligence.</div>", unsafe_allow_html=True)
st.markdown("<span class='pill'>Live AIS-ready</span><span class='pill'>Knowledge Graph</span><span class='pill'>ETA Risk</span><span class='pill'>Carbon Intelligence</span><span class='pill'>Custom Chart Studio</span>", unsafe_allow_html=True)


def rdf_graph_to_plotly(g) -> go.Figure:
    """Create a clean dark semantic graph view without pyvis iframe issues."""
    triples = [(str(s), str(p), str(o)) for s, p, o in g]
    if not triples:
        return go.Figure()

    def short(value: str) -> str:
        if value.startswith("http"):
            return value.rstrip("/").split("/")[-1].replace("_", " ")
        return value.replace("_", " ")

    nodes = sorted(set([s for s, _, _ in triples] + [o for _, _, o in triples]))
    labels = {n: short(n) for n in nodes}

    # Put important entities close to center and spread the rest in a ring.
    center_keywords = ["route", "vessel", "risk", "carbon"]
    center_nodes = [n for n in nodes if any(k.lower() in labels[n].lower() for k in center_keywords)]
    ring_nodes = [n for n in nodes if n not in center_nodes]

    positions = {}
    for i, n in enumerate(center_nodes):
        angle = 2 * math.pi * i / max(len(center_nodes), 1)
        positions[n] = (0.55 * math.cos(angle), 0.55 * math.sin(angle))

    for i, n in enumerate(ring_nodes):
        angle = 2 * math.pi * i / max(len(ring_nodes), 1)
        radius = 1.75 + (0.25 if i % 2 else 0)
        positions[n] = (radius * math.cos(angle), radius * math.sin(angle))

    edge_x, edge_y = [], []
    edge_label_x, edge_label_y, edge_text = [], [], []
    for s, p, o in triples:
        x0, y0 = positions[s]
        x1, y1 = positions[o]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_label_x.append((x0 + x1) / 2)
        edge_label_y.append((y0 + y1) / 2)
        edge_text.append(short(p))

    node_x = [positions[n][0] for n in nodes]
    node_y = [positions[n][1] for n in nodes]
    node_text = [labels[n] for n in nodes]

    sizes = []
    colors = []
    for n in nodes:
        label = labels[n].lower()
        if "route" in label:
            sizes.append(38); colors.append("#22d3ee")
        elif "vessel" in label or "express" in label or "muraykh" in label:
            sizes.append(34); colors.append("#a78bfa")
        elif "risk" in label or "high" in label:
            sizes.append(32); colors.append("#fb7185")
        elif "carbon" in label or "emission" in label:
            sizes.append(32); colors.append("#34d399")
        elif "port" in label or label in ["hamburg", "singapore", "rotterdam", "shanghai"]:
            sizes.append(30); colors.append("#60a5fa")
        else:
            sizes.append(24); colors.append("#94a3b8")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y, mode="lines",
        line=dict(width=1.4, color="rgba(148, 163, 184, 0.38)"),
        hoverinfo="none",
        name="relations",
    ))
    fig.add_trace(go.Scatter(
        x=edge_label_x, y=edge_label_y, mode="text",
        text=edge_text,
        textfont=dict(size=9, color="#93c5fd"),
        hoverinfo="none",
        showlegend=False,
    ))
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y, mode="markers+text",
        text=node_text,
        textposition="top center",
        marker=dict(
            size=sizes,
            color=colors,
            line=dict(width=1.5, color="rgba(248,250,252,0.75)")
        ),
        textfont=dict(size=11, color="#e5eefb"),
        hovertext=node_text,
        hoverinfo="text",
        name="semantic nodes",
    ))
    fig.update_layout(
        height=660,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.48)",
        margin=dict(l=10, r=10, t=20, b=10),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        showlegend=False,
        hovermode="closest",
    )
    return fig


# -----------------------------------------------------------------------------
# Pages
# -----------------------------------------------------------------------------
if page == "Command Center":
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("ETA Risk", assessment.eta_risk_label, f"{assessment.eta_risk_score:.2f}")
    m2.metric("Distance", f"{assessment.distance_nm:,.0f} nm")
    m3.metric("Transit", f"{assessment.eta_days} days")
    m4.metric("Carbon", f"{assessment.carbon_tco2:,.0f} tCO₂")
    m5.metric("EU Exposure", "Yes" if assessment.eu_regulation_exposure else "No")
    m6.metric("Tracked Vessels", f"{len(map_df)}")

    left, mid, right = st.columns([1.25, 1, 1])
    with left:
        st.markdown("<div class='section-title'>Global route and fleet view</div>", unsafe_allow_html=True)
        origin_row = ports[ports["port_name"] == origin].iloc[0]
        dest_row = ports[ports["port_name"] == destination].iloc[0]
        fig = go.Figure()
        fig.add_trace(go.Scattergeo(
            lon=[origin_row.lon, dest_row.lon], lat=[origin_row.lat, dest_row.lat],
            mode="lines+markers+text", text=[origin, destination], textposition="top center",
            line=dict(width=4, color="#22d3ee"), marker=dict(size=11, color="#a78bfa"), name="Selected route"))
        fig.add_trace(go.Scattergeo(
            lon=map_df["lon"], lat=map_df["lat"], mode="markers+text",
            text=map_df.get("vessel_name", pd.Series(["Vessel"] * len(map_df))), textposition="top center",
            marker=dict(size=10, color="#34d399", line=dict(width=1, color="#f8fafc")), name="Watched vessels"))
        fig.update_geos(showland=True, landcolor="rgba(30,41,59,0.85)", showocean=True, oceancolor="rgba(8,47,73,0.5)", showcountries=True, countrycolor="rgba(148,163,184,0.25)", projection_type="natural earth")
        st.plotly_chart(style_fig(fig, 520), use_container_width=True)
    with mid:
        st.plotly_chart(make_gauge(assessment.eta_risk_score, assessment.eta_risk_label), use_container_width=True)
        fig = px.bar(route_df.sort_values("risk_score", ascending=False).head(8), x="risk_score", y="route", orientation="h", color="risk_label", title="Top risky simulated routes")
        st.plotly_chart(style_fig(fig, 265), use_container_width=True)
    with right:
        st.markdown("<div class='section-title'>Operational narrative</div>", unsafe_allow_html=True)
        for item in assessment.explanation:
            st.markdown(f"<div class='glass-card'>• {item}</div>", unsafe_allow_html=True)
        question = st.text_input("Copilot question", "Which operational action should I take first?")
        st.info(answer_question(question, assessment, vessel_name, company))

    c1, c2 = st.columns(2)
    with c1:
        fig = px.line(events, x="timestamp", y="delay_hours", color="event_type", markers=True, title="Delay events over time") if not events.empty else go.Figure()
        st.plotly_chart(style_fig(fig), use_container_width=True)
    with c2:
        if not events.empty:
            events_plot = events.copy()
            events_plot["delay_hours_size"] = events_plot["delay_hours"].abs().clip(lower=1)
            fig = px.scatter(
                events_plot,
                x="cost_usd",
                y="co2_delta_tonnes",
                color="severity",
                size="delay_hours_size",
                hover_name="vessel_name",
                hover_data=["delay_hours", "event_type", "port"],
                title="Cost vs CO₂ impact of operational events",
            )
        else:
            fig = go.Figure()
        st.plotly_chart(style_fig(fig), use_container_width=True)

elif page == "FleetPulse Live":
    st.markdown("<div class='section-title'>FleetPulse Live Monitor</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("Average speed", f"{map_df['sog'].mean():.1f} kn", "from live/demo AIS positions")
    with c2: kpi_card("Fastest vessel", str(map_df.loc[map_df['sog'].idxmax(), 'vessel_name']), f"{map_df['sog'].max():.1f} kn")
    with c3: kpi_card("Ports in watch", f"{ports['port_name'].nunique()}", "risk model coverage")
    with c4: kpi_card("Stationary / waiting", f"{(map_df['sog'] < 1).sum()}", "speed below 1 knot")

    left, right = st.columns([1.4, 1])
    with left:
        fig = px.scatter_geo(map_df, lat="lat", lon="lon", color="sog", size="sog", hover_name="vessel_name", hover_data=["destination", "eta", "heading"], title="Watched vessel positions")
        fig.update_geos(showland=True, showocean=True, projection_type="natural earth")
        st.plotly_chart(style_fig(fig, 570), use_container_width=True)
    with right:
        fig = px.bar(map_df.sort_values("sog", ascending=True), x="sog", y="vessel_name", orientation="h", title="Vessel speed ranking")
        st.plotly_chart(style_fig(fig, 275), use_container_width=True)
        fig = px.pie(map_df, names="destination", title="Destination split")
        st.plotly_chart(style_fig(fig, 275), use_container_width=True)
    st.dataframe(map_df, use_container_width=True)

elif page == "Route Intelligence":
    st.markdown("<div class='section-title'>Route Lab</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        st.plotly_chart(make_gauge(assessment.eta_risk_score, assessment.eta_risk_label), use_container_width=True)
    with c2:
        fig = px.bar(route_df, x="route", y="carbon_tco2", color="risk_label", title="Carbon by route scenario")
        st.plotly_chart(style_fig(fig, 300), use_container_width=True)
    with c3:
        fig = px.scatter(route_df, x="distance_nm", y="risk_score", size="carbon_tco2", color="eu_exposure", hover_name="route", title="Distance vs ETA risk")
        st.plotly_chart(style_fig(fig, 300), use_container_width=True)
    st.dataframe(route_df.sort_values("risk_score", ascending=False), use_container_width=True)

elif page == "Chart Studio":
    st.markdown("<div class='section-title'>Self-service BI Chart Studio</div>", unsafe_allow_html=True)
    st.caption("Choose a maritime dataset, pick dimensions/measures, then create your own charts like a lightweight PowerBI/Grafana builder.")
    datasets: Dict[str, pd.DataFrame] = {
        "Fleet positions": map_df,
        "Ports and congestion": ports,
        "Route scenarios": route_df,
        "Operational events": events,
        "Fleet watchlist": company_fleet,
    }
    selected = st.selectbox("Dataset", list(datasets.keys()))
    df = datasets[selected]

    with st.expander("Data filters", expanded=True):
        fcols = st.columns(3)
        filtered = df.copy()
        for i, col in enumerate(df.columns[:6]):
            if df[col].dtype == "object" or str(df[col].dtype).startswith("category") or df[col].nunique() < 12:
                vals = sorted([str(v) for v in df[col].dropna().unique().tolist()])
                chosen = fcols[i % 3].multiselect(f"Filter {col}", vals, default=vals, key=f"filter_{selected}_{col}")
                if chosen:
                    filtered = filtered[filtered[col].astype(str).isin(chosen)]
    chart_builder(filtered, "studio")
    st.download_button("Download filtered dataset as CSV", filtered.to_csv(index=False).encode("utf-8"), file_name=f"{selected.lower().replace(' ', '_')}.csv")

elif page == "Knowledge Graph":
    st.markdown("<div class='section-title'>Semantic digital twin</div>", unsafe_allow_html=True)
    g = build_route_graph(assessment, vessel_name=vessel_name, company=company)
    ttl_path = export_graph(g, EXPORTS / "oceantwin_route_graph.ttl")

    graph_nodes = len(set([str(s) for s, _, _ in g] + [str(o) for _, _, o in g]))
    graph_edges = len(g)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Graph nodes", graph_nodes)
    k2.metric("RDF triples", graph_edges)
    k3.metric("Route risk", assessment.eta_risk_label)
    k4.metric("EU exposure", "Yes" if assessment.eu_regulation_exposure else "No")

    left, right = st.columns([1.45, 1])
    with left:
        st.markdown("<div class='glass-card'><b>Interactive maritime knowledge graph</b><br><span class='small-muted'>Vessel, company, ports, route, ETA risk, carbon estimate and EU exposure are connected as semantic entities.</span></div>", unsafe_allow_html=True)
        st.plotly_chart(rdf_graph_to_plotly(g), use_container_width=True)

    with right:
        st.markdown("<div class='glass-card'><b>Why this matters</b><br>This is the semantic layer behind the dashboard. It can later power SPARQL queries, GraphRAG answers, explainable alerts, and interoperable maritime data exchange.</div>", unsafe_allow_html=True)
        st.markdown("<div class='glass-card'><b>Example questions</b><br>• Which route has high ETA risk?<br>• Which vessel is connected to EU exposure?<br>• Which carbon estimate belongs to this voyage?</div>", unsafe_allow_html=True)
        st.code(g.serialize(format="turtle")[:3200], language="turtle")
        with open(ttl_path, "rb") as f:
            st.download_button("Download RDF/Turtle graph", data=f, file_name="oceantwin_route_graph.ttl")

else:
    st.markdown("<div class='section-title'>Executive report builder</div>", unsafe_allow_html=True)
    report = f"""# OceanTwin AI Route Intelligence Report

## Scenario
- Company: {company}
- Watched vessel: {vessel_name}
- Route: {origin} → {destination}
- Assumed speed: {speed} knots
- Capacity: {teu:,} TEU

## Route Intelligence
- Approximate distance: {assessment.distance_nm:,.0f} nautical miles
- Estimated transit time: {assessment.eta_days} days
- ETA risk: {assessment.eta_risk_label} ({assessment.eta_risk_score})
- Carbon estimate: {assessment.carbon_tco2:,.0f} tCO₂
- EU regulation exposure: {'Yes' if assessment.eu_regulation_exposure else 'No'}

## Explanation
{chr(10).join('- ' + x for x in assessment.explanation)}

## Operational Recommendation
Use FleetPulse to monitor speed and destination changes, compare route-level carbon/risk scores, and trigger customer alerts when ETA risk moves from medium to high.

## Product angle
This prototype demonstrates how maritime companies can combine AIS-ready fleet tracking, route risk, carbon intelligence, and semantic knowledge graphs into a decision-support layer.
"""
    st.markdown(report)
    st.download_button("Download Markdown report", data=report, file_name="oceantwin_route_report.md")
    st.download_button("Download route scenarios CSV", data=route_df.to_csv(index=False), file_name="route_scenarios.csv")