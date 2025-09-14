"""Small helper script for the project.

This file is NOT the Streamlit entrypoint. To run the app use:

    streamlit run ui.py

The script can be used to quickly check that the parquet dataset can be loaded.
"""
from function import load_database


def check_data():
    df = load_database()
    print(f"Dataset loaded with shape: {df.shape}")


if __name__ == "__main__":
    print("This module is not the Streamlit entrypoint.")
    print("Run the app with: streamlit run ui.py")
    try:
        check_data()
    except Exception as e:
        print("Error loading data:", e)
