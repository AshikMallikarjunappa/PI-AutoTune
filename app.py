import streamlit as st
import numpy as np

st.title("PI Autotune Tool")

# Create two tabs: Directions and Simulation
tab1, tab2 = st.tabs(["Directions", "Simulation"])

# ------------------ Directions Tab ------------------
with tab1:
    st.header("How to Use the PI Autotune Tool")
    st.markdown("""
Welcome to the **PI Autotune Tool**! This app lets you simulate a PI controller and understand how the proportional and integral terms affect the output.

---

### Step 1: Enter Inputs
Use the **sidebar** to enter:

- **Feedback (FB):** Current measured value (e.g., temperature)  
- **Setpoint (SP):** Target value  
- **Proportional constant (Kp):** How strongly the controller reacts  
- **Integral constant (Ki):** Accumulates past error  
- **Max integral change (IMX):** Max allowed per-second change  
- **Integral startup (STUP):** Initial integral value  
- **Integral limit (ILMT):** Maximum absolute integral  

---

### Step 2: How Calculations Work
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

### Tips:
- Start with small Kp/Ki values to avoid overshoot  
- Use IMX and ILMT to prevent windup  
- Adjust STUP if starting from non-zero integral  

Happy tuning! 🚀
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
