"""Project wide pytest plugins / fixtures

References:
    - http://alexmic.net/flask-sqlalchemy-pytest/
    - http://flask.pocoo.org/docs/1.0/testing/
"""

import pytest

from busy_beaver.adapters import KeyValueStoreAdapter
from busy_beaver.app import create_app
from busy_beaver.extensions import db as _db, rq as _rq


@pytest.fixture(scope="session")
def vcr_config():
    return {"filter_headers": [("authorization", "DUMMY")]}


@pytest.fixture(scope="module")
def app():
    """Session-wide test `Flask` application.

    Establish an application context before running the tests.
    """
    app = create_app(testing=True)
    ctx = app.app_context()
    ctx.push()
    yield app

    ctx.pop()


@pytest.fixture(scope="module")
def client(app):
    """Create flask test client where we can trigger test requests to app"""
    client = app.test_client()
    yield client


@pytest.fixture(scope="module")
def db(app):
    """Test database."""
    _db.app = app
    _db.create_all()
    yield _db

    _db.drop_all()


@pytest.fixture(scope="function")
def session(db):
    """Creates a new database session for each test."""
    connection = db.engine.connect()
    transaction = connection.begin()
    options = dict(bind=connection, binds={})

    session = db.create_scoped_session(options=options)
    db.session = session
    yield session

    transaction.rollback()
    connection.close()
    session.remove()


@pytest.fixture
def kv_store(session):
    return KeyValueStoreAdapter()


@pytest.fixture(scope="module")
def rq(app):
    yield _rq
