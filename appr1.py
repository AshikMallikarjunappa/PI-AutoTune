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
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    h1 {
        color: #0a3d62;
        text-align: center;
        font-weight: 700;
        font-size: 3rem;
        margin-bottom: 0.3rem;
    }
    .stButton>button {
        background: linear-gradient(90deg,#0fbcf9,#1e90ff);
        color: white;
        border-radius: 10px;
        height: 3em;
    }
    .stSlider>div>div>div>div>div {
        color: #1e90ff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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
        FB += output * 0.01  # process response

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
    controls = {
        "Standard Zone Heating Signal": {"Kp": 12, "Ki": 1, "Imax": 3, "Ilimit": 50},
        "Standard Zone Cooling Signal": {"Kp": 12, "Ki": 1, "Imax": 3, "Ilimit": 50},
        "Standard Economizer Control": {"Kp": 0.6, "Ki": 1.5, "Imax": 60, "Ilimit": 50},
        "Standard Supply DSP Control": {"Kp": 0, "Ki": 30, "Imax": 60, "Ilimit": 50},
        "Standard SAT Heating Valve": {"Kp": 0.6, "Ki": 1.5, "Imax": 60, "Ilimit": 50},
        "Standard BSP Fan Control": {"Kp": 0, "Ki": 25, "Imax": 20, "Ilimit": 50}
    }

    selected = st.selectbox("Select control strategy:", list(controls.keys()))
    params = controls[selected]
    response_speed = st.slider("Response Speed (Slow ↔ Fast)", 0.5, 2.0, 1.0, 0.1)
    da_choice = st.radio("Control Action:", ["Direct Acting", "Reverse Acting"])
    DA = 1 if da_choice == "Direct Acting" else 0

    if selected in ["Standard Zone Heating Signal", "Standard Zone Cooling Signal"]:
        STUP = -30 if DA == 1 else 30
    elif selected == "Standard Supply DSP Control":
        STUP = -30 if DA == 1 else 30
    elif selected == "Standard BSP Fan Control":
        STUP = 0
    else:
        STUP = -50 if DA == 1 else 50

    scaled_params = {
        "Kp": round(params["Kp"] * response_speed, 3),
        "Ki": round(params["Ki"] * response_speed, 3),
        "Imax": round(params["Imax"] * response_speed, 3),
        "Ilimit": params["Ilimit"],
        "STUP": STUP
    }

    st.subheader(f"{selected} Parameters (scaled by Response Speed)")
    st.json(scaled_params)

    FB = st.number_input("Feedback (FB)", value=22.0, key="alerton_fb")
    SP = st.number_input("Setpoint (SP)", value=24.0, key="alerton_sp")
    E = SP - FB if DA == 1 else FB - SP
    P = scaled_params["Kp"] * E
    if "Iprev_alerton" not in st.session_state:
        st.session_state.Iprev_alerton = scaled_params["STUP"]
    Iinc = (scaled_params["Ki"] * E) / 60.0
    Iinc = np.clip(Iinc, -scaled_params["Imax"] / 60.0, scaled_params["Imax"] / 60.0)
    I = st.session_state.Iprev_alerton + Iinc
    I = np.clip(I, -scaled_params["Ilimit"], scaled_params["Ilimit"])
    st.session_state.Iprev_alerton = I
    Output = P + I + 50
    st.write(f"Error (E): {E:.2f}")
    st.write(f"Proportional (P): {P:.2f}")
    st.write(f"Integral (I): {I:.2f}")
    st.write(f"**Controller Output: {Output:.2f}**")

# ------------------ Niagara 4 PID Tab ------------------
with tab5:
    st.header("Niagara 4 PID Tuning")
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
    st.json(tuning)
