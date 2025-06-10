# dtal - Digital Twin Administrative Law of Upper Austrian tourism levy

Digital Twin Administrative Law of Upper Austrian tourism levy

This repository contains the source code for calculating the Upper Austrian tourism levy.

## Running the API

Install dependencies (Flask, rdflib):

```bash
pip install flask rdflib
```

Start the server:

```bash
python src/dtal_toursimlevy/logic_ooetourism_levy.py
```

The API will listen on `http://localhost:5000`.

## API Documentation

OpenAPI specification is available in [openapi.yaml](openapi.yaml). The endpoint `/dtal/calculate_ooetourism_levy` accepts a JSON payload with the following fields:

- `taxpayer`: name of the business
- `revenue`: annual revenue
- `municipality_name`: municipality name
- `contribution_group`: contribution group (1-7)

The response returns the calculated tourism levy and related information.

Model Context Protocol description is provided in [model_context.json](model_context.json).
