from sqlite3 import connect

conn = connect("users.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()  # Fetch all rows from the executed query

for row in rows:
    print(row)  # Print each row in the table
    print()


conn.close()  # Always close the connection when done

print()
print()
print()
print()

conn = connect("planes.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM planes")
rows = cursor.fetchall()  # Fetch all rows from the executed query

for row in rows:
    print(row)  # Print each row in the table
    print()


conn.close()  # Always close the connection when done







input()
