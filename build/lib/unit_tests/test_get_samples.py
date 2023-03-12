"""Unit tests for the /samples endpoint

Functions
----------
    test_get_samples
        Test the get_samples function
"""

from fastapi.testclient import TestClient

from src.endpoints import app


def test_get_samples():
    """Test the get_samples function"""

    with TestClient(app) as client:
        response = client.get("/samples")
        assert response.status_code == 200
