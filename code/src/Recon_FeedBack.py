import streamlit as st
import pandas as pd
import json
import os


def save_feedback(feedback_log):
    try:
        feedback_file_path = os.path.join(os.getcwd(), 'feedback_log.json')
        st.write("Feedback File Path:", feedback_file_path)  # Show the file path

        # Check write permissions
        try:
            with open('feedback_log.json', 'w') as file:
                json.dump({"test": "write check"}, file)
            st.success("Write test successful!")
        except Exception as e:
            st.error(f"Error writing file: {e}")

        # Save feedback
        with open('feedback_log.json', 'w') as file:
            json.dump(feedback_log, file, indent=4)
        st.success("Feedback successfully saved!")
    except Exception as e:
        st.error(f"Failed to save feedback: {e}")


feedback_log = {}

st.title("Anomaly Feedback Tool")

# Load detected anomalies from CSV
anomaly_file = st.file_uploader("Upload CSV with Detected Anomalies:", type=["csv"])
anomalies = []

if anomaly_file is not None:
    data = pd.read_csv(anomaly_file)
    if 'Anomaly' in data.columns:
        anomalies = data[data['Anomaly'] == 1].index.tolist()

if anomalies:
    selected_anomaly = st.selectbox("Select an Anomaly:", anomalies)
    st.write("### Selected Anomaly Details:")
    st.dataframe(data.iloc[selected_anomaly])  # Show the full row of the selected anomaly

    feedback_type = st.selectbox("Feedback Type:", ["False Positive", "False Negative", "True Positive", "True Negative"])
    comments = st.text_area("Comments:")

    if st.button("Submit Feedback"):
        if selected_anomaly is not None and feedback_type:
            feedback_log[str(selected_anomaly)] = {
                "feedback_type": feedback_type,
                "comments": comments,
                "anomaly_details": data.iloc[selected_anomaly].to_dict()  # Log the anomaly details
            }
            save_feedback(feedback_log)
            st.success("Feedback submitted!")
        else:
            st.error("Please provide all required fields.")
else:
    st.warning("No detected anomalies found. Please upload a valid CSV.")
