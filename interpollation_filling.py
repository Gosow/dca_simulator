import pandas as pd
import numpy as np
from datetime import datetime

def fill_missing_dates_with_interpolation(
    file_path,
    date_col='Date',
    fill_method='linear',
    log_file='cleaning/cleaning.log'
):
    # Create a log filename with timestamp
    log_file = f'cleaning/cleaning_{file_path.split("/")[-1].split(".")[0]}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

    # Load the dataset
    df = pd.read_csv(file_path, parse_dates=[date_col], dayfirst=True)

    # Ensure the date column is in datetime format
    df[date_col] = pd.to_datetime(df[date_col])

    # Log the original data info with timestamp
    log_data_info(log_file, "Original Data", df)

    # Handle duplicate timestamps if any
    df = handle_duplicates(df, date_col, log_file)

    # Resample to fill missing dates
    df_filled = resample_and_fill(df, date_col, fill_method)

    # Log final data info with timestamp
    log_data_info(log_file, "Final Data After Filling", df_filled)

    return df_filled

def log_data_info(log_file, description, df):
    """Log the description and statistical info of a DataFrame."""
    with open(log_file, 'a') as log:
        log.write(f"{datetime.now()}: {description}:\n{df.describe()}\n")

def handle_duplicates(df, date_col, log_file):
    """Handle duplicate timestamps in the DataFrame."""
    if df[date_col].duplicated().any():
        duplicates = df[date_col].duplicated(keep=False)
        num_duplicates = duplicates.sum()
        print(f"{num_duplicates} duplicates found in the date column. Handling duplicates.")
        df = df.groupby(date_col).mean().reset_index()

        # Log duplicate handling with timestamp
        with open(log_file, 'a') as log:
            log.write(f"{datetime.now()}: Handled {num_duplicates} duplicates by averaging.\n")
    return df

def resample_and_fill(df, date_col, fill_method):
    """Resample the DataFrame to fill in missing dates using the specified method."""
    # Set the date column as index for resampling
    df.set_index(date_col, inplace=True)

    # Create a complete date range
    all_dates = pd.date_range(start=df.index.min(), end=df.index.max(), freq='D')
    df_resampled = df.reindex(all_dates)

    # Fill missing values using the specified method
    if fill_method == 'ffill':
        df_filled = df_resampled.ffill()
    elif fill_method == 'bfill':
        df_filled = df_resampled.bfill()
    elif fill_method == 'linear':
        df_filled = df_resampled.interpolate(method='linear')
    elif fill_method == 'mean':
        df_filled = df_resampled.fillna(df_resampled.mean())
    else:
        raise ValueError(f"Unknown fill method: {fill_method}")

    # Fill remaining NaN values
    df_filled = df_filled.fillna(method='bfill').fillna(method='ffill')

    # Reset the index and rename it to 'Date' to retain it in the output
    df_filled.reset_index(inplace=True)
    df_filled.rename(columns={'index': date_col}, inplace=True)  # Rename back to 'Date' if necessary

    return df_filled

# Example usage
path = "raw_data/"
files = ["monthly.csv", "data.csv"]  # Replace with your actual file paths
for file_name in files:
    file_path = f"{path}{file_name}"
    updated_data = fill_missing_dates_with_interpolation(
        file_path,
        log_file=f'cleaning/{file_name.split(".")[0]}_cleaning.log'
    )
    print(updated_data)
    updated_data.to_csv(f"cleaning/updated_{file_name}", index=False)
