import argparse
from pathlib import Path
import os
import sys
from load_and_clean_claims import load_and_validate_json_data
from load_and_clean_reverts import load_and_validate_revert_json_data
from load_and_clean_pharmacies import load_and_clean_pharmacies
from utils import filter_claims_by_pharmacies, filter_reverts_by_claims
from utils import remove_duplicate_claims
from utils import save_output
from analytics import calculate_metrics
from analytics import get_chain_recommendations
from analytics import analyze_quantities
from logging_config import setup_logging
import logging
import pandas as pd

# Setup logging
setup_logging()

# Define the static output folder
OUTPUT_FOLDER = "output\\"  # You can modify this path as needed

# Default directories for claims, pharmacies, and reverts
DEFAULT_CLAIMS_FOLDER = "data\\claims\\"
DEFAULT_PHARMACIES_FOLDER = "data\\pharmacies\\"
DEFAULT_REVERTS_FOLDER = "data\\reverts\\"

def main(pharmacies, claims, reverts):
       
    output_path = 'output'
    base_dir = os.path.dirname(os.path.dirname(__file__))

    # Get the folder paths from the command-line arguments
    claims_folder_path = os.path.join(base_dir, claims)
    pharmacy_folder_path = os.path.join(base_dir, pharmacies)
    reverts_folder_path = os.path.join(base_dir, reverts)
    output_path = os.path.join(base_dir, output_path)
    
    # Load the data from the files
    logging.info(f"pharmacies path: {pharmacy_folder_path}")
    pharmacies_data = load_and_clean_pharmacies(pharmacy_folder_path)
    logging.info(f"claims path: {claims_folder_path}")
    claims_data = load_and_validate_json_data(claims_folder_path)
    logging.info(f"reverts path: {reverts_folder_path}")
    reverts_data = load_and_validate_revert_json_data(reverts_folder_path)

    # Filter the claims data
    total_claims = len(claims_data)
    claims_data = filter_claims_by_pharmacies(claims_data, pharmacies_data)
    ignored_claims = total_claims - len(claims_data)
    logging.info(f"Ignored {ignored_claims} claims that do not correspond to any pharmacies")
    total_claims = len(claims_data)
    unique_claims = remove_duplicate_claims(claims_data)
    logging.info(f"Removed {total_claims - len(unique_claims)} duplicate claims")
    
    total_reverts = len(reverts_data)
    reverts_data = filter_reverts_by_claims(reverts_data, claims_data)
    ignored_reverts = total_reverts - len(reverts_data)
    logging.info(f"Ignored {ignored_reverts} reverts that do not correspond to any claims")

    # Log the number of records loaded
    logging.info(f'Loaded {len(unique_claims)} valid claims')
    logging.info(f'Loaded {len(reverts_data)} valid reverts')
    logging.info(f'Loaded {len(pharmacies_data)} valid pharmacies')

    # Calculate metrics
    logging.info("Processing metrics...")
    metrics = calculate_metrics(unique_claims, reverts_data)
    save_output(metrics, 'metrics.json', output_path)

    # Get chain recommendations
    logging.info("Processing chain recommendations...")
    claims_df = pd.DataFrame(unique_claims)
    pharmacies_df = pd.DataFrame(pharmacies_data)
    chain_recommendations = get_chain_recommendations(claims_df, pharmacies_df)
    save_output(chain_recommendations, 'chain_recommendations.json', output_path)

    # Analyze quantities
    logging.info("Processing quantity analysis...")
    quantities = analyze_quantities(claims_df)
    save_output(quantities, 'common_ndc_quantities.json', output_path)

    logging.info("Application finished")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process pharmacy claims and reverts data to generate insights.')
    parser.add_argument('--claims', type=str, default=DEFAULT_CLAIMS_FOLDER, help='Directory containing claims data (default: ./claims)')
    parser.add_argument('--pharmacies', type=str, default=DEFAULT_PHARMACIES_FOLDER, help='Directory containing pharmacy data (default: ./pharmacies)')
    parser.add_argument('--reverts', type=str, default=DEFAULT_REVERTS_FOLDER, help='Directory containing reverts data (default: ./reverts)')
    
    args = parser.parse_args()
    logging.info("Application started")
    # Validate directories
    for directory in [args.pharmacies, args.claims, args.reverts]:
        if not Path(directory).is_dir():
            logging.error(f"Error: {directory} is not a valid directory.")
            sys.exit(1)
    
    # Validate the static output directory, ensuring it exists or can be created
    output_path = Path(OUTPUT_FOLDER)
    if not output_path.exists():
        logging.error(f"Output directory does not exist, creating {output_path}")
        try:
            output_path.mkdir(parents=True, exist_ok=True)  # Creates the directory if it doesn't exist
        except Exception as e:
            logging.error(f"Failed to create output directory: {e}")
            sys.exit(1)
    elif not output_path.is_dir():
        logging.error(f"Error: {OUTPUT_FOLDER} is not a valid directory.")
        sys.exit(1)

    try:
        main(args.pharmacies, args.claims, args.reverts)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        sys.exit(1)