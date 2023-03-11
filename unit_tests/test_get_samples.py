import os
import sys

from fastapi.testclient import TestClient
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app


def test_get_samples():
    """Test the get_samples function"""

    with TestClient(app) as client:
        response = client.get("/samples")
        assert response.status_code == 200
