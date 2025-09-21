import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ------------------ Page Config ------------------
st.set_page_config(
    page_title="PI Loop Autotune Tool by Ashik",
    layout="wide",
)

# ------------------ Custom CSS for Modern UI ------------------
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        color: white;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    h1, h2, h3, h4, h5, h6 {
        color: white !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }
    p, label, span {
        color: white !important;
    }
    .stButton>button {
        background: linear-gradient(90deg,#00c6ff,#0072ff);
        color: white;
        border-radius: 10px;
        height: 3em;
        font-weight: 600;
    }
    .stSlider>div>div>div>div>div {
        color: #00c6ff !important;
    }
    .stSelectbox>div>div>div>div {
        background-color: #0072ff !important;
        color: white !important;
        border-radius: 8px;
    }
    .stRadio>div>div>label {
        color: white !important;
        font-weight: 600;
    }
    .stCodeBlock, pre {
        background-color: #0a0a0a !important;
        color: #00ffff !important;
        border-radius: 10px;
        padding: 15px;
        font-size: 1rem;
    }
    .stFileUploader>div>div>label {
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------ Header ------------------
st.image("https://github.com/AshikMallikarjunappa/PI-AutoTune/blob/main/Ashik.jpg", caption="Ashik", use_container_width=True)
st.markdown("<h1>PI Loop Autotune Tool by Ashik</h1>", unsafe_allow_html=True)

# ------------------ Tabs ------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Directions", "Simulation", "CSV Tuning", "Alerton Presets", "Niagara 4 PID"]
)

# ------------------ Directions Tab ------------------
with tab1:
    st.header("Instructions")
    st.markdown("""
    - Use **Simulation** tab to test PI control response.
    - Use **CSV Tuning** tab to upload tuning values and visualize results.
    - Use **Alerton Presets** tab to quickly select standard tuning strategies.
    - Use **Niagara 4 PID** tab to view tuned PID constants for various control types.
    """)

# ------------------ Simulation Tab ------------------
with tab2:
    st.header("PI Simulation")
    Kp = st.number_input("Proportional Gain (Kp)", value=2.0)
    Ki = st.number_input("Integral Gain (Ki)", value=0.5)
    Imax = st.number_input("Max Integral (Imax)", value=50.0)
    SP = st.number_input("Setpoint (SP)", value=25.0)
    FB = st.number_input("Feedback (FB)", value=20.0)

    steps = 100
    dt = 1
    I = 0
    outputs, errors = [], []

    for _ in range(steps):
        error = SP - FB
        P = Kp * error
        I += Ki * error * dt
        I = np.clip(I, -Imax, Imax)
        output = P + I
        outputs.append(output)
        errors.append(error)
        FB += output * 0.01

    st.line_chart(pd.DataFrame({"Output": outputs, "Error": errors}))

# ------------------ CSV Tuning Tab ------------------
with tab3:
    st.header("CSV Tuning Upload & Comparison")
    uploaded_file = st.file_uploader("Upload a CSV with columns: Kp, Ki, Imax", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df)
        fig, ax = plt.subplots()
        ax.plot(df["Kp"], label="Kp")
        ax.plot(df["Ki"], label="Ki")
        ax.plot(df["Imax"], label="Imax")
        ax.legend()
        st.pyplot(fig)

# ------------------ Alerton Tab ------------------
with tab4:
    st.header("Alerton Control Strategies")
    st.markdown("*(Alerton presets functionality placeholder – you can add your presets here)*")

# ------------------ Niagara 4 PID Tab ------------------
with tab5:
    st.header("Niagara 4 PID Tuning")
    st.markdown("<div style='background-color:#0a2a5e; padding:15px; border-radius:10px;'>", unsafe_allow_html=True)

    niagara_type = st.selectbox("Select Control Type:", ["Heating", "Cooling", "Pressure", "Damper"])
    loop_action = st.radio("Loop Action:", ["Direct", "Reverse"])

    niagara_tuning = {
        "Heating": {"Direct": {"Kp": 2.0, "Ki": 0.5, "Kd": 0.1},
                    "Reverse": {"Kp": 1.8, "Ki": 0.4, "Kd": 0.08}},
        "Cooling": {"Direct": {"Kp": 1.5, "Ki": 0.3, "Kd": 0.05},
                    "Reverse": {"Kp": 1.2, "Ki": 0.25, "Kd": 0.04}},
        "Pressure": {"Direct": {"Kp": 3.0, "Ki": 0.8, "Kd": 0.2},
                     "Reverse": {"Kp": 2.5, "Ki": 0.7, "Kd": 0.15}},
        "Damper": {"Direct": {"Kp": 1.0, "Ki": 0.2, "Kd": 0.05},
                   "Reverse": {"Kp": 0.9, "Ki": 0.15, "Kd": 0.04}}
    }

    tuning = niagara_tuning[niagara_type][loop_action]
    st.subheader(f"{niagara_type} PID Constants ({loop_action})")
    st.code(tuning, language="json")

    st.markdown("</div>", unsafe_allow_html=True)
