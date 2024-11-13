from flask import Flask, request, make_response
import mysql.connector
import socket
from datetime import datetime, timedelta

app = Flask(__name__)

# Database connection configuration
db_config = {
    'user': 'root',
    'password': 'admin',
    'host': 'db',  # This refers to the MySQL service name in docker-compose.yml
    'database': 'mydb',
}

# Function to establish a database connection
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Function to convert datetime to the correct HTTP-date format
def format_cookie_expires(expiration_datetime):
    return expiration_datetime.strftime("%a, %d-%b-%Y %H:%M:%S GMT")

# Route to increment the counter and log access details
@app.route('/')
def index():
    try:
        # Establish database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Increment the global counter
        cursor.execute("UPDATE counter SET count = count + 1")
        conn.commit()

        # Get the server's internal IP address
        server_ip = socket.gethostbyname(socket.gethostname())

        # Log the access with the client's IP, date, and server IP
        client_ip = request.remote_addr
        date_time = datetime.now()
        cursor.execute(
            "INSERT INTO access_log (date, client_ip, server_ip) VALUES (%s, %s, %s)",
            (date_time, client_ip, server_ip)
        )
        conn.commit()

        # Close the database connection
        cursor.close()
        conn.close()

        # Check if cookie exists before setting a new one
        if 'srv_id' not in request.cookies:
            # Set a 5-minute cookie with the server's internal IP for sticky sessions
            expires = datetime.now() + timedelta(minutes=5)
            expires_str = format_cookie_expires(expires)

            response = make_response(f"Internal IP of the server: {server_ip}")
            response.set_cookie('srv_id', server_ip, expires=expires_str)

        else:
            # If the cookie already exists, just create the response
            response = make_response(f"Internal IP of the server: {server_ip}")

        return response

    except mysql.connector.Error as err:
        # Handle database connection errors
        print(f"Database error: {err}")
        return "Database connection error", 500

# Route to display the global counter value
@app.route('/showcount')
def showcount():
    try:
        # Establish database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Retrieve the counter value from the database
        cursor.execute("SELECT count FROM counter")
        count = cursor.fetchone()[0]

        # Close the database connection
        cursor.close()
        conn.close()

        # Return the counter value to the browser
        return str(count)

    except mysql.connector.Error as err:
        # Handle database connection errors
        print(f"Database error: {err}")
        return "Database connection error", 500

# Main entry point for the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
