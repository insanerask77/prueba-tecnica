import random
from fastapi import FastAPI, Response
from prometheus_fastapi_instrumentator import Instrumentator

# --- Constants ---
# Add more 200s to make it the most frequent status code.
HTTP_STATUS_CODES = [
    200, 200, 200, 200, 200, 200, 200,  # 70% chance of success
    400, 404, 422,  # Bad requests
    500, 502, 503  # Server errors
]

# --- Application Setup ---
app = FastAPI(
    title="Random Error Service",
    description="A simple web service that returns random HTTP status codes.",
    version="1.0.0",
)

# Instrument the app with Prometheus metrics
# This exposes a /metrics endpoint automatically
Instrumentator().instrument(app).expose(app)


# --- API Endpoints ---
@app.get("/", summary="Root endpoint with random status codes")
def get_root(response: Response):
    """
    This endpoint returns a "Hello world" message with a 200 OK status code,
    or randomly returns a 4xx or 5xx HTTP error status code.
    """
    status_code = random.choice(HTTP_STATUS_CODES)
    response.status_code = status_code

    if status_code == 200:
        return {"message": "Hello world"}
    else:
        # For non-200 responses, FastAPI sends a default message
        # corresponding to the status code. We return an empty dict
        # to avoid overriding it with a success-oriented payload.
        return {}


@app.get("/health", summary="Health check endpoint")
def get_health():
    """
    A simple health check endpoint that always returns 200 OK.
    Useful for liveness probes in container orchestrators.
    """
    return {"status": "ok"}
