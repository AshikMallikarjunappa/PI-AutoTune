import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="PI Autotune Tool", layout="wide")
st.title("PI Autotune Tool")

# ------------------ Tabs ------------------
tab1, tab2, tab3 = st.tabs(["Directions", "Simulation", "CSV Tuning"])

# ------------------ Directions Tab ------------------
with tab1:
    st.header("How to Use the PI Autotune Tool")
    st.markdown("""
Welcome to the **PI Autotune Tool**! This app lets you simulate a PI controller and understand how the proportional and integral terms affect the output.
import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="PI Autotune Tool", layout="wide")
st.title("PI Autotune Tool")

# ------------------ Tabs ------------------
tab1, tab2, tab3, tab4 = st.tabs(["Directions", "Simulation", "CSV Tuning", "Alerton"])

# ------------------ Directions Tab ------------------
with tab1:
    st.header("How to Use the PI Autotune Tool")
    st.markdown("""
Welcome to the **PI Autotune Tool**! This app lets you simulate a PI controller and understand how the proportional and integral terms affect the output.

- **Simulation Tab**: manually test PI values  
- **CSV Tuning Tab**: upload logged data to get suggested PI values with feedback  
- **Alerton Tab**: explore default Alerton control strategies with sliders
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
The app will suggest **Kp** and **Ki**, and provide feedback on the system behavior.
""")

    start_time = datetime(2025, 8, 10, 14, 20)
    times = [start_time + timedelta(seconds=i) for i in range(3000)]

    np.random.seed(0)
    feedback = 22 + np.cumsum(np.random.randn(3000) * 0.05)
    setpoint = np.full(3000, 24.0)

    df_template = pd.DataFrame({
        "Time": [dt.strftime("%-m/%-d/%Y %H:%M") for dt in times],
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

            sim_feedback = [df["Feedback"].iloc[0]]
            I_term = 0.0
            for sp in df["Setpoint"]:
                e = sp - sim_feedback[-1]
                P = suggested_Kp * e
                I_term += suggested_Ki * e
                new_fb = sim_feedback[-1] + 0.1 * (P + I_term)
                sim_feedback.append(new_fb)

            df["Simulated_PI"] = sim_feedback[:len(df)]

            st.subheader("Performance Chart: Current PI vs Suggested PI")
            st.line_chart(df[["Feedback", "Setpoint", "Simulated_PI"]], use_container_width=True)

        else:
            st.error("CSV must contain 'Time', 'Feedback', and 'Setpoint' columns")

# ------------------ Alerton Tab ------------------
with tab4:
    st.header("Alerton Control Strategies")
    st.markdown("Adjust parameters for different standard Alerton control strategies using the sliders below.")

    controls = {
        "Standard Zone Heating Signal": dict(DirectActing=0, FeedbackResponse=-23, SmallestSetptInc=0.5, UseKp=1, UseKi=1, OutputResponse=2000, Ilimit=50, StartPosition=20, KpVal=12, KiVal=1, ImaxVal=3, IlimitVal=50, StupVal=30),
        "Standard Zone Cooling Signal": dict(DirectActing=1, FeedbackResponse=-23, SmallestSetptInc=0.5, UseKp=1, UseKi=1, OutputResponse=2000, Ilimit=50, StartPosition=20, KpVal=12, KiVal=1, ImaxVal=3, IlimitVal=50, StupVal=-30),
        "Standard Economizer Control": dict(DirectActing=1, FeedbackResponse=6, SmallestSetptInc=2.5, UseKp=1, UseKi=1, OutputResponse=100, Ilimit=50, StartPosition=0, KpVal=0.6, KiVal=1.5, ImaxVal=60, IlimitVal=50, StupVal=-50),
        "Standard Supply DSP Control": dict(DirectActing=0, FeedbackResponse=0, SmallestSetptInc=0.1, UseKp=0, UseKi=1, OutputResponse=100, Ilimit=50, StartPosition=20, KpVal=0, KiVal=30, ImaxVal=60, IlimitVal=50, StupVal=30),
        "Standard SAT Heating Valve": dict(DirectActing=0, FeedbackResponse=6, SmallestSetptInc=2.5, UseKp=1, UseKi=1, OutputResponse=100, Ilimit=50, StartPosition=0, KpVal=0.6, KiVal=1.5, ImaxVal=60, IlimitVal=50, StupVal=50),
        "Standard BSP Fan Control": dict(DirectActing=1, FeedbackResponse=-23, SmallestSetptInc=0.01, UseKp=0, UseKi=1, OutputResponse=300, Ilimit=50, StartPosition=50, KpVal=0, KiVal=25, ImaxVal=20, IlimitVal=50, StupVal=0),
    }

    selected = st.selectbox("Choose a control strategy:", list(controls.keys()))
    params = controls[selected]

    st.subheader(f"{selected} Parameters")
    for key, val in params.items():
        if isinstance(val, int) or isinstance(val, float):
            params[key] = st.slider(key, min_value=-100 if val < 0 else 0, max_value=int(val * 2 + 50), value=float(val))
        else:
            st.write(f"**{key}:** {val}")

    st.json(params)

- **Simulation Tab**: manually test PI values  
- **CSV Tuning Tab**: upload logged data to get suggested PI values with feedback
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
The app will suggest **Kp** and **Ki**, and provide feedback on the system behavior.
""")

    # ------------------ CSV Template with 3000 rows ------------------
    start_time = datetime(2025, 8, 10, 14, 20)
    times = [start_time + timedelta(seconds=i) for i in range(3000)]

    np.random.seed(0)
    feedback = 22 + np.cumsum(np.random.randn(3000) * 0.05)  # small random walk
    setpoint = np.full(3000, 24.0)  # constant setpoint

    df_template = pd.DataFrame({
        "Time": [dt.strftime("%-m/%-d/%Y %H:%M") for dt in times],
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

    # ------------------ File Uploader ------------------
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

            # ----------------- Simulated PI Response -----------------
            sim_feedback = [df["Feedback"].iloc[0]]
            I_term = 0.0
            for sp in df["Setpoint"]:
                e = sp - sim_feedback[-1]
                P = suggested_Kp * e
                I_term += suggested_Ki * e
                new_fb = sim_feedback[-1] + 0.1 * (P + I_term)  # simple plant model
                sim_feedback.append(new_fb)

            df["Simulated_PI"] = sim_feedback[:len(df)]

            # ----------------- Chart -----------------
            st.subheader("Performance Chart: Current PI vs Suggested PI")
            st.line_chart(df[["Feedback", "Setpoint", "Simulated_PI"]], use_container_width=True)

        else:
            st.error("CSV must contain 'Time', 'Feedback', and 'Setpoint' columns")
