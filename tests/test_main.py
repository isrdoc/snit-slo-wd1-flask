import os
import pytest
from main import app, db

# important: this line needs to be set BEFORE the "app" import
os.environ["DATABASE_URL"] = "sqlite:///:memory:"


@pytest.fixture
def client():
    client = app.test_client()

    cleanup()  # clean up before every test

    db.create_all()

    yield client


def cleanup():
    # clean up/delete the DB (drop all tables in the database)
    db.drop_all()


def test_index_not_logged_in(client):
    response = client.get('/')
    assert b'Hi, stranger! Please login' in response.data


def test_index_logged_in(client):
    client.post('/register', data={"email": "igor@srdoc.si", "password": "ninja", "first_name": "Igor"}, follow_redirects=True)
    client.post('/login', data={"email": "igor@srdoc.si", "password": "ninja"}, follow_redirects=True)

    response = client.get('/')
    assert b'Hi, Igor! Welcome back to HTML ;)' in response.data


def test_index_has_logo(client):
    response = client.get('/')
    assert b'/static/img/smartninja-logo.png' in response.data
