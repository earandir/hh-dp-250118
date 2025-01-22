import json
import glob
import os
from typing import List, Dict, Any
from datetime import datetime
from logging_config import setup_logging
import logging

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
            try:
                # Attempt to parse the timestamp
                datetime.fromisoformat(value)
            except ValueError:
                logging.error(f"Invalid timestamp format for key: {key}, value: {value}")
                return False
        elif expected_type == int:
            # Check if value is an integer or a float that can be safely converted
            if not (isinstance(value, int) or (isinstance(value, float) and value.is_integer())):
                logging.error(f"Claim ID {claim_id}: Invalid type for key: {key}. Expected int, got {type(value)} with value {value}")
                return False
        elif not isinstance(value, expected_type):
            logging.error(f"Claim ID {claim_id}: Invalid type for key: {key}. Expected {expected_type}, got {type(value)}")
            return False

    return True

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
    
    invalid_files = []
    invalid_records = []
    total_records = 0
    
    for file in files:
        try:
            with open(file, 'r') as j:
                logging.info(f"Loading data from {os.path.basename(file)}")

                records = json.load(j)
                
                # Handle both single records and lists of records
                if isinstance(records, dict):
                    records = [records]
                
                total_records += len(records)
                
                valid_records = []
                for record in records:
                    if validate_claim_record(record, claims_schema):
                        # Convert timestamp to datetime object
                        record['timestamp'] = datetime.fromisoformat(record['timestamp'])
                        valid_records.append(record)
                    else:
                        invalid_records.append(f"ID: {record.get('id', 'Unknown')} in {os.path.basename(file)}")
                
                if valid_records:
                    valid_data.extend(valid_records)
                else:
                    invalid_files.append(os.path.basename(file))
                    
        except (json.JSONDecodeError, Exception) as e:
            invalid_files.append(f"{os.path.basename(file)} (Error: {str(e)})")
            continue
    
    if invalid_files:
        logging.warning(f"The following files were skipped due to invalid format or schema: {', '.join(invalid_files)}")
    
    if invalid_records:
        logging.info(f"Found {len(invalid_records)} invalid claims out of {total_records} total records")
        #for idx, record in enumerate(invalid_records, 1):
        #    logging.info(f"{idx} of {len(invalid_records)} - {record}")
    
    return valid_data