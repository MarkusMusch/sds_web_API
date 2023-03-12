"""Unit tests for the /sample/{id}/statistics endpoint

This module contains unit tests for the get_sample_statistics function

Functions
----------
    mock_sample_def
        Mock a sample definition for testing
    test_get_stats
        Test the get_sample_statistics function with a mocked database call
    test_get_stats_invalid_id
        Test the get_sample_statistics function with an invalid distribution id
"""

from fastapi.testclient import TestClient
import pytest
from unittest.mock import patch

from src.endpoints import app


@pytest.fixture
def mock_sample_def():
    """Mock sample definition for testing"""

    return {
        "id": 1,
        "distribution_type": "uniform",
        "param_one": 0,
        "param_two": 1,
        "num_samples": 100
    }


def test_get_stats(mock_db_setup, mock_sample_def):
    """Test the get_samples function with a mocked database call

    Parameters
    ----------
    mock_db_setup : fixture
        Mock database connection
    mock_sample_def : fixture
        Mock sample definition
    """

    mock_db_connection, mock_execute = mock_db_setup

    mock_cursor = mock_db_connection.cursor.return_value

    mock_cursor.fetchone.return_value = mock_sample_def

    with TestClient(app) as client:

        with patch('src.endpoints.app.db_connection', new=mock_db_connection):

            response = client.get('/sample/1/statistics')

            assert response.status_code == 200

            assert mock_sample_def == response.json()[0]

            mock_execute.assert_called_once_with('SELECT * FROM '
                                                 + 'sample_definitions WHERE'
                                                 + ' id = ?', (1,))


def test_get_stats_invalid_id():
    """Test the get_samples function throws the correct exception for an
    invalid ID"""

    with TestClient(app) as client:
        with pytest.raises(ValueError):
            client.get("/sample/-1/statistics")
