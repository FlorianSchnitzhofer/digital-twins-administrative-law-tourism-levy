import os
import sys
from fastmcp import FastMCP

# Ensure local src directory is on path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from dtal_toursimlevy.logic_ooetourism_levy import (
    calculate_tourism_levy,
    get_contribution_group,
    get_municipality_class,
)

mcp = FastMCP("ooe-tourism-levy")

@mcp.tool(name="dtal.calculate_ooetourism_levy")
def calculate_ooetourism_levy(
    municipality_name: str,
    business_activity: str,
    revenue_two_years_ago: float,
) -> dict:
    """Calculate the Upper Austrian tourism levy.

    Args:
        municipality_name: Municipality where the business operates.
        business_activity: Description of the business activity.
        revenue_two_years_ago: Annual revenue of the business from two years ago in EUR.

    Returns:
        A dictionary with levy calculation details.
    """
    municipality_class = get_municipality_class(municipality_name)
    contribution_group = get_contribution_group(business_activity, municipality_class)
    result = calculate_tourism_levy(
        revenue_two_years_ago, municipality_class, contribution_group
    )
    result["business_activity"] = business_activity
    return result


if __name__ == "__main__":
    mcp.run()
