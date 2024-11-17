import logging
from logging.handlers import RotatingFileHandler
import mysql.connector
import socket
from flask import Flask, request, make_response
from datetime import datetime
import sys
import os

# Ensure the logs directory exists
os.makedirs('/app/logs', exist_ok=True)

# Configure logging
log_file = '/app/logs/app.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Log to stdout
        RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=3)  # Log to a file
    ]
)
logger = logging.getLogger(__name__)

# Flask app instance
app = Flask(__name__)

# Check if required environment variables are set
required_vars = ['DATABASE_USER', 'DATABASE_PASSWORD', 'DATABASE_HOST', 'DATABASE_NAME']
for var in required_vars:
    if not os.getenv(var):
        raise EnvironmentError(f"Required environment variable {var} not set")

# Database connection configuration using environment variables
db_config = {
    'user': os.getenv('DATABASE_USER'),
    'password': os.getenv('DATABASE_PASSWORD'),
    'host': os.getenv('DATABASE_HOST'),
    'database': os.getenv('DATABASE_NAME'),
}

# Establish a database connection
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Helper function to execute queries
def execute_query(query, params=(), fetch_one=False):
    conn = None  # Initialize connection variable
    cursor = None  # Initialize cursor variable
    try:
        conn = get_db_connection()  # Establish a database connection
        cursor = conn.cursor()  # Create a cursor to interact with the database
        cursor.execute(query, params)  # Execute the given query with parameters
        if fetch_one:
            return cursor.fetchone()  # Fetch a single row if requested
        else:
            conn.commit()  # Commit the transaction if not fetching data
    except mysql.connector.Error as e:
        app.logger.error(f"Database error: {e}")  # Log any database-specific errors
        raise  # Re-raise the exception to notify the caller
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")  # Log any other unexpected exceptions
        raise  # Re-raise the exception to notify the caller
    finally:
        if cursor:
            cursor.close()  # Ensure the cursor is closed to release resources
        if conn:
            conn.close()  # Ensure the connection is closed to prevent leaks

@app.route('/')
def index():
    try:
        # Increment the global counter
        execute_query("UPDATE counter SET count = count + 1")

        # Get server IP and log client access
        server_ip = socket.gethostbyname(socket.gethostname())  # Get the IP address of the server where the application is running
        client_ip = request.remote_addr                         # Get the IP address of the client making the request
        date_time = datetime.now()                              # Get the current date and time for logging purposes

        execute_query(
            "INSERT INTO access_log (date, client_ip, server_ip) VALUES (%s, %s, %s)",
            params=(date_time, client_ip, server_ip)
        )

        # Create the response
        return make_response(f"server ip: {server_ip}")
    except Exception as e:
        app.logger.error(f"Error in index route: {e}")
        return make_response("An error occurred while processing the request.", 500)


# Route to display the global counter value
@app.route('/showcount')
def showcount():
    try:
        # Query to fetch the current value of the counter
        result = execute_query("SELECT count FROM counter", fetch_one=True)

        if result is None:
            # Handle case where the counter table is empty
            app.logger.error("No counter value found in the database.")
            return "Counter value not found", 404

        # Extract the counter value
        count = result[0]

        # Log the counter value
        app.logger.info(f"Counter value retrieved: {count}")

        # Return the counter value
        return f"counter number: {count}"
    except mysql.connector.Error as err:
        # Log database-specific errors
        app.logger.error(f"Database error: {err}")
        return "Database connection error", 500
    except Exception as e:
        # Log any other unexpected exceptions
        app.logger.error(f"Unexpected error: {e}")
        return "An unexpected error occurred", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
