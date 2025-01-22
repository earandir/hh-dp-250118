from uuid import UUID
from datetime import datetime
from typing import Any

def is_valid_uuid(value: str) -> bool:
    """Validate if a string is a valid UUID."""
    try:
        UUID(value)
        return True
    except ValueError:
        return False
    
from uuid import UUID

def is_valid_timestamp(value: str) -> bool:
    """Validate if a string is a valid timestamp in the expected format."""
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
        return True
    except ValueError:
        return False

def is_valid_ndc(value: str) -> bool:
    """Validate if a string is a valid NDC (National Drug Code)."""
    if not isinstance(value, str):
        return False
    # NDC should be numeric and typically 11 digits
    return value.isdigit() and len(value) == 11

def is_valid_npi(value: str) -> bool:
    """Validate if a string is a valid NPI (National Provider Identifier)."""
    if not isinstance(value, str):
        return False
    # NPI should be numeric and 10 digits
    return value.isdigit() and len(value) == 10

def is_valid_quantity(value: Any) -> bool:
    """
    Validate if a value is a valid quantity (positive integer).
    
    Args:
        value: Value to validate
        
    Returns:
        bool: True if value is a positive integer
    """
    if not isinstance(value, (int, float)):
        return False
    # Check if it's a whole number
    if int(value) != value:
        return False
    return value > 0

def filter_claims_by_pharmacies(claims, pharmacies):
    """
    Filters claims to keep only those corresponding to valid pharmacies based on NPI.

    Args:
        claims (list[dict]): A list of claim dictionaries.
        pharmacies (list[dict]): A list of pharmacy dictionaries with 'npi' keys.

    Returns:
        list[dict]: Filtered list of claims corresponding to valid pharmacies.
    """
    # Extract valid NPIs from the pharmacies
    valid_npis = {pharmacy['npi'] for pharmacy in pharmacies}
    
    # Filter claims based on valid NPIs
    filtered_claims = [claim for claim in claims if claim['npi'] in valid_npis]
    
    return filtered_claims

def filter_reverts_by_claims(reverts, claims):
    """
    Filters reverts to keep only those corresponding to valid claim based on claim id.

    Args:
        claims (list[dict]): A list of claim dictionaries.
        reverts (list[dict]): A list of reverts dictionaries with 'claim_id' keys.

    Returns:
        list[dict]: Filtered list of reverts corresponding to valid claims.
    """
    # Extract valid claim_id from the claims
    valid_claim_ids = {claim['id'] for claim in claims}
        
    # Filter reverts based on valid claims
    filtered_reverts = [revert for revert in reverts if revert['claim_id'] in valid_claim_ids]
        
    return filtered_reverts