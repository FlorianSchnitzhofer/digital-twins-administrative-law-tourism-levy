"""Application entry point exposing REST and MCP interfaces."""

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.wsgi import WSGIMiddleware

from dtal_toursimlevy.logic_ooetourism_levy import app as flask_app
from mcp_server import mcp


# Root application that will host both the REST API and the MCP endpoint
app = FastAPI()

# Allow any origin/methods so that the MCP endpoint can be called from a
# browser-based client such as Claude's custom connector.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- MCP ------------------------------------------------------------------
# The FastMCP SSE application does not handle HEAD requests which are issued by
# Claude to verify connectivity.  We wrap the SSE app in another FastAPI app
# that returns ``200`` on ``HEAD`` and delegates all other requests to the
# original SSE application.
mcp_app = FastAPI()


@mcp_app.head("/")
async def _head_handler() -> Response:  # pragma: no cover - trivial
    """Return an empty 200 response for health checks."""

    return Response(status_code=200)


# Mount the FastMCP SSE handler under the wrapper app
mcp_app.mount("/", mcp.sse_app())

# Expose the MCP endpoint under /dtal/mcp
app.mount("/dtal/mcp", mcp_app)


# --- REST -----------------------------------------------------------------
# Mount existing Flask app for REST endpoints
app.mount("/", WSGIMiddleware(flask_app))

