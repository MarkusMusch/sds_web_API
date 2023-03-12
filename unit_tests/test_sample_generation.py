"""Unit tests for the /sample endpoint

This module contains unit tests for the sample generation endpoint

Functions
----------
    test_generate_uniform_sample
        Test the generate_sample_entry function with a valid request for a
        uniform distribution
    test_generate_normal_sample
        Test the generate_sample_entry function with a valid request for a
        normal distribution
    test_generate_weibull_sample
        Test the generate_sample_entry function with a valid request for a
        weibull distribution
    test_generate_uniform_num_args_error
        Test the generate_sample_entry function with an invalid number of
        arguments for a uniform distribution
    test_generate_uniform_param_type_error
        Test the generate_sample_entry function with an invalid parameter type
    test_generate_normal_value_error
        Test the generate_sample_entry function with an invalid parameter value
    test_generate_unknown_distribution_error
        Test the generate_sample_entry function with an invalid distribution
        type
"""

from fastapi.testclient import TestClient
import pytest
from unittest.mock import patch

from src.endpoints import app


def test_generate_uniform_sample(mock_db_setup):
    """Test the generate_sample_entry function with a valid request for a
    uniform distribution"""

    mock_db_connection, mock_execute = mock_db_setup

    sample = {
            'distribution_type': 'uniform',
            'num_samples': 100,
            'params': [
                {
                    'param_type': 'min',
                    'param_val': 0.0
                },
                {
                    'param_type': 'max',
                    'param_val': 1.0
                }
            ]
            }

    with TestClient(app) as client:

        with patch('src.endpoints.app.db_connection', new=mock_db_connection):

            response = client.post('/sample', json=sample)

            assert response.status_code == 200

            assert {'ID': 1} == response.json()

            mock_execute.assert_called_once_with(
                'INSERT INTO sample_definitions (distribution_type, '
                + 'param_one, param_two, num_samples) VALUES (?, ?, ?, ?)',
                (sample['distribution_type'], sample['params'][0]['param_val'],
                 sample['params'][1]['param_val'], sample['num_samples'])
            )


def test_generate_normal_sample(mock_db_setup):
    """Test the generate_sample_entry function with a valid request for a
    normal distribution"""

    mock_db_connection, mock_execute = mock_db_setup

    sample = {
            'distribution_type': 'normal',
            'num_samples': 100,
            'params': [
                {
                    'param_type': 'mean',
                    'param_val': 0.0
                },
                {
                    'param_type': 'std',
                    'param_val': 1.0
                }
            ]
            }

    with TestClient(app) as client:

        with patch('src.endpoints.app.db_connection', new=mock_db_connection):

            response = client.post('/sample', json=sample)

            assert response.status_code == 200

            assert {'ID': 1} == response.json()

            mock_execute.assert_called_once_with(
                'INSERT INTO sample_definitions (distribution_type, '
                + 'param_one, param_two, num_samples) VALUES (?, ?, ?, ?)',
                (sample['distribution_type'], sample['params'][0]['param_val'],
                 sample['params'][1]['param_val'], sample['num_samples'])
            )


def test_generate_weibull_sample(mock_db_setup):
    """Test the generate_sample_entry function with a valid request for a
    weibull distribution"""

    mock_db_connection, mock_execute = mock_db_setup

    sample = {
            'distribution_type': 'weibull',
            'num_samples': 100,
            'params': [
                {
                    'param_type': 'shape',
                    'param_val': 1.0
                },
                {
                    'param_type': 'scale',
                    'param_val': 1.0
                }
            ]
            }

    with TestClient(app) as client:

        with patch('src.endpoints.app.db_connection', new=mock_db_connection):

            response = client.post('/sample', json=sample)

            assert response.status_code == 200

            assert {'ID': 1} == response.json()

            mock_execute.assert_called_once_with(
                'INSERT INTO sample_definitions (distribution_type, param_one,'
                + ' param_two, num_samples) VALUES (?, ?, ?, ?)',
                (sample['distribution_type'], sample['params'][0]['param_val'],
                 sample['params'][1]['param_val'], sample['num_samples'])
            )


def test_generate_uniform_num_args_error(mock_db_setup):
    """Test the generate_sample_entry function raises a error when given an
    invalid number of arguments"""

    mock_db_connection, mock_execute = mock_db_setup

    sample = {
                'distribution_type': 'uniform',
                'num_samples': 100,
                'params': [
                    {
                        'param_type': 'min',
                        'param_val': 0
                    },
                    {
                        'param_type': 'max',
                        'param_val': 1
                    },
                    {
                        'param_type': 'max',
                        'param_val': 1
                    }
                ]
             }

    with TestClient(app) as client:
        with patch('src.endpoints.app.db_connection', new=mock_db_connection):
            with pytest.raises(TypeError):
                client.post('/sample', json=sample)


def test_generate_uniform_param_type_error(mock_db_setup):
    """Test the generate_sample_entry function raises a error when given an
    invalid parameter type"""

    mock_db_connection, mock_execute = mock_db_setup

    sample = {
                'distribution_type': 'uniform',
                'num_samples': 100,
                'params': [
                    {
                        'param_type': 'shape',
                        'param_val': 1
                    },
                    {
                        'param_type': 'max',
                        'param_val': 1
                    }
                ]
             }

    with TestClient(app) as client:
        with patch('src.endpoints.app.db_connection', new=mock_db_connection):
            with pytest.raises(TypeError):
                client.post('/sample', json=sample)


def test_generate_normal_value_error(mock_db_setup):
    """Test the generate_sample_entry function raises a error when given an
    invalid parameter value"""

    mock_db_connection, mock_execute = mock_db_setup

    sample = {
            'distribution_type': 'normal',
            'num_samples': 100,
            'params': [
                {
                    'param_type': 'mean',
                    'param_val': 0
                },
                {
                    'param_type': 'std',
                    'param_val': -1
                }
            ]
            }

    with TestClient(app) as client:
        with patch('src.endpoints.app.db_connection', new=mock_db_connection):
            with pytest.raises(ValueError):
                client.post('/sample', json=sample)


def test_generate_unkown_distribution_error(mock_db_setup):
    """Test the generate_sample_entry function raises a error when given an
    unknown distribution type"""

    mock_db_connection, mock_execute = mock_db_setup

    with TestClient(app) as client:
        with patch('src.endpoints.app.db_connection', new=mock_db_connection):
            response = client.post('/sample', json={
                'distribution_type': 'exponential',
                'num_samples': 100,
                'params': [
                    {
                        'param_type': 'mean',
                        'param_val': 0
                    },
                    {
                        'param_type': 'std',
                        'param_val': 1
                    }
                ]
            })

            assert response.status_code == 422
            assert response.json() == {
                    "detail": [
                        {
                            "ctx": {"enum_values": ["uniform", "normal",
                                    "weibull"]},
                            "loc": ["body", "distribution_type"],
                            "msg": "value is not a valid enumeration member; "
                            + "permitted: 'uniform', 'normal', 'weibull'",
                            "type": "type_error.enum"
                        }
                    ]
            }
