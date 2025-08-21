import random
from fastapi import FastAPI, Response
from prometheus_fastapi_instrumentator import Instrumentator, metrics

# --- Constants ---
HTTP_STATUS_CODES = [
    200, 200, 200, 200, 200, 200, 200,  # 70% chance of success
    400, 404, 422,                        # Client errors
    500, 502, 503                          # Server errors
]

# --- Application Setup ---
app = FastAPI(
    title="Random Error Service",
    description="A simple web service that returns random HTTP status codes.",
    version="1.0.0",
)

# --- Instrumentator with custom labels ---
instrumentator = Instrumentator()

# Track latency with exact HTTP status codes as a label
instrumentator.add(
    metrics.latency(
        metric_name="http_request_duration_seconds",
        labels={"status_code": lambda r: str(r.status_code)}
    )
)

# Track total requests with exact status code
instrumentator.add(
    metrics.requests(
        metric_name="http_requests_total",
        labels={"status_code": lambda r: str(r.status_code)}
    )
)

# Track request/response size
instrumentator.add(metrics.request_size())
instrumentator.add(metrics.response_size())

# Expose metrics at /metrics
instrumentator.instrument(app).expose(app)


# --- API Endpoints ---
@app.get("/", summary="Root endpoint with random status codes")
def get_root(response: Response):
    status_code = random.choice(HTTP_STATUS_CODES)
    response.status_code = status_code
    return {"message": "Hello world"} if status_code == 200 else {}

@app.get("/health", summary="Health check endpoint")
def get_health():
    return {"status": "ok"}
