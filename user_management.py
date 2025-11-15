from sqlite3 import connect

from security import generate_salt, hash_password

#############################################################
###################### USER MANAGEMENT ######################
#############################################################

class User:
    """
    Represents a user in the system.
    Demonstrates OOP concept of Abstraction by hiding complexity.
    """
    def __init__(self, user_id, username, password_hash, level = 1, flight_minutes = 0):

        # Defensive Programming
        
        if not isinstance(user_id, int) or user_id < 1:
            raise ValueError("User ID a must be a natural number")
        if not isinstance(username, str) or len(username) == 0:
            raise TypeError("Username must be a non-empty string")
        if not isinstance(password_hash, int) or user_id < 1:
            raise TypeError("Password hash must be a natural number")
        
        self.user_id = user_id
        self.username = username
        self.password_hash = password_hash
        self.level = level
        self.flight_minutes = max(0, flight_minutes)  # Ensure non-negative

class UserManager:
    """
    Manages user authentication and database operations.
    Demonstrates database integration with SQLite.
    Demonstrates SQL table creation, selection, and insertion.
    """
    def __init__(self, db_path = "users.db"):
        try:
            self.conn = connect(db_path)
            self.cursor = self.conn.cursor()
        except:
            raise RuntimeError("Failed to connect to database")
        self.create_table()
        self.add_default_user()

    def create_table(self):
        """
        Creates the users table if it doesn't exist.
        Demonstrates SQL schema design with:
        - Primary key with auto-increment
        - Unique constraints
        - Default values
        """
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash INTEGER NOT NULL,
                salt INTEGER NOT NULL,
                level INTEGER DEFAULT 1,
                flight_minutes REAL DEFAULT 0)""")
        self.conn.commit()

    def add_default_user(self):
        """
        Adds a default test user if none exists.
        """
        username = "test"
        password = "password"
        salt = generate_salt()
        password_hash = hash_password(password, salt)

        # Check if user exists before inserting
        self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if not self.cursor.fetchone():
            self.cursor.execute("""
                                INSERT INTO users
                                    (username, password_hash, salt, level, flight_minutes)
                                VALUES (?, ?, ?, ?, ?)""", (username, password_hash, salt, 5, 12))
            self.conn.commit()

    def register_user(self, username, password):
        """
        Registers a new user with salted password hash.
        Returns True if successful, False if username exists.
        Demonstrates security best practices for password storage.
        """
        # Defensive Programming
        if not isinstance(username, str) or not isinstance(password, str) or len(username) == 0:
            raise TypeError("Username and password must be strings")
        self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if self.cursor.fetchone():
            return False

        salt = generate_salt()
        password_hash = hash_password(password, salt)
        
        self.cursor.execute("INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)", 
                            (username, password_hash, salt))
        self.conn.commit()
        return True  # Registration successful

    def login(self, username, password):
        """
        Authenticates a user by username and password.
        Returns User object if successful, None if failed.
        Demonstrates secure password verification technique.
        """
        self.cursor.execute('''
            SELECT user_id, username, password_hash, salt, level, flight_minutes FROM users
            WHERE username = ?''',
            (username,))
        user_data = self.cursor.fetchone()
        
        if user_data:
            user_id, username, stored_hash, salt, level, flight_minutes = user_data
            # Verify password by hashing with same salt and comparing
            if stored_hash ==  hash_password(password, salt):
                return User(user_id, username, stored_hash, level, flight_minutes)
        return None

    def update_level(self, user_id, new_level):
        """
        Updates the user's level in the database.
        Ensures level stays within valid range (1-10).
        Returns the updated level.
        """
        # Ensure level is within bounds (1-10)
        # Defensive Programming
        if not isinstance(new_level, int):
            raise TypeError("Level must be an integer")
        if new_level < 1:
            new_level = 1
        elif new_level > 10:
            new_level = 10
            
        # Update the database
        self.cursor.execute("UPDATE users SET level = ? WHERE user_id = ?", (new_level, user_id))
        self.conn.commit()
        
        # Return the final level value
        return new_level

    def update_flight_minutes(self, user_id, minutes_to_add):
        """
        Updates the user's accumulated flight time in the database.
        Returns the new total flight minutes.
        """
        # Defensive Programming
        if not isinstance(minutes_to_add, (int, float)):
            raise TypeError("Minutes must be a number")
        
        # Fetch current flight minutes
        self.cursor.execute("SELECT flight_minutes FROM users WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()  # Fetch only once and store the result

        # Defensive Programming
        if result is None:
            raise ValueError("User ID not found")
                
        # Calculate new total
        current_minutes = result[0]  # Access the first column of the result
        new_total = max(0, current_minutes + minutes_to_add)  # Ensure non-negative
        
        # Update the database
        self.cursor.execute("UPDATE users SET flight_minutes = ? WHERE user_id = ?", (new_total, user_id))
        self.conn.commit()
        
        # Return the new total
        return new_total
