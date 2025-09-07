import matplotlib.pyplot as plt

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

        # ----------------- Plot Current vs Suggested PI -----------------
        st.subheader("Performance Chart: Current PI vs Suggested PI")

        # Simulate response with suggested PI (simple incremental model)
        sim_feedback = [df["Feedback"].iloc[0]]
        I_term = 0
        for sp, fb in zip(df["Setpoint"], sim_feedback[-1:] + list(df["Feedback"].iloc[1:])):
            e = sp - sim_feedback[-1]
            P = suggested_Kp * e
            I_term += suggested_Ki * e
            new_fb = sim_feedback[-1] + 0.1 * (P + I_term)  # simplified plant response
            sim_feedback.append(new_fb)

        df["Simulated_PI"] = sim_feedback[:len(df)]

        # Plot
        fig, ax = plt.subplots(figsize=(10,5))
        ax.plot(df["Time"], df["Feedback"], label="Current Feedback", color="blue")
        ax.plot(df["Time"], df["Setpoint"], label="Setpoint", color="green", linestyle="--")
        ax.plot(df["Time"], df["Simulated_PI"], label="Simulated with Suggested PI", color="red")
        ax.set_xlabel("Time")
        ax.set_ylabel("Value")
        ax.legend()
        ax.grid(True)

        st.pyplot(fig)

    else:
        st.error("CSV must contain 'Time', 'Feedback', and 'Setpoint' columns")
