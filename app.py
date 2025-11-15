import os
import sys
from flask import Flask, jsonify, request
from contextlib import contextmanager

# Try to support multiple psycopg pool implementations (psycopg v3, psycopg_pool package, or psycopg2)
make_pool = None

# Prefer psycopg v3 pool
try:
    from psycopg.pool import ConnectionPool as _PsycopgV3Pool

    def make_pool(conninfo, min_size=1, max_size=10):
        return _PsycopgV3Pool(conninfo, min_size=min_size, max_size=max_size)

except Exception:
    # Fallback to the separate psycopg_pool package
    try:
        from psycopg_pool import ConnectionPool as _PsycopgPoolPackage

        def make_pool(conninfo, min_size=1, max_size=10):
            return _PsycopgPoolPackage(conninfo, min_size=min_size, max_size=max_size)

    except Exception:
        # Final fallback to psycopg2's SimpleConnectionPool with an adapter that exposes
        # a .connection() context manager and an .execute() convenience method to
        # match psycopg v3 usage in the app.
        try:
            import psycopg2
            from psycopg2.pool import SimpleConnectionPool as _Psycopg2SimplePool

            class _Psycopg2PoolAdapter:
                def __init__(self, pool):
                    self._pool = pool

                @contextmanager
                def connection(self):
                    raw = self._pool.getconn()
                    try:
                        class ConnWrapper:
                            def __init__(self, raw_conn):
                                self._raw = raw_conn

                            def execute(self, query, *args, **kwargs):
                                with self._raw.cursor() as cur:
                                    cur.execute(query, *args, **kwargs)

                            def cursor(self):
                                return self._raw.cursor()

                            def commit(self):
                                try:
                                    self._raw.commit()
                                except Exception:
                                    pass

                            def rollback(self):
                                try:
                                    self._raw.rollback()
                                except Exception:
                                    pass

                        yield ConnWrapper(raw)
                    finally:
                        try:
                            self._pool.putconn(raw)
                        except Exception:
                            pass

            def make_pool(conninfo, min_size=1, max_size=10):
                pool = _Psycopg2SimplePool(min_size, max_size, conninfo)
                return _Psycopg2PoolAdapter(pool)

        except Exception:
            make_pool = None

app = Flask(__name__)

# --- Database Connection ---
# All config is read from environment variables
try:
    if make_pool is None:
        raise RuntimeError('No supported DB pool implementation is installed')

    # Use a connection string for psycopg3 or a DSN for psycopg2
    conninfo = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('DB_HOST', os.getenv('PGHOST', 'localhost'))}:{os.getenv('DB_PORT', os.getenv('PGPORT', 5432))}/{os.getenv('POSTGRES_DB')}">
    db_pool = make_pool(conninfo, min_size=1, max_size=10)

    # Test connection on startup
    with db_pool.connection() as conn:
        try:
            # psycopg3 supports conn.execute; adapter for psycopg2 provides execute too
            conn.execute("SELECT 1")
        except AttributeError:
            # fall back to cursor-based execution
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
    print("Database connection pool created successfully")
except Exception as e:
    print(f"Error creating connection pool: {e}", file=sys.stderr)
    db_pool = None

# --- API Endpoints ---

# Health check
@app.route('/health')
def health_check():
    if db_pool is None:
        return jsonify(status='unhealthy', database='disconnected', error='Pool not initialized'), 503

    try:
        # 'with' handles getconn/putconn automatically for all supported pools
        with db_pool.connection() as conn:
            try:
                conn.execute('SELECT 1')
            except AttributeError:
                with conn.cursor() as cursor:
                    cursor.execute('SELECT 1')
        return jsonify(status='healthy', database='connected'), 200
    except Exception as e:
        return jsonify(status='unhealthy', database='disconnected', error=str(e)), 503

# Get all loans
@app.route('/api/loans', methods=['GET'])
def get_loans():
    # Mock data for demo
    return jsonify([{'id': 1, 'amount': 1000}, {'id': 2, 'amount': 2000}])

# Get specific loan
@app.route('/api/loans/<int:id>', methods=['GET'])
def get_loan(id):
    return jsonify({'id': id, 'amount': 1000, 'applicant': 'Mock User'})

# Create new loan
@app.route('/api/loans', methods=['POST'])
def create_loan():
    return jsonify({'id': 3, **request.json}), 201

# Get loan stats
@app.route('/api/stats', methods=['GET'])
def get_stats():
    return jsonify({'total_loans': 2, 'total_value': 3000})

# --- Server Start ---
if __name__ == '__main__':
    # This is for local Flask development (e.g., python app.py)
    app.run(host='0.0.0.0', port=os.getenv('PORT', 8080), debug=True)
