#!/bin/sh
set -e

# Run combined ASGI application (REST API + MCP)
exec uvicorn app:app --host 0.0.0.0 --port ${WEBSITES_PORT:-${PORT:-8000}}
