import psycopg2
from contextlib import contextmanager

# Optional: centralize credentials here
PG_CONFIG = {
    'dbname': "db_ddis",
    'user': "postgres",
    'password': "root",
    'host': "172.31.196.14",
    'port': "5432"
}

@contextmanager
def get_pg_connection(verbose=False):
    """
    Context manager to get a PostgreSQL connection.
    Automatically closes the connection after use.
    """
    conn = None
    try:
        if verbose: print("🔌 Connecting to PostgreSQL...")
        conn = psycopg2.connect(**PG_CONFIG)
        if verbose: print("✅ Connected to PostgreSQL")
        yield conn
    finally:
        if conn:
            conn.close()
            if verbose: print("🔌 PostgreSQL connection closed")