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

# Database connection configuration
db_config = {
    'user': 'root',
    'password': 'admin',
    'host': 'db',  # MySQL service name in docker-compose.yml
    'database': 'mydb',
}

# Establish a database connection
def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def index():
    conn = None  # Initialize conn to None
    try:
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Increment the global counter
            cursor.execute("UPDATE counter SET count = count + 1")
            conn.commit()

            # Get server IP and log client access
            server_ip = socket.gethostbyname(socket.gethostname())
            client_ip = request.remote_addr
            date_time = datetime.now()

            cursor.execute(
                "INSERT INTO access_log (date, client_ip, server_ip) VALUES (%s, %s, %s)",
                (date_time, client_ip, server_ip)
            )
            conn.commit()

            # Create the response
            response = make_response(f"server ip: {server_ip}")
        except Exception as e:
            # Log and handle any database operation errors
            app.logger.error(f"Database operation failed: {e}")
            conn.rollback()
            return make_response("An error occurred while processing the request.", 500)
        finally:
            # Ensure the cursor is closed
            cursor.close()

        return response
    except Exception as e:
        # Log and handle any connection errors
        app.logger.error(f"Failed to connect to the database: {e}")
        return make_response("An error occurred while connecting to the database.", 500)
    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()


# Route to display the global counter value
@app.route('/showcount')
def showcount():
    conn = None  # Initialize the database connection to None
    try:
        # Establish a connection to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query to fetch the current value of the counter
        cursor.execute("SELECT count FROM counter")
        result = cursor.fetchone()

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
    finally:
        # Ensure the database resources are properly closed
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
