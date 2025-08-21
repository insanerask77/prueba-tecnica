import pytest
from httpx import AsyncClient
from unittest.mock import patch

# Import the FastAPI app instance
# Make sure the `src` directory is in the Python path.
# In a real CI setup, you'd configure PYTHONPATH or install the package.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main import app, HTTP_STATUS_CODES

@pytest.mark.asyncio
async def test_health_check():
    """Tests that the /health endpoint always returns 200 OK."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
@patch('random.choice')
async def test_root_success(mock_choice):
    """Tests the root endpoint when a 200 status code is chosen."""
    # Force random.choice to return 200
    mock_choice.return_value = 200

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello world"}
    # Verify that random.choice was called with the correct list of codes
    mock_choice.assert_called_once_with(HTTP_STATUS_CODES)

@pytest.mark.asyncio
@patch('random.choice')
async def test_root_server_error(mock_choice):
    """Tests the root endpoint when a 500 status code is chosen."""
    # Force random.choice to return 500
    mock_choice.return_value = 500

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")

    assert response.status_code == 500
    # The body might contain a default error message from FastAPI.
    # We are primarily concerned with the status code.
    # For a 500 error, the JSON body might not be {"message": "Internal Server Error"}
    # depending on FastAPI version, so we just check the code.

    mock_choice.assert_called_once_with(HTTP_STATUS_CODES)

@pytest.mark.asyncio
@patch('random.choice')
async def test_root_client_error(mock_choice):
    """Tests the root endpoint when a 404 status code is chosen."""
    # Force random.choice to return 404
    mock_choice.return_value = 404

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")

    assert response.status_code == 404
    mock_choice.assert_called_once_with(HTTP_STATUS_CODES)
