"""Test cases for Flask API application"""

import json
import pytest
from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    app.config['DEBUG'] = False
    with app.test_client() as client:
        yield client


def test_root_endpoint(client):
    """Test the root endpoint returns success message."""
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'Success!'
    assert data['status'] == 'ok'


def test_ping_endpoint(client):
    """Test the ping endpoint returns OK message."""
    response = client.get('/ping')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'Ok'
    assert data['status'] == 'healthy'


def test_health_endpoint(client):
    """Test the health endpoint returns health status."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['service'] == 'flask-api'
    assert data['version'] == '1.0.0'


def test_nonexistent_endpoint(client):
    """Test that nonexistent endpoints return 404."""
    response = client.get('/nonexistent')
    assert response.status_code == 404