"""Fixtures for auth tests."""
import sqlite3
from pathlib import Path
from typing import Union
from contextlib import closing

import pytest
from yoyo import get_backend, read_migrations
from yoyo.migrations import Migration, MigrationList

from gn3.migrations import apply_migrations, rollback_migrations

@pytest.fixture(scope="session")
def auth_testdb_path(test_app_config): # pylint: disable=redefined-outer-name
    """Get the test application's auth database file"""
    return test_app_config["AUTH_DB"]

@pytest.fixture(scope="session")
def auth_migrations_dir(test_app_config): # pylint: disable=redefined-outer-name
    """Get the test application's auth database file"""
    return test_app_config["AUTH_MIGRATIONS"]

def apply_single_migration(db_uri: Union[Path, str], migration: Migration):
    """Utility to apply a single migration"""
    apply_migrations(get_backend(f"sqlite:///{db_uri}"), MigrationList([migration]))

def rollback_single_migration(db_uri: Union[Path, str], migration: Migration):
    """Utility to rollback a single migration"""
    rollback_migrations(get_backend(f"sqlite:///{db_uri}"), MigrationList([migration]))

@pytest.fixture(scope="session")
def backend(auth_testdb_path): # pylint: disable=redefined-outer-name
    return get_backend(f"sqlite:///{auth_testdb_path}")

@pytest.fixture(scope="session")
def all_migrations(auth_migrations_dir): # pylint: disable=redefined-outer-name
    return read_migrations(auth_migrations_dir)

@pytest.fixture(scope="function")
def conn_after_auth_migrations(backend, auth_testdb_path, all_migrations): # pylint: disable=redefined-outer-name
    """Run all migrations and return a connection to the database after"""
    apply_migrations(backend, all_migrations)
    with closing(sqlite3.connect(auth_testdb_path)) as conn:
        yield conn

    rollback_migrations(backend, all_migrations)

def migrations_up_to(migration, migrations_dir):
    migrations = read_migrations(migrations_dir)
    index = [mig.path for mig in migrations].index(migration)
    return MigrationList(migrations[0:index])
