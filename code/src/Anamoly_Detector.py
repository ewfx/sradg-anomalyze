import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN, KMeans
from scipy.stats import zscore
import matplotlib.pyplot as plt
import seaborn as sns
import json
from collections import defaultdict

# Load configuration
with open('recon_config.json', 'r') as file:
    config = json.load(file)

# Load preprocessed datasets
datasets = {}
for recon_name, recon_info in config.items():
    datasets[recon_name] = pd.read_csv(recon_info['file_path'])
    print(f"Loaded {recon_name} with {len(datasets[recon_name])} records.")

# Predefined anomaly categories
anomaly_reasons = defaultdict(lambda: "New Anomaly Detected")
predefined_categories = ["Data Quality Issue", "Outlier Transaction", "Suspicious Activity", "Data Entry Error"]
anomaly_reasons.update({category: category for category in predefined_categories})

# Feedback Mechanism: Placeholder for user feedback collection
feedback_log = {}

# Anomaly Detection
for recon_name, recon_info in config.items():
    data = datasets[recon_name]
    print(f"
Analyzing {recon_name} for anomalies...")

    # Select criteria and derived columns for anomaly detection
    target_columns = recon_info['criteria_columns'] + recon_info['derived_columns']
    target_columns = [col for col in target_columns if col in data.columns]

    if not target_columns:
        print(f"No valid columns for anomaly detection in {recon_name}. Skipping.")
        continue

    # Standardize data
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data[target_columns].fillna(0))

    # Statistical Anomaly Detection
    z_scores = np.abs(zscore(scaled_data))
    z_anomalies = (z_scores > 3).any(axis=1)

    # Isolation Forest
    iso_forest = IsolationForest(contamination=0.05, random_state=42)
    iso_labels = iso_forest.fit_predict(scaled_data)
    iso_anomalies = iso_labels == -1

    # DBSCAN
    dbscan = DBSCAN(eps=0.5, min_samples=5)
    dbscan_labels = dbscan.fit_predict(scaled_data)
    dbscan_anomalies = dbscan_labels == -1

    # K-Means
    kmeans = KMeans(n_clusters=3, random_state=42)
    kmeans.fit(scaled_data)
    distances = np.linalg.norm(scaled_data - kmeans.cluster_centers_[kmeans.labels_], axis=1)
    kmeans_anomalies = distances > np.percentile(distances, 95)

    # Combine anomaly indicators and classify
    data['Z_Anomaly'] = z_anomalies
    data['IF_Anomaly'] = iso_anomalies
    data['DBSCAN_Anomaly'] = dbscan_anomalies
    data['KMeans_Anomaly'] = kmeans_anomalies
    data['Anomaly'] = data[['Z_Anomaly', 'IF_Anomaly', 'DBSCAN_Anomaly', 'KMeans_Anomaly']].any(axis=1)

    # Assign anomaly category and reason
    def get_anomaly_reason(row):
        if recon_name == list(datasets.keys())[0]:  # Only for the first dataset
            if row['Anomaly']:
                reasons = []
                if row['Z_Anomaly']:
                    reasons.append("Inconsistent variations in outstanding balances")
                if row['IF_Anomaly']:
                    reasons.append("Huge spike in outstanding balances")
                if row['DBSCAN_Anomaly']:
                    reasons.append("Unusual patterns in transaction clusters")
                if row['KMeans_Anomaly']:
                    reasons.append("Outliers deviating significantly from expected clusters")
                return ', '.join(reasons)
            return "Consistent increase or decrease in outstanding balances or balances are in line with previous months"
        return ""

    data['Anomaly_Category'] = data.apply(lambda row: anomaly_reasons[row['Anomaly']] if row['Anomaly'] else "No Anomaly", axis=1)

    if recon_name == list(datasets.keys())[0]:
        data['Anomaly_Reason'] = data.apply(lambda row: get_anomaly_reason(row), axis=1)

    # Visualization
    if len(target_columns) >= 2:
        plt.figure(figsize=(10, 6))
        sns.scatterplot(x=data[target_columns[0]], y=data[target_columns[1]], hue=data['Anomaly'], palette={0: 'blue', 1: 'red'})
        plt.title(f"Anomaly Detection for {recon_name}")
        plt.xlabel(target_columns[0])
        plt.ylabel(target_columns[1])
        plt.grid(True)
        plt.show()

    # Save results
    data.to_csv(f"{recon_name}_anomaly_results.csv", index=False)

print("Anomaly detection completed for all datasets with classifications and feedback capabilities!")
