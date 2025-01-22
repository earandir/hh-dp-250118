import argparse
import os
import sys
from load_and_clean_claims import load_and_validate_json_data
from load_and_clean_reverts import load_and_validate_revert_json_data
from load_and_clean_pharmacies import load_and_clean_pharmacies
from utils import filter_claims_by_pharmacies, filter_reverts_by_claims
from logging_config import setup_logging
import logging

# Setup logging
setup_logging()

def main(pharmacies, claims, reverts):
    logging.info("Application started")
    
    base_dir = os.path.dirname(os.path.dirname(__file__))
    # Get the folder paths from the command-line arguments
    claims_folder_path = os.path.join(base_dir, claims)
    pharmacy_folder_path = os.path.join(base_dir, pharmacies)
    reverts_folder_path = os.path.join(base_dir, reverts)
    
    # Validate that the folders exist
    if not os.path.isdir(claims_folder_path):
        logging.error(f"The claims folder path '{claims_folder_path}' does not exist.")
        sys.exit(1)
    
    if not os.path.isdir(pharmacy_folder_path):
        logging.error(f"The pharmacy folder path '{pharmacy_folder_path}' does not exist.")
        sys.exit(1)
    
    if not os.path.isdir(reverts_folder_path):
        logging.error(f"The reverts folder path '{reverts_folder_path}' does not exist.")
        sys.exit(1)
    
    # Load the data from the files
    claims_data = load_and_validate_json_data(claims_folder_path)
    reverts_data = load_and_validate_revert_json_data(reverts_folder_path)
    pharmacies_data = load_and_clean_pharmacies(pharmacy_folder_path)
    
    total_claims = len(claims_data)
    claims_data = filter_claims_by_pharmacies(claims_data, pharmacies_data)
    ignored_claims = total_claims - len(claims_data)
    logging.info(f"Ignored {ignored_claims} claims that don't correspond to any pharmacies")

    total_reverts = len(reverts_data)
    reverts_data = filter_reverts_by_claims(reverts_data, claims_data)
    ignored_reverts = total_reverts - len(reverts_data)
    logging.info(f"Ignored {ignored_reverts} reverts that don't correspond to any claims")

    # Log the number of records loaded
    logging.info(f'Loaded {len(claims_data)} valid claims')
    logging.info(f'Loaded {len(reverts_data)} valid reverts')
    logging.info(f'Loaded {len(pharmacies_data)} valid pharmacies')

    logging.info("Application finished")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process pharmacy claims data')
    parser.add_argument('--claims', type=str, required=True, help='Directory containing claims data')
    parser.add_argument('--pharmacies', type=str, required=True, help='Directory containing pharmacy data')
    parser.add_argument('--reverts', type=str, required=True, help='Directory containing reverts data')
    
    args = parser.parse_args()
    main(args.pharmacies, args.claims, args.reverts)