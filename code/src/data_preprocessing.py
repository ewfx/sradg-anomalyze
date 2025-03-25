import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json

# Load configuration
with open('recon_config.json', 'r') as file:
    config = json.load(file)

# Load reconciliation datasets
datasets = {}
for recon_name, recon_info in config.items():
    datasets[recon_name] = pd.read_csv(recon_info['file_path'])
    print(f"Loaded {recon_name} data with {len(datasets[recon_name])} records.")

# Data Cleaning - Handling missing values
for recon_name, data in datasets.items():
    data.fillna('Unknown', inplace=True)

# Feature Engineering
for recon_name, recon_info in config.items():
    data = datasets[recon_name]

    # Convert relevant columns to numeric if applicable
    for col in recon_info['criteria_columns'] + recon_info['derived_columns']:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors='coerce')
        else:
            print(f"Warning: '{col}' not found in {recon_name} dataset. Skipping.")

    # Calculate differences for criteria columns
    for col in recon_info['criteria_columns']:
        if col in data.columns and pd.api.types.is_numeric_dtype(data[col]):
            diff_col = f"{col}_Diff"
            data[diff_col] = data[col].diff().fillna(0).abs()
        else:
            print(f"Warning: '{col}' not found or not numeric in {recon_name}. Skipping.")

    # Normalize differences for derived columns
    for col in recon_info['derived_columns']:
        if col in data.columns and pd.api.types.is_numeric_dtype(data[col]):
            norm_col = f"Normalized_{col}_Diff"
            data[norm_col] = data[col].abs() / (data[col].mean() + 1e-5)
        else:
            print(f"Warning: '{col}' not found or not numeric in {recon_name}. Skipping.")

    # Feature for historical pattern check
    for hist_col in recon_info['historical_columns']:
        if hist_col in data.columns:
            data[f"Is_Historical_{hist_col}"] = data[hist_col].duplicated(keep=False).astype(int)
        else:
            print(f"Warning: '{hist_col}' not found in {recon_name} dataset. Skipping.")

# Data Exploration
for recon_name, data in datasets.items():
    plt.figure(figsize=(10, 6))
    sns.histplot(data.select_dtypes(include=np.number).stack(), bins=20, kde=True)
    plt.title(f"Distribution of Numeric Differences - {recon_name}")
    plt.xlabel("Value")
    plt.ylabel("Frequency")
    plt.grid(True)
    plt.show()

print("Configurable Data Ingestion and Preprocessing Completed!")
