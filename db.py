import mysql.connector

def get_connection():
    """
    Establishes and returns a connection to the MySQL database.

    Attempts to connect to a MySQL database using the specified host, user, password, and database name.
    If the connection is successful, returns the connection object.
    If an error occurs during connection, prints the error and returns None.

    Returns:
        mysql.connector.connection.MySQLConnection or None: The database connection object if successful, otherwise None.
    """
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="password",
            database="cqms"
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None