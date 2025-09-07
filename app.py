import streamlit as st
import numpy as np

st.title("PI Autotune Tool")

# Sidebar inputs
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
    # Per-second increment (Ki is per minute)
    Iinc = (Ki * E) / 60.0
    # Limit increment to ±IMX/60
    Iinc = np.clip(Iinc, -IMX / 60.0, IMX / 60.0)
    # Update integral
    I = st.session_state.Iprev + Iinc
    # Clamp integral to ±ILMT
    I = np.clip(I, -ILMT, ILMT)

# Update stored integral
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
