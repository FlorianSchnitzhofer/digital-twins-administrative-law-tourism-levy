
from flask import Flask, request, jsonify
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS, XSD
from typing import List, Tuple
import json
import os

# Flask-Initialisierung
app = Flask(__name__)


def load_ontology_parameters():
    """
    Load tourism levy configuration parameters from the OWL ontology.
    """
    g = Graph()
   
    # Load the ontology file from the package directory so the
    # application can be run from any working directory
    ontology_path = os.path.join(os.path.dirname(__file__),
                                "model_ooetourism_levy.owl")
    g.parse(ontology_path)
    
    # Extract contribution rates
    contribution_rates_query = """
    SELECT ?value WHERE {
        <http://tourismlevy.lawdigitaltwin.com/dtal_toursimlevy/ooe_tourism_axioms#contributionRates>
            <http://www.w3.org/1999/02/22-rdf-syntax-ns#value> ?value .
    """
    
    # Extract minimum contributions
    min_contributions_query = """
    SELECT ?value WHERE { 
        ?s <http://tourismlevy.lawdigitaltwin.com/dtal_toursimlevy/ooe_tourism_axioms#minimumContributions> 
         <http://www.w3.org/1999/02/22-rdf-syntax-ns#value> ?value .
    }
    """
    
    # Extract max revenue cap
    max_revenue_query = """
    SELECT ?value WHERE { 
        ?s <http://tourismlevy.lawdigitaltwin.com/dtal_toursimlevy/ooe_tourism_axioms#maxContributionBase> 
         <http://www.w3.org/1999/02/22-rdf-syntax-ns#value> ?value .
    }
    """
    
    # Execute queries
    contribution_rates = json.loads(list(g.query(contribution_rates_query))[0][0])
    min_contributions = json.loads(list(g.query(min_contributions_query))[0][0])
    max_revenue_cap = float(list(g.query(max_revenue_query))[0][0])
    
    return contribution_rates, min_contributions, max_revenue_cap
    
"""
Calculate the tourism levy based on the Upper Austrian Tourism Law Ontology.

:param taxpayer: Name of the taxpayer
:param revenue: Annual revenue of the business in EUR
:param municipality_class: Class of the municipality (A, B, C, D, etc.)
:param contribution_group: Contribution group (1 to 7)
:return: Calculated tourism levy amount
"""
def calculate_tourism_levy(taxpayer, revenue, municipality_class, contribution_group):
    
    # Load ontology parameters
    contribution_rates, minimum_contributions, max_revenue_cap = load_ontology_parameters()
    
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
    #taxpayer_info = {
    #    "taxpayer": taxpayer,
    #    "municipality_class": municipality_class,
    #    "contribution_group": contribution_group,
    #    "taxable_revenue": revenue,
    #    "levy_percentage": 3,
    #    "calculated_levy": 1234,
    #    "final_levy": 74321
    #}
    print(taxpayer_info)
    
    return jsonify(taxpayer_info)

# Run Flask app
if __name__ == '__main__':
    app.run(debug=True)
