import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timezone

API_URL = "http://127.0.0.1:8000"

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="IT Support Dashboard",
    layout="wide"
)

st.title("IT Support Dashboard")

# ---------------- FILTERS ----------------
st.sidebar.header("Filtreler")

status_filter = st.sidebar.selectbox(
    "Status",
    ["all", "open", "in_progress", "closed"]
)

priority_filter = st.sidebar.selectbox(
    "Priority",
    ["all", "P1", "P2", "P3", "P4"]
)

# ---------------- FETCH DATA ----------------
try:
    params = {}
    if status_filter != "all":
        params["status"] = status_filter

    response = requests.get(
        f"{API_URL}/tickets",
        params=params,
        timeout=5
    )
    response.raise_for_status()
    tickets = response.json()

except Exception as e:
    st.error(f"API bağlantı hatası: {e}")
    st.stop()

df = pd.DataFrame(tickets)

if df.empty:
    st.warning("Hiç ticket bulunamadı.")
    st.stop()

# ---------------- DATA CLEAN ----------------
df["created_at"] = pd.to_datetime(
    df.get("created_at"),
    errors="coerce"
)

if "sla_deadline" in df.columns:
    df["sla_deadline"] = pd.to_datetime(
        df["sla_deadline"],
        errors="coerce"
    )
else:
    df["sla_deadline"] = pd.NaT

if priority_filter != "all" and "priority" in df.columns:
    df = df[df["priority"] == priority_filter]

# ---------------- SLA CALCULATION ----------------
def sla_remaining_hours(row):
    if pd.isna(row["sla_deadline"]):
        return None

    return (
        row["sla_deadline"].replace(tzinfo=timezone.utc)
        - datetime.now(timezone.utc)
    ).total_seconds() / 3600

df["sla_remaining_hours"] = df.apply(
    sla_remaining_hours,
    axis=1
)

# ---------------- METRICS ----------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Tickets", len(df))

col2.metric(
    "P1 Tickets",
    len(df[df.get("priority") == "P1"])
)

col3.metric(
    "SLA Breached",
    len(df[df["sla_remaining_hours"] < 0])
)

col4.metric(
    "Escalated",
    len(df[df.get("escalated") == True])
)

# ================== GRAPHS ==================
st.divider()
st.subheader("Ticket Analytics")

g1, g2 = st.columns(2)

# -------- Ticket Trend (Daily) --------
with g1:
    st.markdown("### Ticket Trend (Daily)")

    trend_df = (
        df
        .groupby(df["created_at"].dt.date)
        .size()
        .to_frame(name="ticket_count")
    )

    st.line_chart(
        trend_df,
        height=300
    )

# -------- Priority Distribution --------
with g2:
    st.markdown("### 🚦 Priority Dağılımı")

    if "priority" in df.columns:
        priority_df = (
            df["priority"]
            .value_counts()
            .to_frame(name="count")
        )

        st.bar_chart(
            priority_df,
            height=300
        )
    else:
        st.info("Priority bilgisi bulunamadı.")

# ---------------- TABLE ----------------
st.divider()
st.subheader("Ticket Listesi")

def highlight_sla(row):
    if (
        row["sla_remaining_hours"] is not None
        and row["sla_remaining_hours"] < 0
    ):
        return ["background-color: #ffcccc"] * len(row)
    return [""] * len(row)

st.dataframe(
    df.style.apply(highlight_sla, axis=1),
    width="stretch"
)
