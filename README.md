# beta.ooetourismlevy.dtal
Digital Twin Administrative Law of Upper Austrian tourism levy

This repository contains the source code for calculating the Upper Austrian tourism levy.


## Usage

Send a `POST` request to `/dtal/calculate_ooetourism_levy` with JSON:

```json
{
  "municipality_name": "Adlwang",
  "business_activity": "Wildparks",
  "revenue_two_years_ago": 500000
}
```

## Docker

Build the container and run the combined REST API and MCP server on a single port (default `8000`):

```bash
docker build -t ooe-tourism-levy .
docker run -p 8000:8000 ooe-tourism-levy
```

The REST endpoint is available at `http://localhost:8000/dtal/calculate_ooetourism_levy` and the MCP interface via SSE at `http://localhost:8000/dtal/mcp`.

## MCP

The levy calculation is also available as a Model Context Protocol (MCP) tool
for Claude via [FastMCP](https://github.com/anthropics/fastmcp). When the
application is running, the `dtal.calculate_ooetourism_levy` tool can be
accessed over SSE at `/dtal/mcp` using the same parameters as the REST endpoint.

The MCP endpoint now also responds to `HEAD` requests so that clients like
Claude's Custom Connectors can verify connectivity before opening the SSE
stream.
