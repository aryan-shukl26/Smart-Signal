import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import time
from datetime import datetime

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="SmartSignal India",
    page_icon="🚦",
    layout="wide"
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    body { background-color: #0f1117; }
    .metric-card {
        background: #1e2130;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 1px solid #2e3250;
    }
    .signal-green {
        background: #1a3a2a;
        border: 2px solid #00ff88;
        border-radius: 50%;
        width: 80px; height: 80px;
        margin: auto;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
    }
    .signal-red {
        background: #3a1a1a;
        border: 2px solid #ff4444;
        border-radius: 50%;
        width: 80px; height: 80px;
        margin: auto;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
    }
    .alert-box {
        background: #2a1a1a;
        border-left: 4px solid #ff4444;
        padding: 12px;
        border-radius: 6px;
        margin: 8px 0;
    }
    .violation-box {
        background: #2a2a1a;
        border-left: 4px solid #ffaa00;
        padding: 12px;
        border-radius: 6px;
        margin: 8px 0;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────
st.markdown("# 🚦 SmartSignal India")
st.markdown("### Adaptive Traffic Management Dashboard")
st.divider()

# ── Simulated live data (replace with real traci data later) ──
directions = ["North", "South", "East", "West"]

def get_mock_data():
    import random
    counts = {d: random.randint(2, 20) for d in directions}
    ns = counts["North"] + counts["South"]
    ew = counts["East"] + counts["West"]
    busiest = "North/South" if ns >= ew else "East/West"
    green_duration = min(10 + (max(ns, ew) * 2), 60)
    return counts, busiest, green_duration

# ── Load violation log ────────────────────────────────────────
try:
    violations_df = pd.read_csv("violation_log.csv")
except:
    violations_df = pd.DataFrame(columns=["frame","timestamp_sec","type","class","confidence"])

# ── Mock accident log ─────────────────────────────────────────
accident_log = [
    {"timestamp_sec": 18.75, "vehicle_id": 13, "class": "car", "location": "(46, 166)"},
    {"timestamp_sec": 19.0,  "vehicle_id": 13, "class": "car", "location": "(33, 166)"}
]

# ── Auto refresh ──────────────────────────────────────────────
refresh = st.sidebar.slider("Refresh rate (seconds)", 1, 10, 3)
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Session Info")
st.sidebar.markdown(f"**Started:** {datetime.now().strftime('%H:%M:%S')}")
st.sidebar.markdown(f"**Violations logged:** {len(violations_df)}")
st.sidebar.markdown(f"**Accidents logged:** {len(accident_log)}")

counts, busiest, green_duration = get_mock_data()

# ── Row 1: Vehicle counts ─────────────────────────────────────
st.markdown("### 🚗 Live Vehicle Counts")
cols = st.columns(4)
for i, direction in enumerate(directions):
    with cols[i]:
        st.metric(
            label=f"{'🟢' if direction in busiest else '🔴'} {direction}",
            value=f"{counts[direction]} vehicles"
        )

st.divider()

# ── Row 2: Signal state + chart ───────────────────────────────
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 🔴🟢 Signal State")
    for direction in directions:
        is_green = direction in busiest
        state = "🟢 GREEN" if is_green else "🔴 RED"
        st.markdown(f"**{direction}:** {state}")
    st.markdown(f"**Active green duration:** `{green_duration}s`")
    st.markdown(f"**Busiest corridor:** `{busiest}`")

with col2:
    st.markdown("### 📊 Traffic Distribution")
    fig = go.Figure(go.Bar(
        x=directions,
        y=[counts[d] for d in directions],
        marker_color=["#00ff88" if d in busiest else "#ff4444" for d in directions],
        text=[counts[d] for d in directions],
        textposition="outside"
    ))
    fig.update_layout(
        paper_bgcolor="#1e2130",
        plot_bgcolor="#1e2130",
        font_color="white",
        height=300,
        margin=dict(t=20, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Row 3: Violations ─────────────────────────────────────────
st.markdown("### ⚠️ Violation Log")
if len(violations_df) > 0:
    st.dataframe(
        violations_df.style.map(
            lambda x: "background-color: #2a2a1a; color: #ffaa00"
            if isinstance(x, str) else ""
        ),
        use_container_width=True
    )
else:
    st.info("No violations detected yet.")

st.divider()

# ── Row 4: Accident alerts ────────────────────────────────────
st.markdown("### 🆘 Accident Alerts")
if accident_log:
    for alert in accident_log:
        st.markdown(f"""
        <div class="alert-box">
            🚨 <strong>ACCIDENT DETECTED</strong> &nbsp;|&nbsp;
            Vehicle: <strong>{alert['class']} ID:{alert['vehicle_id']}</strong> &nbsp;|&nbsp;
            Time: <strong>{alert['timestamp_sec']}s</strong> &nbsp;|&nbsp;
            Location: <strong>{alert['location']}</strong>
        </div>
        """, unsafe_allow_html=True)
else:
    st.success("No accidents detected.")

# ── Auto refresh ──────────────────────────────────────────────
time.sleep(refresh)
st.rerun()