import pytest
from app import app as flask_app
from unittest.mock import patch, MagicMock

# Mock the database pool before any tests run
mock_pool = MagicMock()
mock_conn = MagicMock()
mock_cursor = MagicMock()

# Mock the 'with db_pool.connection() as conn:' context
mock_pool.connection.return_value.__enter__.return_value = mock_conn
# Mock the 'with conn.cursor() as cursor:' context
mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
mock_cursor.execute.return_value = None

# Patch the 'db_pool' in the 'app' module
@pytest.fixture(scope='module', autouse=True)
def patch_db():
    with patch('app.db_pool', mock_pool):
        yield

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

def test_health_check(client):
    """Test the health check endpoint."""
    rv = client.get('/health')
    assert rv.status_code == 200
    assert rv.json['status'] == 'healthy'

def test_get_loans(client):
    """Test the GET /api/loans endpoint."""
    rv = client.get('/api/loans')
    assert rv.status_code == 200
    assert isinstance(rv.json, list)
    assert len(rv.json) > 0
