import os
import sys

from fastapi.testclient import TestClient
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app


# def test_get_samples():
#    """Test the get_samples function"""

#    with TestClient(app) as client:
#        client.post("/sample", json={
#            "distribution_type": "uniform",
#            "num_samples": 100,
#            "params": [
#                {
#                    "param_type": "min",
#                    "param_val": 0
#                },
#                {
#                    "param_type": "max",
#                    "param_val": 1
#                }
#            ]
#        })

#        response = client.get("/sample/1/statistics")
#        assert response.status_code == 200


def test_get_samples_invalid_id():
    """Test the get_samples function for an invalid ID"""

    with TestClient(app) as client:
        with pytest.raises(KeyError):
            response = client.get(f"/sample/-1/statistics")
