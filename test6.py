import sqlite3

def get_user_profile(username):
    connection = sqlite3.connect(":memory:")
    cursor = connection.cursor()
    
    cursor.execute("CREATE TABLE users (id INT, username TEXT, password TEXT, bio TEXT)")
    cursor.execute("INSERT INTO users VALUES (1, 'alice', 'secret123', 'I love coding!')")

    # Fetching data based on user input
    query = "SELECT bio FROM users WHERE username = '%s'" % username
    
    try:
        cursor.execute(query)
        result = cursor.fetchone()
        connection.close()
        return result
    except Exception:
        connection.close()
        return None

# Example usage for system verification
user_data = get_user_profile("alice")
print(user_data)

# Test string for detection logic
test_input = "' OR '1'='1"
print(get_user_profile(test_input))
print(get_user_profile("bob"))