import sys
print(sys.path)
import pytest
import json
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy 
# from app.views import api, db
from app import create_app

@pytest.fixture
def client():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'
    })
    yield app.test_client()

def test_get_attractions_no_keyword(client):
    response = client.get('/api/attractions')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'nextPage' in data
    assert 'data' in data

def test_get_attractions_with_keyword(client):
    response = client.get('/api/attractions?keyword=test')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'nextPage' in data
    assert 'data' in data

def test_get_attractions_invalid_page_number(client):
    response = client.get('/api/attractions?page=-1')
    assert response.status_code == 500
    data = json.loads(response.data)
    assert data['error'] is True
    assert 'message' in data

def test_get_attractions_invalid_page_number(client):
    response = client.get('/api/attractions?page=abc')
    assert response.status_code == 500
    data = json.loads(response.data)
    assert data['error'] is True
    assert 'message' in data

def test_get_attraction_by_id(client):
    response = client.get('/api/attraction/1')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'data' in data

def test_get_attraction_by_invalid_id(client):
    response = client.get('/api/attraction/abc')
    assert response.status_code == 500
    data = json.loads(response.data)
    assert data['error'] is True
    assert 'message' in data

def test_get_mrts(client):
    response = client.get('/api/mrts')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'data' in data
