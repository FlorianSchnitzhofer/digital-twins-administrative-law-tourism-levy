# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .
RUN chmod +x start.sh

# Ensure Python can find modules in src
ENV PYTHONPATH=/app/src
ENV PORT=8000
EXPOSE 8000

# Start combined REST and MCP server
CMD ["./start.sh"]
