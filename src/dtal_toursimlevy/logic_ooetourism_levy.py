from flask import (
    Flask,
    Response,
    jsonify,
    request,
    send_from_directory,
    stream_with_context,
)
from flask_cors import CORS
from rdflib import Graph, URIRef
import json
import os
import time

# Flask-Initialisierung
app = Flask(__name__)
CORS(app)

# Paths to project resources
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
WELL_KNOWN_DIR = os.path.join(ROOT_DIR, ".well-known")
LAW_TEXT_FILE = os.path.join(os.path.dirname(__file__), "text_ooetourism_levy.txt")


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
    contribution_rates_query = (
        """
        SELECT ?value WHERE {
            <http://tourismlevy.lawdigitaltwin.com/dtal_toursimlevy/ooe_tourism_axioms#contributionRates>
                <http://www.w3.org/1999/02/22-rdf-syntax-ns#value> ?value .
        }
        """.strip()
    )
 
    # Extract minimum contributions
    min_contributions_query = (
        """
        SELECT ?value WHERE {
            <http://tourismlevy.lawdigitaltwin.com/dtal_toursimlevy/ooe_tourism_axioms#minimumContributions>
                <http://www.w3.org/1999/02/22-rdf-syntax-ns#value> ?value .
        }
        """.strip()
    )
    max_revenue_query = (
        """
        SELECT ?value WHERE {
            <http://tourismlevy.lawdigitaltwin.com/dtal_toursimlevy/ooe_tourism_axioms#maxContributionBase>
                <http://www.w3.org/1999/02/22-rdf-syntax-ns#value> ?value .
        }
        """.strip()
    )
    
    # Execute queries with basic error handling
    contrib_res = list(g.query(contribution_rates_query))
    if not contrib_res:
        raise ValueError("Contribution rates not found in ontology")
    contribution_rates = json.loads(str(contrib_res[0][0]))

    min_res = list(g.query(min_contributions_query))
    if not min_res:
        raise ValueError("Minimum contributions not found in ontology")
    min_contributions = float(min_res[0][0]))

    max_res = list(g.query(max_revenue_query))
    if not max_res:
        raise ValueError("Max revenue cap not found in ontology")
    max_revenue_cap = float(max_res[0][0])
    
    return contribution_rates, min_contributions, max_revenue_cap
    

def get_municipality_class(municipality_name: str) -> str:
    """Return the municipality class for a given municipality name using SPARQL."""
    g = Graph()

    ontology_path = os.path.join(os.path.dirname(__file__), 
                                 "model_municipality_class_mapping.owl")
    g.parse(ontology_path)
    
    escaped_name = json.dumps(municipality_name)
    query = f"""
        SELECT ?clazz WHERE {{
            ?entry ex:municipalityName ?name ;
                   ex:municipalityClass ?clazz .
            FILTER(LCASE(STR(?name)) = LCASE({escaped_name}))
        }}
    """

    res = list(g.query(query))
    if not res:
        raise ValueError(
            f"Municipality '{municipality_name}' not found in municipality ontology"
        )

    return str(res[0][0])

  
"""Calculate the tourism levy based on the Upper Austrian Tourism Law Ontology.

:param revenue: Annual revenue of the business in EUR (two years ago)
:param municipality_class: Class of the municipality (A, B, C, D, etc.)
:param contribution_group: Contribution group (1 to 7)
:return: Calculated tourism levy amount
"""
def calculate_tourism_levy(revenue, municipality_class, contribution_group):
    
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
        "municipality_class": municipality_class,
        "contribution_group": contribution_group,
        "taxable_revenue": taxable_revenue,
        "levy_percentage": levy_percentage,
        "calculated_levy": calculated_levy,
        "final_levy": final_levy,
    }


_contribution_map = None


def _load_contribution_map():
    """Load contribution group mapping from the generated JSON file."""
    global _contribution_map
    if _contribution_map is None:
        json_path = os.path.join(
            os.path.dirname(__file__), "contribution_group_mapping.json"
        )
        with open(json_path, "r", encoding="utf-8") as f:
            # store keys in lower case for case-insensitive lookup
            _contribution_map = {k.lower(): v for k, v in json.load(f).items()}
    return _contribution_map


def get_contribution_group(
    business_activity_label: str, municipality_class: str
) -> int:
    """Return the contribution group for a business activity and municipality class."""

    mapping = _load_contribution_map()
    key = business_activity_label.lower()
    if key not in mapping:
        raise ValueError(
            f"Business activity '{business_activity_label}' not found in contribution group mapping"
        )

    groups = mapping[key]
    if municipality_class not in groups:
        raise ValueError(f"Unsupported municipality class '{municipality_class}'")

    return int(groups[municipality_class])

# Route for calculating ooetourism levy based on JSON payload
@app.route('/dtal/calculate_ooetourism_levy', methods=['POST'])
def calculate_tax_endpoint():
    payload = request.get_json()

    revenue = payload["revenue_two_years_ago"]
    municipality_name = payload["municipality_name"]
    business_activity = payload["business_activity"]

    try:
        municipality_class = get_municipality_class(municipality_name)
        contribution_group = get_contribution_group(business_activity, municipality_class)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404

    result = calculate_tourism_levy(revenue, municipality_class, contribution_group)
    result["business_activity"] = business_activity

    return jsonify(result)


# Run Flask app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)
