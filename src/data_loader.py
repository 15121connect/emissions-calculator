"""
Data loading utilities for the emissions calculator.

This module provides functions to load CSV files from a directory into pandas DataFrames.
"""

import pandas as pd
import os


def load_data_from_directory(csv_dir):
    """
    Load all CSV files from a directory into a dictionary of DataFrames.
    
    Args:
        csv_dir (str): Path to the directory containing CSV files.
    
    Returns:
        dict: Dictionary where keys are filenames (without extension) and 
              values are pandas DataFrames.
    
    Example:
        >>> dataframes = load_data_from_directory('data/raw')
        >>> print(dataframes.keys())
        dict_keys(['fuel_data', 'refrigerant_gwp', ...])
    """
    dataframes = {}
    
    # Check if directory exists
    if not os.path.exists(csv_dir):
        raise FileNotFoundError(f"Directory '{csv_dir}' not found.")
    
    # Iterate over files in the directory
    for filename in os.listdir(csv_dir):
        if filename.endswith('.csv'):
            filepath = os.path.join(csv_dir, filename)
            try:
                # Read the CSV file into a pandas DataFrame
                df = pd.read_csv(filepath)
                
                # Use the filename (without extension) as the key
                key = os.path.splitext(filename)[0]
                dataframes[key] = df
                print(f"Successfully loaded '{filename}' into dataframe '{key}'")
                
            except pd.errors.EmptyDataError:
                print(f"Warning: '{filename}' is empty. Skipping.")
            except pd.errors.ParserError:
                print(f"Warning: Could not parse '{filename}'. Skipping.")
            except Exception as e:
                print(f"An unexpected error occurred while reading '{filename}': {e}")
    
    if not dataframes:
        print(f"Warning: No CSV files found in '{csv_dir}'")
    
    return dataframes
