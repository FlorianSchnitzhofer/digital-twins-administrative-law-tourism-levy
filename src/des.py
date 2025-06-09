import csv
import requests
import json
import os

# Define the digital twin for administrative law API endpoint
url = "http://localhost:5000/dtal/calculate_ooetourism_levy"


# Set headers for both APIs
headers = {
    "Content-Type": "application/json"
}

count = 0
sample = {
    "taxpayer": "Sample Business",
    "revenue": 500000, 
    "municipality_name": "Adlwang",
    "contribution_group": 2}
    

# Send a POST request to the API
response = requests.post(url, json=sample, headers=headers)

if response.status_code == 200:
    calculated_levy = response.json().get('final_levy', 'N/A')
    print(f"DTAL - OOE Upper Austrian Tourism levy - # {count}: {calculated_levy}")
else:
    print(f"Request failed for {count} with status code {response.status_code}: {response.text}")


count += 1
