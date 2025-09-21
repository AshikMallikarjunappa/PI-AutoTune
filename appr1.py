import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="PI Loop Tuning Tool", layout="wide")

# ------------------ Tabs ------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Directions", "Simulation", "CSV Tuning", "Alerton Presets", "Niagara 4 Presets"]
)

# ------------------ Directions Tab ------------------
with tab1:
    st.title("PI Loop Tuning Tool")
    st.markdown("""
    ### Instructions:
    - Use **Simulation** tab to test PI control response.
    - Use **CSV Tuning** tab to upload tuning values and visualize results.
    - Use **Alerton Presets** or **Niagara 4 Presets** tab to quickly select standard tuning strategies.
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
    st.markdown("Select a control strategy and adjust Response Speed.")

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

    # --- STUP Logic ---
    if selected in ["Standard Zone Heating Signal", "Standard Zone Cooling Signal"]:
        STUP = -30 if DA == 1 else 30
    elif selected == "Standard Supply DSP Control":
        STUP = -30 if DA == 1 else 30
    elif selected == "Standard BSP Fan Control":
        STUP = 0
    else:
        STUP = -50 if DA == 1 else 50

    # Scale values
    scaled_params = {
        "Kp": round(params["Kp"] * response_speed, 3),
        "Ki": round(params["Ki"] * response_speed, 3),
        "Imax": round(params["Imax"] * response_speed, 3),
        "Ilimit": params["Ilimit"],
        "STUP": STUP
    }

    st.subheader(f"{selected} Parameters (scaled by Response Speed)")
    st.json(scaled_params)

    # --- PI Calculation ---
    st.subheader("Controller Output Calculation")
    FB = st.number_input("Feedback (FB)", value=22.0, key="alerton_fb")
    SP = st.number_input("Setpoint (SP)", value=24.0, key="alerton_sp")

    if DA == 1:  # Direct Acting
        E = SP - FB
    else:  # Reverse Acting
        E = FB - SP

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

# ------------------ Niagara 4 Tab ------------------
with tab5:
    st.header("Niagara 4 Presets")
    st.markdown("Select a Niagara strategy and adjust Response Speed.")

    controls_n4 = {
        "N4 Zone Heating Loop": {"Kp": 12, "Ki": 1, "Imax": 3, "Ilimit": 50},
        "N4 Zone Cooling Loop": {"Kp": 12, "Ki": 1, "Imax": 3, "Ilimit": 50},
        "N4 Economizer Loop": {"Kp": 0.6, "Ki": 1.5, "Imax": 60, "Ilimit": 50},
        "N4 Supply DSP Loop": {"Kp": 0, "Ki": 30, "Imax": 60, "Ilimit": 50},
        "N4 Heating Valve SAT": {"Kp": 0.6, "Ki": 1.5, "Imax": 60, "Ilimit": 50},
        "N4 BSP Fan Loop": {"Kp": 0, "Ki": 25, "Imax": 20, "Ilimit": 50}
    }

    selected_n4 = st.selectbox("Select Niagara strategy:", list(controls_n4.keys()))
    params_n4 = controls_n4[selected_n4]

    response_speed_n4 = st.slider("Response Speed (Slow ↔ Fast)", 0.5, 2.0, 1.0, 0.1, key="n4_speed")

    da_choice_n4 = st.radio("Control Action (N4):", ["Direct Acting", "Reverse Acting"], key="n4_da")
    DA_n4 = 1 if da_choice_n4 == "Direct Acting" else 0

    # --- STUP Logic for Niagara ---
    if selected_n4 in ["N4 Zone Heating Loop", "N4 Zone Cooling Loop"]:
        STUP_n4 = -30 if DA_n4 == 1 else 30
    elif selected_n4 == "N4 Supply DSP Loop":
        STUP_n4 = -30 if DA_n4 == 1 else 30
    elif selected_n4 == "N4 BSP Fan Loop":
        STUP_n4 = 0
    else:
        STUP_n4 = -50 if DA_n4 == 1 else 50

    # Scale values
    scaled_params_n4 = {
        "Kp": round(params_n4["Kp"] * response_speed_n4, 3),
        "Ki": round(params_n4["Ki"] * response_speed_n4, 3),
        "Imax": round(params_n4["Imax"] * response_speed_n4, 3),
        "Ilimit": params_n4["Ilimit"],
        "STUP": STUP_n4
    }

    st.subheader(f"{selected_n4} Parameters (scaled by Response Speed)")
    st.json(scaled_params_n4)

    # --- PI Calculation ---
    st.subheader("Controller Output Calculation (Niagara)")
    FB_n4 = st.number_input("Feedback (FB)", value=22.0, key="n4_fb_input")
    SP_n4 = st.number_input("Setpoint (SP)", value=24.0, key="n4_sp_input")

    if DA_n4 == 1:  # Direct Acting
        E_n4 = SP_n4 - FB_n4
    else:  # Reverse Acting
        E_n4 = FB_n4 - SP_n4

    P_n4 = scaled_params_n4["Kp"] * E_n4

    if "Iprev_n4" not in st.session_state:
        st.session_state.Iprev_n4 = scaled_params_n4["STUP"]

    Iinc_n4 = (scaled_params_n4["Ki"] * E_n4) / 60.0
    Iinc_n4 = np.clip(Iinc_n4, -scaled_params_n4["Imax"] / 60.0, scaled_params_n4["Imax"] / 60.0)
    I_n4 = st.session_state.Iprev_n4 + Iinc_n4
    I_n4 = np.clip(I_n4, -scaled_params_n4["Ilimit"], scaled_params_n4["Ilimit"])
    st.session_state.Iprev_n4 = I_n4

    Output_n4 = P_n4 + I_n4 + 50

    st.write(f"Error (E): {E_n4:.2f}")
    st.write(f"Proportional (P): {P_n4:.2f}")
    st.write(f"Integral (I): {I_n4:.2f}")
    st.write(f"**Controller Output: {Output_n4:.2f}**")
