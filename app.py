import streamlit as st
import json
import os
import pandas as pd

st.set_page_config(page_title="Sovereign Control Plane", layout="wide")

st.title("⚡ Sovereign Grid-Agent: Industrial Governor")
st.markdown("### Status: **Autonomous Sovereignty Engaged**")

# Function to load backend status
def load_status():
    if os.path.exists("status.json"):
        with open("status.json", "r") as f:
            return json.load(f)
    return None

# Sidebar for System Parameters
st.sidebar.header("System Governance")
st.sidebar.info("Governor Veto Protocol: ACTIVE")
st.sidebar.metric("Watchdog Pulse", "500ms")

# Display Metrics
status = load_status()
if status:
    col1, col2, col3 = st.columns(3)
    col1.metric("Current Frequency", f"{status['telemetry']['freq']} Hz")
    col2.metric("System Temperature", f"{status['telemetry']['temp']} °C")
    col3.metric("Swarm Action", status['action'].get('action_val', 'N/A'))

    st.subheader("Decision Audit Trail")
    st.json(status['action'])
else:
    st.warning("Backend Engine Offline. Please initiate SovereignGridSwarm.")

# Refresh Mechanism
if st.button("Sync Governance State"):
    st.rerun()

st.divider()
st.caption("WARNING: This dashboard is for monitoring only. Command input is physically disabled at the OS level.")
