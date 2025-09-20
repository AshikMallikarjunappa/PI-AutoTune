import streamlit as st

st.set_page_config(page_title="PI Autotune Tool", layout="wide")
st.title("Alerton PI Configuration")

st.header("Alerton Control Strategies")
st.markdown("Select a control strategy and adjust Response Speed (slow ↔ fast).")

# Alerton presets with corrected STUP values
controls = {
    "Standard Zone Heating Signal": {"Kp": 12, "Ki": 1, "Imax": 3, "Ilimit": 50, "STUP": 30},
    "Standard Zone Cooling Signal": {"Kp": 12, "Ki": 1, "Imax": 3, "Ilimit": 50, "STUP": -30},
    "Standard Economizer Control": {"Kp": 0.6, "Ki": 1.5, "Imax": 60, "Ilimit": 50, "STUP": -50},
    "Standard Supply DSP Control": {"Kp": 0, "Ki": 30, "Imax": 60, "Ilimit": 50, "STUP": 30},
    "Standard SAT Heating Valve": {"Kp": 0.6, "Ki": 1.5, "Imax": 60, "Ilimit": 50, "STUP": 50},
    "Standard BSP Fan Control": {"Kp": 0, "Ki": 25, "Imax": 20, "Ilimit": 50, "STUP": 0}
}

selected = st.selectbox("Select control strategy:", list(controls.keys()))
params = controls[selected]

# Response Speed slider
response_speed = st.slider("Response Speed (Slow ↔ Fast)", 0.5, 2.0, 1.0, 0.1)

# Only scale Kp, Ki, Imax by slider; Ilimit and STUP remain fixed
scaled_params = {
    "Kp": round(params["Kp"] * response_speed, 3),
    "Ki": round(params["Ki"] * response_speed, 3),
    "Imax": round(params["Imax"] * response_speed, 3),
    "Ilimit": params["Ilimit"],
    "STUP": params["STUP"]  # Corrected exact values
}

st.subheader(f"{selected} Parameters (scaled by Response Speed)")
st.json(scaled_params)
