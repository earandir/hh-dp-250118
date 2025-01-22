from typing import List, Dict, Tuple
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