import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

st.set_page_config(page_title="PI Autotune Tool", layout="wide")
st.title("PI Autotune Tool")

# ------------------ Tabs ------------------
tab1, tab2, tab3 = st.tabs(["Directions", "Simulation", "CSV Tuning"])

# ------------------ Directions Tab ------------------
with tab1:
    st.header("How to Use the PI Autotune Tool")
    st.markdown("""
Welcome to the **PI Autotune Tool**! This app lets you simulate a PI controller and understand how the proportional and integral terms affect the output.

- **Simulation Tab**: manually test PI values  
- **CSV Tuning Tab**: upload logged data to get suggested PI values with feedback and see a visual comparison of controller response.
""")

# ------------------ Simulation Tab ------------------
with tab2:
    st.sidebar.header("Simulation Inputs")
    FB = st.sidebar.number_input("Feedback (FB)", value=22.0)
    SP = st.sidebar.number_input("Setpoint (SP)", value=24.0)
    Kp = st.sidebar.number_input("Proportional constant (Kp)", value=1.0)
    Ki = st.sidebar.number_input("Integral constant (Ki)", value=0.1)
    IMX = st.sidebar.number_input("Max integral change (IMX)", value=10.0)
    STUP = st.sidebar.number_input("Integral startup (STUP)", value=0.0)
    ILMT = st.sidebar.number_input("Integral limit (ILMT)", value=100.0)

    if "Iprev" not in st.session_state:
        st.session_state.Iprev = STUP

    E = FB - SP
    P = Kp * E

    if Ki == 0:
        Iinc = 0.0
        I = STUP
    else:
        Iinc = (Ki * E) / 60.0
        Iinc = np.clip(Iinc, -IMX / 60.0, IMX / 60.0)
        I = st.session_state.Iprev + Iinc
        I = np.clip(I, -ILMT, ILMT)

    st.session_state.Iprev = I
    Output = P + I + 50

    st.subheader("Simulation Results")
    st.write(f"Error (E): {E:.2f}")
    st.write(f"Proportional (P): {P:.2f}")
    st.write(f"Integral increment (Iinc): {Iinc:.4f}")
    st.write(f"Integral (I): {I:.2f}")
    st.write(f"Controller Output: {Output:.2f}")

# ------------------ CSV Tuning Tab ------------------
with tab3:
    st.header("CSV Tuning: Suggest PI Values")
    st.markdown("""
Upload a CSV with columns: `Time, Feedback, Setpoint`  
The app will suggest **Kp** and **Ki**, and provide feedback on the system behavior and compare PI responses.
""")

    # ------------------ CSV Template with 3000 rows ------------------
    start_time = datetime(2025, 8, 10, 14, 20)
    times = [start_time + timedelta(seconds=i) for i in range(3000)]

    np.random.seed(0)
    feedback = 22 + np.cumsum(np.random.randn(3000)*0.05)  # small random walk
    setpoint = np.full(3000, 24.0)  # constant setpoint

    df_template = pd.DataFrame({
        "Time": [dt.strftime("%-m/%-d/%Y %H:%M:%S") for dt in times],
        "Feedback": feedback.round(2),
        "Setpoint": setpoint
    })

    csv_template_3000 = df_template.to_csv(index=False)
    st.download_button(
        label="Download CSV Template",
        data=csv_template_3000,
        file_name="pi_logged_data_template_3000.csv",
        mime="text/csv"
    )

    uploaded_file = st.file_uploader("Upload your CSV", type="csv")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("Preview of uploaded data:")
        st.dataframe(df.head())

        if all(col in df.columns for col in ["Time", "Feedback", "Setpoint"]):
            error = df["Setpoint"] - df["Feedback"]
            delta_fb = df["Feedback"].diff().abs().mean()
            delta_error = error.diff().abs().mean()

            suggested_Kp = round(delta_error / (delta_fb + 1e-6), 2)
            suggested_Ki = round(suggested_Kp / 10, 3)

            st.success("Suggested PI values:")
            st.write(f"**Kp:** {suggested_Kp}")
            st.write(f"**Ki:** {suggested_Ki}")

            # ----------------- User Feedback -----------------
            st.subheader("Feedback / Analysis:")
            avg_error = error.abs().mean()
            st.write(f"Average Error: {avg_error:.2f}")

            if avg_error < 0.5:
                st.info("✅ Your system is stable; only small corrections are needed.")
            elif avg_error < 2:
                st.info("⚠️ Moderate error detected; PI tuning may improve stability.")
            else:
                st.warning("❌ Large error detected; system may need higher Kp or Ki.")

            if suggested_Kp > 5:
                st.warning("⚡ Kp is strong; monitor for overshoot.")
            elif suggested_Kp < 0.5:
                st.info("ℹ️ Kp is small; system response may be slow.")

            if suggested_Ki > 1:
                st.warning("🌀 Ki is strong; watch for oscillations.")
            elif suggested_Ki < 0.05:
                st.info("ℹ️ Ki is small; integral effect may be slow.")

            # ----------------- Plot PI response using Matplotlib -----------------
            I_suggested = 0.0
            Output_suggested = []
            FB_series = df["Feedback"].values
            SP_series = df["Setpoint"].values

            for FB_i, SP_i in zip(FB_series, SP_series):
                E_i = SP_i - FB_i
                P_i = suggested_Kp * E_i
                I_suggested += suggested_Ki * E_i / 60.0
                Output_suggested.append(P_i + I_suggested + 50)

            # Previous PI (rough estimation)
            I_orig = 0.0
            Output_orig = []
            for FB_i, SP_i in zip(FB_series, SP_series):
                E_i = SP_i - FB_i
                P_i = (delta_error / (delta_fb + 1e-6)) * E_i if delta_fb != 0 else 0
                I_orig += (suggested_Ki * E_i / 60.0)
                Output_orig.append(P_i + I_orig + 50)

            # Plot
            fig, ax = plt.subplots(figsize=(12, 4))
            ax.plot(df["Time"], Output_orig, label="Previous PI Response")
            ax.plot(df["Time"], Output_suggested, label="Suggested PI Response")
            ax.set_xlabel("Time")
            ax.set_ylabel("Controller Output")
            ax.set_title("PI Controller Response Comparison")
            ax.legend()
            plt.xticks(rotation=45)
            st.pyplot(fig)

        else:
            st.error("CSV must contain 'Time', 'Feedback', and 'Setpoint' columns")
