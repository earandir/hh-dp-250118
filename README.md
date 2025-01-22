# Pharmacy Claims Analyzer

This application processes pharmacy claims data to generate various analytics and recommendations.

## Features

- Processes pharmacy, claims, and revert data from JSON files
- Calculates metrics per pharmacy and drug combination
- Generates chain recommendations based on drug prices
- Analyzes most common prescribed quantities per drug
- Handles invalid data gracefully
- Utilizes multi-threading for improved performance

## Requirements

- Python 3.13
- argparse
- pandas

## Installation

1. Clone the repository:
```bash
git clone https://github.com/earandir/hh-dp-250118.git
cd hh-dp-250118
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install the required packages:
```bash
pip install -r requirements.txt
```
## Usage

Run the application using the following command:

```bash
python src\main.py --pharmacies data\pharmacies --claims data\claims --reverts data\reverts
```

### Input Data Structure

The application expects JSON files in the following format:

#### Pharmacy Data
```json
{
    "npi": "string",
    "chain": "string"
}
```

#### Claims Data
```json
{
    "id": "string",
    "ndc": "string",
    "npi": "string",
    "price": float,
    "quantity": integer,
    "timestamp": "datetime"
}
```

#### Reverts Data
```json
{
    "id": "string",
    "claim_id": "string",
    "timestamp": "datetime"
}
```

### Output Files

The application generates three JSON files:

1. `metrics.json`: Contains metrics per pharmacy and drug combination
2. `chain_recommendations.json`: Contains top 2 chains per drug based on pricing
3. `common_ndc_quantities.json`: Contains most common prescribed quantities per drug

## Performance Considerations

- The application uses ThreadPoolExecutor with 10 workers to process files in parallel
- Data is processed in a streaming fashion to minimize memory usage
- Invalid data is logged and skipped rather than causing application failure

## License

This project is licensed under the MIT License - see the LICENSE file for details.
