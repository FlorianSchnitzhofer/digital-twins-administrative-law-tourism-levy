
from flask import Flask, request, jsonify
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS, XSD
from typing import List, Tuple

# Flask-Initialisierung
app = Flask(__name__)

# Define namespaces based on provided ontologies
#ONTOLOGY = Namespace("http://tax.digitaltwin.com/income/ontology_at_income_tax#")
#MODEL = Namespace("http://tax.digitaltwin.com/income/model_at_income_tax#")

# Load ontologies and initialize graphs
#ontology_graph = Graph()
#ontology_graph.parse("ontology_income_tax.owl", format="turtle")

# Load ontologies and initialize graphs
#model_graph = Graph()
#model_graph.parse("model_income_tax.owl", format="turtle")

"""
Calculate the tourism levy based on the Upper Austrian Tourism Law Ontology.

:param taxpayer: Name of the taxpayer
:param revenue: Annual revenue of the business in EUR
:param municipality_class: Class of the municipality (A, B, C, D, etc.)
:param contribution_group: Contribution group (1 to 7)
:return: Calculated tourism levy amount
"""
def calculate_tourism_levy(taxpayer, revenue, municipality_class, contribution_group):
    
    # Contribution rates based on municipality class and group
    contribution_rates = {
        "A": [0.50, 0.35, 0.20, 0.15, 0.10, 0.05, 0.00],
        "B": [0.45, 0.30, 0.15, 0.10, 0.05, 0.00, 0.00],
        "C": [0.40, 0.20, 0.10, 0.05, 0.025, 0.00, 0.00],
        "St": [0.40, 0.20, 0.10, 0.05, 0.025, 0.00, 0.00]
    }
    
    # Minimum contribution amounts
    minimum_contributions = {
        "A": [69.00, 51.00, 34.50, 34.50, 34.50, 34.50, 0.00],
        "B": [51.00, 34.50, 34.50, 34.50, 34.50, 0.00, 0.00],
        "C": [34.50, 34.50, 34.50, 34.50, 34.50, 0.00, 0.00],
        "St": [34.50, 34.50, 34.50, 34.50, 34.50, 0.00, 0.00]
    }
    
    max_revenue_cap = 4280000  # Maximum taxable revenue
    
    # Ensure contribution group is within valid range
    if contribution_group < 1 or contribution_group > 7:
        raise ValueError("Invalid contribution group. Must be between 1 and 7.")
    
    # Cap revenue if necessary
    taxable_revenue = min(revenue, max_revenue_cap)
    
    # Determine levy based on the applicable percentage
    levy_percentage = contribution_rates[municipality_class][contribution_group - 1]
    calculated_levy = taxable_revenue * levy_percentage / 100
    
    # Ensure minimum contribution is met
    min_levy = minimum_contributions[municipality_class][contribution_group - 1]
    final_levy = max(calculated_levy, min_levy)
    
    return {
        "taxpayer": taxpayer,
        "municipality_class": municipality_class,
        "contribution_group": contribution_group,
        "taxable_revenue": taxable_revenue,
        "levy_percentage": levy_percentage,
        "calculated_levy": calculated_levy,
        "final_levy": final_levy
    }


# Route for calculating ooetourism levy based on JSON payload
@app.route('/dtal/calculate_ooetourism_levy', methods=['POST'])
def calculate_tax_endpoint():
    payload = request.get_json()
    
    
    taxpayer = payload["taxpayer"]
    revenue = payload["revenue"]
    municipality_class = payload["municipality_class"]
    contribution_group =  payload["contribution_group"]
    
     # Example usage
    taxpayer_info = calculate_tourism_levy(taxpayer, revenue, municipality_class, contribution_group)
    print(taxpayer_info)
    
    return jsonify(taxpayer_info)

# Run Flask app
if __name__ == '__main__':
    app.run(debug=True)
