import json
import glob
import os
from typing import List, Dict, Any
from logging_config import setup_logging
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import is_valid_uuid, is_valid_timestamp

setup_logging()

def validate_revert_record(record: Dict[str, Any]) -> bool:
    """
    Validate if a revert record matches the expected schema and data types.
    
    Args:
        record: Dictionary containing the revert record
        
    Returns:
        bool: True if record is valid, False otherwise
    """
    try:
        # Check if all required fields are present
        required_fields = {'id', 'claim_id', 'timestamp'}
        if not all(field in record for field in required_fields):
            logging.error(f"Missing required fields in record: {record}")
            return False
            
        # Validate each field
        if not is_valid_uuid(record['id']):
            logging.error(f"Invalid ID in record: {record['id']}")
            return False
            
        if not is_valid_uuid(record['claim_id']):
            logging.error(f"Invalid claim ID in record: {record['claim_id']}")
            return False
            
        if not is_valid_timestamp(record['timestamp']):
            logging.error(f"Invalid timestamp in record: {record['timestamp']}")
            return False
            
        return True
    except Exception as e:
        logging.error(f"Error validating revert record: {e}")
        return False

def process_file(file: str) -> List[Dict[str, Any]]:
    """
    Process a single JSON file and validate its records.
    
    Args:
        file: Path to the JSON file
        
    Returns:
        List[Dict[str, Any]]: List of valid revert records
    """
    valid_records = []
    try:
        with open(file, 'r') as j:
            logging.info(f"Loading reverts data from {os.path.basename(file)}")
            records = json.load(j)
            
            # Handle both single records and lists of records
            if isinstance(records, dict):
                records = [records]
            
            for record in records:
                if validate_revert_record(record):
                    # Convert timestamp to datetime object
                    record['timestamp'] = datetime.fromisoformat(record['timestamp'])
                    valid_records.append(record)
    except (json.JSONDecodeError, Exception) as e:
        logging.error(f"Error processing file {file}: {e}")
    
    return valid_records

def load_and_validate_revert_json_data(folder_path: str) -> List[Dict[str, Any]]:
    """
    Load and validate JSON data from revert transaction files in the specified folder.
    
    Args:
        folder_path: Path to the folder containing JSON files
        
    Returns:
        List[Dict[str, Any]]: List containing all valid revert records
        
    Raises:
        ValueError: If folder_path doesn't exist or no JSON files found
    """
    if not os.path.exists(folder_path):
        logging.error(f"Directory not found: {folder_path}")
        raise ValueError(f"Directory not found: {folder_path}")
    
    valid_data = []
    files = glob.glob(os.path.join(folder_path, "*.json"))
    
    if not files:
        logging.error(f"No JSON files found in {folder_path}")
        raise ValueError(f"No JSON files found in {folder_path}")
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_file = {executor.submit(process_file, file): file for file in files}
        for future in as_completed(future_to_file):
            file = future_to_file[future]
            try:
                valid_records = future.result()
                valid_data.extend(valid_records)
            except Exception as e:
                logging.error(f"Error processing file {file}: {e}")
    
    return valid_data