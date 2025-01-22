from typing import List, Dict
from collections import defaultdict
from statistics import mean

def calculate_metrics(claims, reverts) -> List[Dict]:
        """Calculate metrics per NPI and NDC combination."""
        metrics = defaultdict(lambda: {
            'fills': 0,
            'reverted': 0,
            'total_price': 0.0,
            'prices': []
        })

        # Process claims
        for claim in claims:
            key = (claim['npi'], claim['ndc'])
            metrics[key]['fills'] += 1
            metrics[key]['total_price'] += claim['price']
            metrics[key]['prices'].append(claim['price'] / claim['quantity'])

            if claim['id'] in reverts:
                metrics[key]['reverted'] += 1

        # Format results
        results = []
        for (npi, ndc), data in metrics.items():
            results.append({
                'npi': npi,
                'ndc': ndc,
                'fills': data['fills'],
                'reverted': data['reverted'],
                'avg_price': round(mean(data['prices']), 2) if data['prices'] else 0,
                'total_price': round(data['total_price'], 2)
            })

        return results

def get_chain_recommendations(claims_df, pharmacies_df):
    # Merge claims with pharmacy data to get chain information
    merged_df = claims_df.merge(pharmacies_df, left_on='npi', right_on='npi')
    
    # Calculate unit price
    merged_df['unit_price'] = merged_df['price'] / merged_df['quantity']
    
    # Calculate average price per chain and drug
    avg_prices = (merged_df.groupby(['ndc', 'chain'])['unit_price']
                          .mean()
                          .reset_index())
    
    # Get top 2 chains per drug
    recommendations = (avg_prices.sort_values(['ndc', 'unit_price'])
                               .groupby('ndc')
                               .head(2)
                               .groupby('ndc')
                               .apply(lambda x: [{'name': r['chain'], 
                                                'avg_price': round(r['unit_price'], 2)} 
                                               for _, r in x.iterrows()])
                               .reset_index()
                               .rename(columns={0: 'chain'})
                               .to_dict('records'))
    
    return recommendations

def analyze_quantities(claims_df):
    # Group by NDC and get most common quantities
    quantities = (claims_df.groupby('ndc')['quantity']
                         .value_counts()
                         .groupby('ndc')
                         .head(5)  # Top 5 most common quantities
                         .reset_index(level=1)
                         .groupby('ndc')['quantity']
                         .apply(list)
                         .reset_index()
                         .rename(columns={'quantity': 'most_prescribed_quantity'})
                         .to_dict('records'))
    
    return quantities