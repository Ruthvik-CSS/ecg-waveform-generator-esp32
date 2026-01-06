import os
import requests
import wfdb
import pandas as pd
import numpy as np

# Record names and dataset URL base
record_names = ['100', '101', '102']
base_url = 'https://physionet.org/files/mitdb/1.0.0/'

dataset_dir = 'mitdb_data'
os.makedirs(dataset_dir, exist_ok=True)

def download_file(url, dest):
    if not os.path.exists(dest):
        print(f"Downloading {url}...")
        r = requests.get(url)
        r.raise_for_status()
        with open(dest, 'wb') as f:
            f.write(r.content)
    else:
        print(f"File {dest} already exists, skipping download.")

def download_record_files(record_name):
    extensions = ['.dat', '.hea', '.atr']  # essential MIT-BIH files
    for ext in extensions:
        url = f"{base_url}{record_name}{ext}"
        dest = os.path.join(dataset_dir, f"{record_name}{ext}")
        download_file(url, dest)

def load_ecg(record_name):
    record_path = os.path.join(dataset_dir, record_name)
    record = wfdb.rdrecord(record_path)
    ecg_signal = record.p_signal[:, 0]
    return ecg_signal

def save_raw_csv(ecg_signal, record_name):
    df = pd.DataFrame({'ECG': ecg_signal})
    raw_csv_file = f"{record_name}_raw_ecg.csv"
    df.to_csv(raw_csv_file, index=False)
    print(f"Saved raw ECG CSV: {raw_csv_file}")
    return raw_csv_file

def save_scaled_csv(raw_csv_file, record_name):
    df = pd.read_csv(raw_csv_file)
    normalized = (df['ECG'] - df['ECG'].min()) / (df['ECG'].max() - df['ECG'].min())
    scaled = (normalized * 255).astype(int)
    scaled_df = pd.DataFrame({'DAC': scaled})
    scaled_csv_file = f"{record_name}_scaled_dac.csv"
    scaled_df.to_csv(scaled_csv_file, index=False)
    print(f"Saved scaled DAC CSV: {scaled_csv_file}")
    return scaled_csv_file

for record_name in record_names:
    print(f"Downloading files for record {record_name}...")
    download_record_files(record_name)
    print(f"Processing record {record_name}...")
    ecg_signal = load_ecg(record_name)
    raw_csv = save_raw_csv(ecg_signal, record_name)
    scaled_csv = save_scaled_csv(raw_csv, record_name)

print("All records downloaded and processed.")
