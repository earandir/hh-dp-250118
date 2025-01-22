import json
import glob
import os
from typing import List, Dict, Any
from logging_config import setup_logging
import logging
from datetime import datetime

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
            return False
            
        # Validate each field
        if not isinstance(record['id'], str) or not record['id']:
            return False
            
        if not isinstance(record['claim_id'], str) or not record['claim_id']:
            return False
            
        try:
            datetime.fromisoformat(record['timestamp'])
        except ValueError:
            return False
            
        return True
    except Exception as e:
        logging.error(f"Error validating revert record: {e}")
        return False

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
        raise ValueError(f"Directory not found: {folder_path}")
    
    valid_data = []
    files = glob.glob(os.path.join(folder_path, "*.json"))
    
    if not files:
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
                    if validate_revert_record(record):
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
        logging.info(f"\nFound {len(invalid_records)} invalid reverts out of {total_records} total records:")
        for idx, record in enumerate(invalid_records, 1):
            logging.info(f"{idx} of {len(invalid_records)} - {record}")
    
    return valid_data