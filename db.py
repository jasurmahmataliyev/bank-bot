import sqlite3
import pandas as pd

DB_NAME = 'database.db'

def connect_db():
    """Connect to the SQLite database."""
    return sqlite3.connect(DB_NAME)

def create_tables():
    """Create tables in the SQLite database."""
    conn = connect_db()
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            phone_number TEXT NOT NULL
        )
    ''')
    
    # Create Debtors table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS debtors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT UNIQUE,
            total_debt INTEGER,
            debt INTEGER,
            district TEXT,
            address TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def add_user(username: str, password: str, phone_number: str):
    """Add a new user to the database."""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (username, password, phone_number)
            VALUES (?, ?, ?)
        ''', (username, password, phone_number))
        conn.commit()
        print(f"User '{username}' added successfully.")
    except sqlite3.IntegrityError:
        print(f"Error: The username '{username}' already exists.")
    finally:
        conn.close()

def update_user(username: str, new_password: str = None, new_phone_number: str = None):
    """Update user details."""
    conn = connect_db()
    cursor = conn.cursor()
    if new_password:
        cursor.execute('''
            UPDATE users SET password = ? WHERE username = ?
        ''', (new_password, username))
    if new_phone_number:
        new_phone_number = normalize_phone_number(new_phone_number)
        cursor.execute('''
            UPDATE users SET phone_number = ? WHERE username = ?
        ''', (new_phone_number, username))
    conn.commit()
    conn.close()

def delete_user(username: str):
    """Delete a user from the database."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM users WHERE username = ?
    ''', (username,))
    conn.commit()
    conn.close()

def check_login(username: str, password: str) -> bool:
    """Check if the login credentials are valid."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) FROM users WHERE username = ? AND password = ?
    ''', (username, password))
    result = cursor.fetchone()[0]
    conn.close()
    return result > 0

def check_phone_number(username: str, phone_number: str) -> bool:
    """Check if the phone number matches the one stored for the username."""
    phone_number = normalize_phone_number(phone_number)
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) FROM users WHERE username = ? AND phone_number = ?
    ''', (username, phone_number))
    result = cursor.fetchone()[0]
    conn.close()
    return result > 0

def list_users():
    """List all users in the database."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT username, phone_number FROM users')
    users = cursor.fetchall()
    conn.close()
    return users

def insert_debtors(debtors):
    """Insert debtor data into the database."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.executemany('''
        INSERT INTO debtors (name, phone, total_debt, debt, district, address)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', debtors)
    conn.commit()
    conn.close()

def get_debtors_by_district(district):
    """Retrieve debtors by district from the database."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM debtors WHERE district = ?
    ''', (district,))
    debtors = cursor.fetchall()
    conn.close()
    return debtors

def read_excel_data(file_path):
    """Read data from an Excel file and return it as a DataFrame."""
    try:
        df = pd.read_excel(file_path)
        return df
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None

def normalize_phone_number(phone_number: str) -> str:
    """Normalize phone number by removing spaces and dashes."""
    return phone_number.replace(' ', '').replace('-', '')

if __name__ == '__main__':
    create_tables()
