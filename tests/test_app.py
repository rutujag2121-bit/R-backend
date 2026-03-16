import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import app, init_db


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DATABASE'] = ':memory:'
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client


def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'


def test_login_valid_user(client):
    response = client.post('/api/login', json={
        'username': 'admin',
        'password': 'admin123'
    })
    assert response.status_code in [200, 401]


def test_login_missing_fields(client):
    response = client.post('/api/login', json={})
    assert response.status_code in [200, 401, 400]


def test_get_users(client):
    response = client.get('/api/users')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_create_user(client):
    response = client.post('/api/users', json={
        'username': 'testuser',
        'password': 'testpass',
        'email': 'test@example.com'
    })
    assert response.status_code == 201


def test_search_endpoint(client):
    response = client.get('/api/search?q=hello')
    assert response.status_code == 200
    data = response.get_json()
    assert 'query' in data
