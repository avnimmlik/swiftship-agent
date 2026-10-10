FROM python:3.13-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files first (for Docker layer caching)
COPY pyproject.toml uv.lock ./

# Install all dependencies
RUN uv sync --no-dev

# Copy the rest of the source code
COPY . .

# Expose the port
EXPOSE 8080

# Run the ADK web server
CMD ["uv", "run", "adk", "web", "app", "--host", "0.0.0.0", "--port", "8080", "--allow_origins", "*"]