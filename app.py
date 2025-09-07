import streamlit as st
import numpy as np
import pandas as pd
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

---

### Step 1: Enter Inputs
Use the **Simulation** tab to manually enter:

- **Feedback (FB):** Current measured value (e.g., temperature)  
- **Setpoint (SP):** Target value  
- **Proportional constant (Kp):** How strongly the controller reacts  
- **Integral constant (Ki):** Accumulates past error  
- **Max integral change (IMX):** Max allowed per-second change  
- **Integral startup (STUP):** Initial integral value  
- **Integral limit (ILMT):** Maximum absolute integral  

---

### Step 2: Understand Calculations
1. **Error (E):** Difference between FB and SP  
2. **Proportional (P):** `Kp * E`  
3. **Integral (I):** Cumulative correction, limited by `IMX` and `ILMT`  
4. **Output:** `P + I + 50`

---

### Step 3: Review Results
You'll see:

- **Error (E)**  
- **Proportional (P)**  
- **Integral increment (Iinc)**  
- **Integral term (I)**  
- **Controller Output**

---

### Step 4: CSV Tuning (Optional)
- Upload your logged CSV with columns: `Time, Feedback, Setpoint`  
- The app will suggest initial **Kp** and **Ki** values.  
- Download a CSV template to fill in your data.

---

### Tips:
- Start with small Kp/Ki values to avoid overshoot  
- Use IMX and ILMT to prevent windup  
- Adjust STUP if starting from non-zero integral  

Happy tuning! 🚀
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

    # Step 1: Error
    E = FB - SP
    # Step 2: Proportional
    P = Kp * E
    # Step 3: Integral
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
The app will suggest **Kp** and **Ki**, provide feedback, and plot the response.
""")

    # CSV Template
    template_df = pd.DataFrame({
        "Time": ["00:00:00", "00:00:01", "00:00:02"],
        "Feedback": [22.0, 22.1, 22.3],
        "Setpoint": [24.0, 24.0, 24.0]
    })
    csv_template = template_df.to_csv(index=False)
    st.download_button(
        label="Download CSV Template",
        data=csv_template,
        file_name="pi_logged_data_template.csv",
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

            # Suggested Kp/Ki
            suggested_Kp = round(delta_error / (delta_fb + 1e-6), 2)
            suggested_Ki = round(suggested_Kp / 10, 3)

            st.success("Suggested PI values:")
            st.write(f"**Kp:** {suggested_Kp}")
            st.write(f"**Ki:** {suggested_Ki}")

            # User Feedback
            st.subheader("Feedback / Analysis")
            avg_error = error.abs().mean()
            st.write(f"Average Error: {avg_error:.2f}")

            if avg_error < 0.5:
                st.info("✅ System is stable; only minor corrections needed.")
            elif avg_error < 2:
                st.info("⚠️ Moderate error; PI tuning may improve stability.")
            else:
                st.warning("❌ Large error; system may need higher Kp/Ki.")

            if suggested_Kp > 5:
                st.warning("⚡ Kp is strong; watch for overshoot.")
            elif suggested_Kp < 0.5:
                st.info("ℹ️ Kp is small; response may be slow.")

            if suggested_Ki > 1:
                st.warning("🌀 Ki is strong; watch for oscillations.")
            elif suggested_Ki < 0.05:
                st.info("ℹ️ Ki is small; integral effect may be slow.")

            # Simulate PI output for visualization
            I_sim = [0]
            Output_sim = []
            for fb in df["Feedback"]:
                E_step = df["Setpoint"].iloc[0] - fb
                I_inc = (suggested_Ki * E_step) / 60.0
                I_new = np.clip(I_sim[-1] + I_inc, -100, 100)
                I_sim.append(I_new)
                Output_sim.append(suggested_Kp * E_step + I_new + 50)

            # Plot Feedback vs Setpoint vs Output
            plt.figure(figsize=(10, 4))
            plt.plot(df["Time"], df["Setpoint"], label="Setpoint", linestyle="--")
            plt.plot(df["Time"], df["Feedback"], label="Feedback")
            plt.plot(df["Time"], Output_sim, label="Simulated PI Output")
            plt.xticks(rotation=45)
            plt.xlabel("Time")
            plt.ylabel("Value")
            plt.title("PI Response Visualization")
            plt.legend()
            plt.tight_layout()
            st.pyplot(plt)
        else:
            st.error("CSV must contain 'Time', 'Feedback', and 'Setpoint' columns")
