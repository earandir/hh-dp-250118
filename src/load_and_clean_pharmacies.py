import csv
import glob
import os
from typing import List, Dict
import logging
from logging_config import setup_logging

# Setup logging
setup_logging()

def load_and_clean_pharmacies(folder_path: str) -> List[Dict[str, str]]:
    """
    Load and clean the pharmacies data from all CSV files in the specified folder.
    
    Args:
        folder_path: Path to the folder containing CSV files with pharmacies data.
        
    Returns:
        List[Dict[str, str]]: List of dictionaries containing unique pharmacies data.
    """
    pharmacies = []
    seen = set()
    
    try:
        csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
        if not csv_files:
            logging.error(f"Error: No CSV files found in the folder '{folder_path}'.")
            return pharmacies
        
        for file_path in csv_files:
            with open(file_path, mode='r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Create a tuple of the values to check for duplicates
                    row_tuple = tuple(row.items())
                    if row_tuple not in seen:
                        seen.add(row_tuple)
                        pharmacies.append(row)
    except FileNotFoundError:
        logging.error(f"Error: The folder '{folder_path}' does not exist.")
    except Exception as e:
        logging.error(f"Error: An error occurred while processing the files in '{folder_path}': {e}")
    
    return pharmacies