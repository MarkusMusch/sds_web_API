import os
import sys

from fastapi.testclient import TestClient
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app


def test_generate_uniform_sample():
    """Test the generate_sample_entry function with a valid request for a
    uniform distribution"""

    with TestClient(app) as client:
        response = client.post("/sample", json={
            "distribution_type": "uniform",
            "num_samples": 100,
            "params": [
                {
                    "param_type": "min",
                    "param_val": 0
                },
                {
                    "param_type": "max",
                    "param_val": 1
                }
            ]
        })
        assert response.status_code == 200
        assert response.json() == {"ID": 1}


def test_generate_normal_sample():
    """Test the generate_sample_entry function with a valid request for a
    normal distribution"""

    with TestClient(app) as client:
        response = client.post("/sample", json={
            "distribution_type": "normal",
            "num_samples": 100,
            "params": [
                {
                    "param_type": "mean",
                    "param_val": 0
                },
                {
                    "param_type": "std",
                    "param_val": 1
                }
            ]
        })
        assert response.status_code == 200
        assert response.json() == {"ID": 2}


def test_generate_weibull_sample():
    """Test the generate_sample_entry function with a valid request for a
    weibull distribution"""

    with TestClient(app) as client:
        response = client.post("/sample", json={
            "distribution_type": "weibull",
            "num_samples": 100,
            "params": [
                {
                    "param_type": "shape",
                    "param_val": 1
                },
                {
                    "param_type": "scale",
                    "param_val": 1
                }
            ]
        })
        assert response.status_code == 200
        assert response.json() == {"ID": 3}


def test_generate_uniform_num_args_error():
    """Test the generate_sample_entry function raises a error when given an
    invalid number of arguments"""

    with TestClient(app) as client:
        with pytest.raises(TypeError):
            response = client.post("/sample", json={
                "distribution_type": "uniform",
                "num_samples": 100,
                "params": [
                    {
                        "param_type": "min",
                        "param_val": 0
                    },
                    {
                        "param_type": "max",
                        "param_val": 1
                    },
                    {
                        "param_type": "max",
                        "param_val": 1
                    }
                ]
            })


def test_generate_uniform_param_type_error():
    """Test the generate_sample_entry function raises a error when given an
    invalid parameter type"""

    with TestClient(app) as client:
        with pytest.raises(TypeError):
            response = client.post("/sample", json={
                "distribution_type": "uniform",
                "num_samples": 100,
                "params": [
                    {
                        "param_type": "shape",
                        "param_val": 0
                    },
                    {
                        "param_type": "max",
                        "param_val": 1
                    }
                ]
            })


def test_generate_normal_value_error():
    """Test the generate_sample_entry function raises a error when given an
    invalid parameter value"""

    with TestClient(app) as client:
        with pytest.raises(ValueError):
            response = client.post("/sample", json={
                "distribution_type": "normal",
                "num_samples": 100,
                "params": [
                    {
                        "param_type": "mean",
                        "param_val": 0
                    },
                    {
                        "param_type": "std",
                        "param_val": -1
                    }
                ]
            })


def test_unkown_distribution_error():
    """Test the generate_sample_entry function raises a error when given an
    unknown distribution type"""

    with TestClient(app) as client:
        response = client.post("/sample", json={
            "distribution_type": "exponential",
            "num_samples": 100,
            "params": [
                {
                    "param_type": "mean",
                    "param_val": 0
                },
                {
                    "param_type": "std",
                    "param_val": 1
                }
            ]
        })

        assert response.status_code == 422
        assert response.json() == {
                "detail": [
                    {
                        "ctx": {"enum_values": ["uniform", "normal", "weibull"]},
                        "loc": ["body", "distribution_type"],
                        "msg": "value is not a valid enumeration member; permitted: 'uniform', 'normal', 'weibull'",
                        "type": "type_error.enum"
                    }
                ]
        }
