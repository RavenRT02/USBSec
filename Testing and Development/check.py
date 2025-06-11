import sqlite3

conn = sqlite3.connect("user_data.db")
cursor = conn.cursor()

# Check what's stored
cursor.execute("SELECT * FROM users")  # Replace 'users' with your table name
print(cursor.fetchall())

# Delete all users (or filter by username/email)
cursor.execute("DELETE FROM users")  # or e.g., WHERE username='admin'
conn.commit()
conn.close()

print("✅ User(s) deleted.")
