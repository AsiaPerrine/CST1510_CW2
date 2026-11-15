"""
fetch_data.py - Week 8: get data from an API and save it as DATA/raw.csv.

Run it:  python fetch_data.py
"""

from pathlib import Path

import pandas as pd
import requests

# ---- Settings: the only part you change for your own data ------------------
# GitHub API for Python organisation repositories
URL = "https://api.github.com/orgs/python/repos"
PARAMS = {"per_page": 100}  # Request up to 100 repositories
RECORDS_KEY = None          # No key is needed because the data is already a list

# Rename selected columns to make them easier to understand
RENAME = {
    "html_url": "repo_link", 
    "description": "details",
    "full_name": "repo_name"
}

# Choose the ten columns to include in the table
KEEP = ["id", "name", "repo_name", "private", "repo_link", "details", "fork", "stargazers_count", "language", "forks_count"]    # the columns you want
MUST_HAVE = ["id", "name", "repo_name"]              # Columns that must contain a value

RAW_FILE = Path(__file__).parent / "DATA" / "raw.csv"  # Set the location where the CSV file will be saved

# ---- The functions ------------------------------------------------------------


def get_data(url, params):
    """Ask the API for data. Returns the JSON reply, or None if something went wrong."""
    try:
        response = requests.get(url, params=params, timeout=15)   # Send a request to the API
        response.raise_for_status()          # turns 404, 500 ... into an error
        return response.json()    # Return the data in JSON format
    except requests.RequestException as error:
        # Show the error if the request fails
        print("Could not get the data:", error)
        return None


def make_table(data, records_key):
    """Turn the JSON reply into a pandas table."""
    # Get the list of repositories
    records = data[records_key] if records_key else data
    return pd.json_normalize(records, sep="_")      # nested {"a": {"b": 1}} becomes column a_b


def tidy_data(df):
    """Rename, keep and clean the columns."""
    df = df.rename(columns=RENAME)    # Rename the selected columns
    df = df[KEEP]     # Keep only the ten chosen columns
    df = df.dropna(subset=MUST_HAVE)    # Remove rows with missing required values
    return df    # Return the cleaned DataFrame


def save_data(df, path):
    """Save the table as a CSV file."""
    path.parent.mkdir(exist_ok=True) # Create the folder if it is missing
    df.to_csv(path, index=False)  # Save the data without the index
    print(f"Saved {len(df)} rows to {path}")    # Show how many records were saved


if __name__ == "__main__":
    data = get_data(URL, PARAMS)    # Fetch the GitHub data
    # Continue if the data was received
    if data is not None:  
        table = make_table(data, RECORDS_KEY)   # Convert the data into a table
        table = tidy_data(table)   # Keep and clean the selected columns
        print(table.head())     # Show the first five records
        save_data(table, RAW_FILE)     # Save the table to raw.csv
