import os
import sys
from flask import Flask, jsonify, request
import psycopg # <-- Changed
from psycopg.pool import ConnectionPool # <-- Changed

app = Flask(__name__)

# --- Database Connection ---
# All config is read from environment variables
try:
    # Use a connection string for psycopg3
    conninfo = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', 5432)}/{os.getenv('POSTGRES_DB')}"
    db_pool = ConnectionPool(conninfo, min_size=1, max_size=10)
    
    # Test connection on startup
    with db_pool.connection() as conn:
        conn.execute("SELECT 1")
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
        # 'with' handles getconn/putconn automatically
        with db_pool.connection() as conn:
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
