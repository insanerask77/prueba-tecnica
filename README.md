# Random Error Code Service

This project is a simple web service that, upon receiving a request, returns "Hello world" with a 200 OK status code or, on occasion, a random 4xx or 5xx HTTP error code. The entire stack is containerized and includes monitoring with Prometheus and Grafana.

The project is designed to be deployed via a GitLab CI/CD pipeline that automates testing, building, and deploying the application.

## 1. Project Structure

The repository is organized into the following main directories:

-   `src/`: Contains the FastAPI application source code.
-   `tests/`: Contains unit tests for the application.
-   `monitoring/`: Contains configuration files for Prometheus and Grafana.
-   `.gitlab-ci.yml`: Defines the CI/CD pipeline.
-   `docker-compose.yml`: Orchestrates all the services.
-   `Dockerfile`: Defines how to build the application's container image.
-   `nginx.conf`: Configuration for the Nginx reverse proxy.

## 2. Service Architecture

The stack is composed of four main services managed by `docker-compose`:

1.  **`web`**: The FastAPI application running with Gunicorn. It exposes the main API and a `/metrics` endpoint for Prometheus.
2.  **`nginx`**: A reverse proxy that routes external traffic on port 80 to the appropriate services.
3.  **`prometheus`**: Scrapes metrics from the `web` service.
4.  **`grafana`**: Provides a dashboard to visualize the metrics collected by Prometheus.

## 3. Accessing the Services

Once deployed, the services are available at the following endpoints:

-   **Application**: `http://<SERVER_IP>/`
    -   Returns "Hello world" or an error code.
-   **Monitoring Dashboard**: `http://<SERVER_IP>/monitoring/`
    -   Displays a Grafana dashboard with the count of HTTP status codes per minute. Anonymous access is enabled.
-   **Prometheus UI**: `http://<SERVER_IP>/prometheus/`
    -   Allows for running custom PromQL queries.

## 4. Local Development

To run the project locally, you need `docker` and `docker-compose` installed.

1.  **Build the application image:**
    ```bash
    docker build -t random-error-app:local .
    ```

2.  **Set up the environment:**
    Copy the `.env.example` file to `.env` and set the image tag.
    ```bash
    cp .env.example .env
    ```
    Then, ensure the `.env` file contains the following line to use your local image:
    ```
    WEB_IMAGE_TAG=random-error-app:local
    ```

3.  **Run the stack:**
    ```bash
    docker-compose up
    ```
    To run in detached mode, use `docker-compose up -d`.

4.  **Run tests locally:**
    First, install dependencies:
    ```bash
    pip install -r requirements.txt -r requirements-dev.txt
    ```
    Then, run `pytest`:
    ```bash
    pytest
    ```

5.  **Stop the stack:**
    ```bash
    docker-compose down
    ```

## 5. CI/CD Pipeline

The `.gitlab-ci.yml` file defines a four-stage pipeline:

1.  **`lint`**: Checks Python code for style errors using `flake8`.
2.  **`test`**: Runs unit tests using `pytest`.
3.  **`build`**: Builds the Docker image and pushes it to the GitLab Container Registry. It tags the image with the commit SHA and, for the `main` branch, also with `latest`.
4.  **`deploy`**: This stage runs only on the `main` branch and uses a `shell` runner on the target server. It pulls the `latest` image and restarts the services using `docker-compose`.

## 6. Configuration and Secrets

-   **Local Configuration**: Managed via the `.env` file (created from `.env.example`).
-   **CI/CD Secrets**: The pipeline requires `CI_REGISTRY_USER` and `CI_REGISTRY_PASSWORD` to be configured as protected CI/CD variables in GitLab to push to the container registry.
-   **Grafana Credentials**: The default Grafana admin credentials are `admin:admin`, as set in the `docker-compose.yml` file. These should be changed for a real production environment by setting `GF_SECURITY_ADMIN_USER` and `GF_SECURITY_ADMIN_PASSWORD` from GitLab CI/CD variables.
-   **Anonymous Access**: Grafana is configured to allow anonymous viewing of dashboards. This is controlled by `GF_AUTH_ANONYMOUS_ENABLED` in the `docker-compose.yml` file.