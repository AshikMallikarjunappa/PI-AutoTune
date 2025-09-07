# ------------------ CSV Tuning Tab ------------------
with tab3:
    st.header("CSV Tuning: Suggest PI Values")
    st.markdown("""
Upload a CSV with columns: `Time, Feedback, Setpoint`  
Time format example: `8/10/2025 14:20`  
The app will suggest **Kp** and **Ki**, and provide feedback on the system behavior.
""")

    # CSV Template with datetime format
    template_df = pd.DataFrame({
        "Time": ["8/10/2025 14:20", "8/10/2025 14:21", "8/10/2025 14:22"],
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

        # Parse Time column as datetime
        df["Time"] = pd.to_datetime(df["Time"], format="%m/%d/%Y %H:%M")

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

            # Optional: use datetime for plotting
            import matplotlib.pyplot as plt
            I_sim = [0]
            Output_sim = []
            for fb in df["Feedback"]:
                E_step = df["Setpoint"].iloc[0] - fb
                I_inc = (suggested_Ki * E_step) / 60.0
                I_new = np.clip(I_sim[-1] + I_inc, -100, 100)
                I_sim.append(I_new)
                Output_sim.append(suggested_Kp * E_step + I_new + 50)

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
