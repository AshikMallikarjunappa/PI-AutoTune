import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ------------------ Page Config ------------------
st.set_page_config(page_title="PI Loop Autotune Tool by Ashik", layout="wide")

# ------------------ Display Title and Photo ------------------
st.title("PI Loop Autotune Tool by Ashik")

# Replace 'your_photo.jpg' with the actual path of your image
st.image("your_photo.jpg", caption="Ashik", use_column_width=True)

# ------------------ Tabs ------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Directions", "Simulation", "CSV Tuning", "Alerton Presets", "Niagara 4"]
)

# ------------------ Directions Tab ------------------
with tab1:
    st.header("Instructions")
    st.markdown("""
    - Use **Simulation** tab to test PI control response.
    - Use **CSV Tuning** tab to upload tuning values and visualize results.
    - Use **Alerton Presets** tab to quickly select standard tuning strategies.
    - Use **Niagara 4** tab to view tuned PID values for LoopPoint.
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

    st.subheader("Controller Output Calculation")
    FB = st.number_input("Feedback (FB)", value=22.0, key="alerton_fb")
    SP = st.number_input("Setpoint (SP)", value=24.0, key="alerton_sp")

    if DA == 1:
        E = SP - FB
    else:
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
    st.header("Niagara 4 LoopPoint Tuning")
    st.markdown("Select a Niagara 4 loop type and control action to view tuned PID values.")

    n4_loops = {
        "Zone Heating Loop": {"Direct": {"Kp": 12.0, "Ki": 0.8, "Kd": 0.5},
                              "Reverse": {"Kp": 12.0, "Ki": 0.8, "Kd": 0.5}},
        "Zone Cooling Loop": {"Direct": {"Kp": 14.0, "Ki": 1.0, "Kd": 0.6},
                              "Reverse": {"Kp": 14.0, "Ki": 1.0, "Kd": 0.6}},
        "Pressure Control Loop": {"Direct": {"Kp": 8.0, "Ki": 0.5, "Kd": 0.3},
                                  "Reverse": {"Kp": 8.0, "Ki": 0.5, "Kd": 0.3}},
        "Damper Control Loop": {"Direct": {"Kp": 10.0, "Ki": 0.7, "Kd": 0.4},
                                "Reverse": {"Kp": 10.0, "Ki": 0.7, "Kd": 0.4}},
        "Economizer Loop": {"Direct": {"Kp": 6.0, "Ki": 0.3, "Kd": 0.2},
                            "Reverse": {"Kp": 6.0, "Ki": 0.3, "Kd": 0.2}},
        "Supply DSP Loop": {"Direct": {"Kp": 5.0, "Ki": 0.5, "Kd": 0.2},
                            "Reverse": {"Kp": 5.0, "Ki": 0.5, "Kd": 0.2}}
    }

    selected_n4 = st.selectbox("Select Niagara Loop Type:", list(n4_loops.keys()))
    da_choice_n4 = st.radio("Loop Action:", ["Direct Acting", "Reverse Acting"])
    action_n4 = "Direct" if da_choice_n4 == "Direct Acting" else "Reverse"

    tuned_values = n4_loops[selected_n4][action_n4]

    st.subheader(f"Tuned PID Values for {selected_n4} ({da_choice_n4})")
    st.json(tuned_values)
