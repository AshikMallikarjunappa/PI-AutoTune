import streamlit as st
import numpy as np
import pandas as pd

st.title("PI Autotune Tool")

# Tabs: Directions, Simulation, CSV Tuning
tab1, tab2, tab3 = st.tabs(["Directions", "Simulation", "CSV Tuning"])

# ------------------ Directions Tab ------------------
with tab1:
    st.header("How to Use the PI Autotune Tool")
    st.markdown("""
Welcome to the **PI Autotune Tool**! This app lets you simulate a PI controller and understand how the proportional and integral terms affect the output.

- Use **Simulation** to manually test PI values.  
- Use **CSV Tuning** to upload logged data and get recommended PI settings.
""")

# ------------------ Simulation Tab ------------------
with tab2:
    st.sidebar.header("Inputs")
    FB = st.sidebar.number_input("Feedback (FB)", value=22.0)
    SP = st.sidebar.number_input("Setpoint (SP)", value=24.0)
    Kp = st.sidebar.number_input("Proportional constant (Kp)", value=1.0)
    Ki = st.sidebar.number_input("Integral constant (Ki)", value=0.1)
    IMX = st.sidebar.number_input("Max integral change (IMX)", value=10.0)
    STUP = st.sidebar.number_input("Integral startup (STUP)", value=0.0)
    ILMT = st.sidebar.number_input("Integral limit (ILMT)", value=100.0)

    # Initialize integral state
    if "Iprev" not in st.session_state:
        st.session_state.Iprev = STUP

    # Step 1: Error
    E = FB - SP

    # Step 2: Proportional term
    P = Kp * E

    # Step 3: Integral term
    if Ki == 0:
        Iinc = 0.0
        I = STUP
    else:
        Iinc = (Ki * E) / 60.0
        Iinc = np.clip(Iinc, -IMX / 60.0, IMX / 60.0)
        I = st.session_state.Iprev + Iinc
        I = np.clip(I, -ILMT, ILMT)

    st.session_state.Iprev = I

    # Step 4: Output
    Output = P + I + 50

    # Display results
    st.subheader("Results")
    st.write(f"Error (E): {E:.2f}")
    st.write(f"Proportional (P): {P:.2f}")
    st.write(f"Integral increment (Iinc): {Iinc:.4f}")
    st.write(f"Integral (I): {I:.2f}")
    st.write(f"Output: {Output:.2f}")

# ------------------ CSV Tuning Tab ------------------
with tab3:
    st.header("Upload Logged Data for PI Suggestion")
    st.markdown("""
Upload a CSV with columns like:  
`Time, Feedback, Setpoint`  
The app will analyze the error trend and suggest initial **Kp** and **Ki** values.
""")
    uploaded_file = st.file_uploader("Upload CSV", type="csv")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("Preview of your data:")
        st.dataframe(df.head())

        if all(col in df.columns for col in ["Time", "Feedback", "Setpoint"]):
            # Simple PI suggestion logic
            error = df["Setpoint"] - df["Feedback"]
            delta_fb = df["Feedback"].diff().abs().mean()  # average feedback change
            delta_error = error.diff().abs().mean()

            # Suggested Kp and Ki (simple heuristic)
            suggested_Kp = round(delta_error / (delta_fb + 1e-6), 2)
            suggested_Ki = round(suggested_Kp / 10, 3)  # smaller integral

            st.success("Suggested PI values based on uploaded data:")
            st.write(f"**Kp:** {suggested_Kp}")
            st.write(f"**Ki:** {suggested_Ki}")
        else:
            st.error("CSV must contain 'Time', 'Feedback', and 'Setpoint' columns")
