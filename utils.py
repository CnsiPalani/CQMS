from db import get_connection

def user_exists(username):
    """
    Checks if a user with the given username exists in the database.

    Args:
        username (str): The username to check for existence.

    Returns:
        bool: True if the user exists, False otherwise.

    Raises:
        Any exceptions raised during database connection or query execution are caught and handled internally.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
            return result is not None
        except Exception as e:
            # Handle or log the exception as needed
            print(f"Error querying user: {e}")
            return False
    finally:
        conn.close()