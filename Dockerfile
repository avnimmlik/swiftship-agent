# Dockerfile for the customer-support-agent
# -------------------------------------------------
# Base image with a lightweight, recent Python version.
FROM python:3.13-slim

# Set a non‑root user for security (optional).
RUN useradd -m appuser && chown -R appuser /app
USER appuser

WORKDIR /app

# Install uv – the fast Python package manager used by this project.
RUN pip install --no-cache-dir uv

# Copy the lock files first so Docker can cache dependency installation.
COPY pyproject.toml uv.lock ./

# Install all dependencies (including google‑adk) into the container.
RUN uv sync --no-dev

# Copy the rest of the source code.
COPY . .

# Expose the port used by the ADK web server.
EXPOSE 8080

# Run the agent web UI. The host must be 0.0.0.0 for cloud services.
CMD ["uv", "run", "adk", "web", "app", "--host", "0.0.0.0", "--port", "8080", "--allow_origins", "*"]