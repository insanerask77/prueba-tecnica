# ---- Base Image ----
# Use a specific version for reproducibility.
# Using slim-bullseye for a smaller and more secure base.
FROM python:3.12-slim-bullseye as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.7.1

# ---- Builder Stage ----
# This stage installs dependencies into a virtual environment.
FROM base as builder

# Create and activate a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt


# ---- Final Stage ----
# This stage creates the final, lean production image.
FROM base as final

# Create a non-root user for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser

WORKDIR /home/appuser/app

# Copy the virtual environment with dependencies from the builder stage
COPY --from=builder /opt/venv ./.venv
# Copy the application code
COPY --chown=appuser:appgroup src/ ./src

# Set the PATH to include the venv
ENV PATH="/home/appuser/app/.venv/bin:$PATH"

# Expose the port the app runs on
EXPOSE 8000

# The command to run the application using Gunicorn
# -w 4: 4 worker processes. Adjust based on CPU cores.
# -k uvicorn.workers.UvicornWorker: Use Uvicorn for async handling.
# -b 0.0.0.0:8000: Bind to all interfaces on port 8000.
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "src.main:app"]
