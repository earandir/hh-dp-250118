import json
import glob
import os
from typing import List, Dict, Any
from datetime import datetime
from logging_config import setup_logging
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import is_valid_uuid, is_valid_timestamp, is_valid_ndc, is_valid_npi, is_valid_quantity

setup_logging()

def validate_claim_record(data, schema) -> bool:
    """
    Validates a dictionary against a schema.

    Args:
        data (dict): The dictionary to validate.
        schema (dict): The schema to validate against.

    Returns:
        bool: True if valid, False otherwise.
    """
    # Extract the ID or use 'Unknown ID' if missing
    claim_id = data.get('id', 'Unknown ID')  

    for key, expected_type in schema.items():
        if key not in data:
            logging.error(f"Claim ID {claim_id}: Missing key: {key}")
            return False

        value = data[key]
        if expected_type == 'timestamp':
            if not is_valid_timestamp(value):
                logging.error(f"Claim ID {claim_id}: Invalid timestamp format for key: {key}. Expected 'YYYY-MM-DDTHH:MM:SS', got {value}")
                return False
        elif key == 'price' and value < 0:
            logging.error(f"Claim ID {claim_id}: Invalid value for key: {key}. Expected greater than 0, got {value}")
            return False    
        elif expected_type == int:
            # Check if value is an integer or a float that can be safely converted
            if not (isinstance(value, int) or (isinstance(value, float) and value.is_integer())):
                logging.error(f"Claim ID {claim_id}: Invalid type for key: {key}. Expected int, got {type(value)} with value {value}")
                return False
            # Check if the quantity is greater than 0
            if key == 'quantity' and value <= 0:
                logging.error(f"Claim ID {claim_id}: Invalid value for key: {key}. Expected greater than 0, got {value}")
                return False
        elif not isinstance(value, expected_type):
            logging.error(f"Claim ID {claim_id}: Invalid type for key: {key}. Expected {expected_type}, got {type(value)}")
            return False

    return True

def process_file(file: str, claims_schema: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Process a single JSON file and validate its records.
    
    Args:
        file: Path to the JSON file
        claims_schema: Dictionary containing the expected schema
        
    Returns:
        List[Dict[str, Any]]: List of valid claim records
    """
    valid_records = []
    try:
        with open(file, 'r') as j:
            logging.info(f"Loading claims data from {os.path.basename(file)}")
            records = json.load(j)
            
            # Handle both single records and lists of records
            if isinstance(records, dict):
                records = [records]
            
            for record in records:
                if validate_claim_record(record, claims_schema):
                    # Convert timestamp to datetime object
                    record['timestamp'] = datetime.fromisoformat(record['timestamp'])
                    valid_records.append(record)
    except (json.JSONDecodeError, Exception) as e:
        logging.error(f"Error processing file {file}: {e}")
    
    return valid_records

def load_and_validate_json_data(folder_path: str) -> List[Dict[str, Any]]:
    """
    Load and validate JSON data from claim transaction files in the specified folder.
    
    Args:
        folder_path: Path to the folder containing JSON files
        
    Returns:
        List[Dict[str, Any]]: List containing all valid claim records
        
    Raises:
        ValueError: If folder_path doesn't exist or no JSON files found
    """
    if not os.path.exists(folder_path):
        logging.error(f"Directory not found: {folder_path}")
        raise ValueError(f"Directory not found: {folder_path}")
    
    valid_data = []
    claims_schema = {
        'id': str,
        'ndc': str,
        'npi': str,
        'quantity': int,
        'price': float,
        'timestamp': 'timestamp'
    }

    files = glob.glob(os.path.join(folder_path, "*.json"))
    
    if not files:
        logging.error(f"No JSON files found in {folder_path}")
        raise ValueError(f"No JSON files found in {folder_path}")
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_file = {executor.submit(process_file, file, claims_schema): file for file in files}
        for future in as_completed(future_to_file):
            file = future_to_file[future]
            try:
                valid_records = future.result()
                valid_data.extend(valid_records)
            except Exception as e:
                logging.error(f"Error processing file {file}: {e}")
    
    return valid_data