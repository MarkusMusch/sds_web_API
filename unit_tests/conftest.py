import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_db_setup():
    """Mock the database connection"""

    mock_db_connection = MagicMock()
    mock_execute = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.lastrowid = 1
    mock_cursor.execute = mock_execute
    mock_db_connection.cursor.return_value = mock_cursor
    mock_db_connection.cursor.return_value.__enter__.return_value = mock_cursor

    yield mock_db_connection, mock_execute