from user_management import UserManager, User
from random import randint

manager = UserManager()

# Helper function to print test results
def print_result(test_no, passed, details = ""):
    if passed:
        status = "PASSED" 
    else:
        status = "FAILED"
        
    print(f"Test {test_no}: {status} - {details}")

# Test 1.1: Register new user
i = randint(1,100000)
un = 'newuser' + str(i)
result = manager.register_user(un, "Password123!")
passed = result is True
manager.cursor.execute("SELECT username FROM users WHERE username = ?", (un,))
exists = manager.cursor.fetchone() is not None
print_result("1.1", passed and exists, "Register new user")

# Test 1.2: Register existing user
result = manager.register_user("test", "Password123!")
print_result("1.2", result is False, "Register existing user 'test'")

# Test 1.3: Register with empty username
try:
    manager.register_user("", "Password123!")
    print_result("1.3", False, "Empty username should raise TypeError")
except TypeError:
    print_result("1.3", True, "Empty username raises TypeError")

# Test 1.4: Login with correct credentials
user = manager.login("test", "password")
passed = (user is not None and isinstance(user, User) and user.username == "test" and user.level == 5)
print_result("1.4", passed, "Login with correct credentials")

# Test 1.5: Login with incorrect password
user = manager.login("test", "wrongpass")
print_result("1.5", user is None, "Login with incorrect password")

# Test 1.6: Login with non-existent user
user = manager.login("nonuser", "password")
print_result("1.6", user is None, "Login with non-existent user")

# Test 1.7: Update flight minutes (positive)
manager.cursor.execute("SELECT flight_minutes FROM users WHERE user_id = ?", (1,))
initial = manager.cursor.fetchone()[0]
new_total = manager.update_flight_minutes(1, 5.0)
print_result("1.7", new_total == initial + 5.0, "Update flight minutes +5.0")

# Test 1.8: Update flight minutes (negative)
manager.cursor.execute("UPDATE users SET flight_minutes = ? WHERE user_id = ?", (10.0, 1))
manager.conn.commit()
new_total = manager.update_flight_minutes(1, -5.0)
print_result("1.8", new_total == 5.0, "Update flight minutes -5.0")

# Test 1.9: Update level to 3
new_level = manager.update_level(1, 3)
manager.cursor.execute("SELECT level FROM users WHERE user_id = ?", (1,))
db_level = manager.cursor.fetchone()[0]
print_result("1.9", new_level == 3 and db_level == 3, "Update level to 3")

# Test 1.10: Update level above max
new_level = manager.update_level(1, 11)
manager.cursor.execute("SELECT level FROM users WHERE user_id = ?", (1,))
db_level = manager.cursor.fetchone()[0]
print_result("1.10", new_level == 10 and db_level == 10, "Update level to 11 (capped at 10)")

# Test 1.11: Update level below min
new_level = manager.update_level(1, 0)
manager.cursor.execute("SELECT level FROM users WHERE user_id = ?", (1,))
db_level = manager.cursor.fetchone()[0]
print_result("1.11", new_level == 1 and db_level == 1, "Update level to 0 (floored at 1)")

# Test 1.12: Update level with non-integer
try:
    manager.update_level(1, "invalid")
    print_result("1.12", False, "Non-integer level should raise TypeError")
except TypeError:
    print_result("1.12", True, "Non-integer level raises TypeError")

# Reset level
new_level = manager.update_level(1, 5)

# Clean up
manager.conn.close()
    
input()

