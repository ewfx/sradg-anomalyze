# import streamlit as st
import streamlit as st
import pandas as pd
import json
import os
import random
from deap import base, creator, tools, algorithms
import requests
from smtplib import SMTP
import smtplib


# Load configuration from config.json

def load_config():
    try:
        config_file = st.file_uploader("Upload Configuration File (recon_config.json)", type=['json'])
        if config_file is not None:
            config = json.load(config_file)
            st.success('Configuration loaded successfully.')
            return config
        else:
            st.warning('Upload a valid configuration file.')
            return {}
    except Exception as e:
        st.error(f'Failed to load configuration: {e}')
        return {}


# Data Ingestion using Config File

def load_anomalies(config):
    try:
        anomalies = pd.DataFrame()
        for recon_type, details in config.items():
            file_path = details.get('file_path')
            if file_path and os.path.exists(file_path):
                df = pd.read_csv(file_path)
                df['Reconciliation_Type'] = recon_type

                # Convert relevant columns to numeric
                for col in details.get('criteria_columns', []):
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '').str.strip(), errors='coerce')

                if recon_type == 'iHub_Reconciliation':
                    df['Recon_Frequency'] = 'Monthly'
                    df['As of Date'] = pd.to_datetime(df['As of Date'], errors='coerce')
                    month_ends = df.groupby(df['As of Date'].dt.to_period('M')).tail(1)
                    df = month_ends

                st.success(f"Loaded {recon_type} Data from {file_path}")
                st.dataframe(df)
                anomalies = pd.concat([anomalies, df], ignore_index=True)
            else:
                st.warning(f"File path for {recon_type} not found or not specified in the configuration.")

        return anomalies
    except Exception as e:
        st.error(f'Failed to load anomalies: {e}')
        return pd.DataFrame()


# Anomaly Detection with Enhanced Error Handling

def detect_anomalies(df, config):
    anomalies = pd.DataFrame()
    for recon_type, details in config.items():
        criteria_columns = details.get('criteria_columns', [])
        recon_df = df[df['Reconciliation_Type'] == recon_type].copy()

        for col in criteria_columns:
            if col in recon_df.columns:
                recon_df[col] = pd.to_numeric(recon_df[col].astype(str).str.replace(',', '').str.strip(), errors='coerce')

        if recon_type == 'iHub_Reconciliation':
            threshold = details.get('anomaly_threshold', 5000)
            grouped_df = recon_df.groupby(recon_df['As of Date'].dt.to_period('M'))

            for _, group in grouped_df:
                if not group.empty:
                    for col in criteria_columns:
                        breaks = group[col].diff().abs() > threshold
                        if breaks.any():
                            if breaks.sum() == group.shape[0] - 1:
                                group['Anomaly_Status'] = 'Not An Anomaly'
                            else:
                                group['Anomaly_Status'] = 'Anomaly'
                    anomalies = pd.concat([anomalies, group], ignore_index=True)

        elif recon_type == 'Catalyst_Reconciliation':
            threshold = details.get('anomaly_threshold', 1000)
            recon_df = recon_df.dropna(subset=criteria_columns)

            for col in criteria_columns:
                detected = recon_df[recon_df[col] > threshold]
                detected['Anomaly_Status'] = 'Anomaly'
                anomalies = pd.concat([anomalies, detected], ignore_index=True)

    st.write("Anomalies Detected:", len(anomalies))
    st.dataframe(anomalies)
    feedback_tool(anomalies)
    automate_resolution(anomalies)
    return anomalies


# Interactive Feedback Tool

def feedback_tool(anomalies):
    st.write("### Provide Feedback on Detected Anomalies")
    for idx, row in anomalies.iterrows():
        feedback = st.selectbox(f"Anomaly at index {idx} (Status: {row['Anomaly_Status']}):", ["Valid Anomaly", "False Positive", "Needs Review"], key=idx)


# Automating Resolution Tasks with Actual Calls

def automate_resolution(anomalies):
    for idx, row in anomalies.iterrows():
        severity = random.choice(['High', 'Medium', 'Low'])

        if severity == 'High':
            create_resolution_task(row)
            call_api(row)
            send_email(row)

        elif severity == 'Medium':
            send_email(row)



# Sample Automation Functions with Dummy API and Email Calls

def create_resolution_task(row):
    print(f"Creating ServiceNow incident for anomaly {row['Reconciliation_Type']}.")
    incident_data = {
        'short_description': f"Anomaly detected in {row['Reconciliation_Type']}",
        'description': f"Detailed anomaly info: {row.to_dict()}",
        'urgency': '2',
        'impact': '2'
    }
    try:
        response = requests.post("https://servicenow-instance.com/api/now/table/incident", json=incident_data)
        print(f"ServiceNow Incident Response: {response.status_code}")
    except Exception as e:
        print(f"Failed to create ServiceNow incident: {e}")


def call_api(row):
    print(f"Calling external API for anomaly {row['Reconciliation_Type']}.")
    response = requests.post("https://dummy-api-endpoint.com/resolution", data={'anomaly_type': row['Reconciliation_Type']})
    print(f"API Response: {response.status_code}")


def send_email(row):
    print(f"Sending email for anomaly {row['Reconciliation_Type']}. Using SMTP server smtp.yhc.com.")
    try:
        with smtplib.SMTP('smtp.yhc.com') as smtp:
            sender = 'test_email@yhc.com'
            recipient = 'team@example.com'
            subject = f"Anomaly Detected in {row['Reconciliation_Type']}"
            body = f"Anomaly details: {row.to_dict()}"
            smtp.sendmail(sender, recipient, message)
            print(f"Email sent to {recipient}.")
    except Exception as e:
        print(f"Failed to send email: {e}")



def main():
    st.title("Genetic AI for Anomaly Break Resolution with Feedback Loop")
    config = load_config()
    if config:
        anomalies = load_anomalies(config)
        if not anomalies.empty:
            detect_anomalies(anomalies, config)


if __name__ == "__main__":
    main()

