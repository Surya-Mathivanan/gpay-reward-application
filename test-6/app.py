from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from datetime import datetime, timedelta
import os
import threading
import time
import re
from flask import request, jsonify

app = Flask(__name__)

# Secret key for session management
app.secret_key = os.urandom(24)

# Database configurations
login_db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'login_details'
}

redeem_db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'redeemcode_database'
}

# Function to get database connection
def get_redeem_db_connection():
    return mysql.connector.connect(**redeem_db_config)

# Function to retry a transaction in case of lock wait timeout
def retry_transaction(cursor, query, params, retries=3, delay=5):
    for attempt in range(retries):
        try:
            cursor.execute(query, params)
            return True
        except mysql.connector.errors.DatabaseError as err:
            if "1205" in str(err):  # Lock wait timeout error code
                print(f"Lock wait timeout exceeded. Retrying {attempt + 1}/{retries}...")
                time.sleep(delay)
            else:
                raise  # Reraise the error if it's not a timeout error
    return False

# ROUTES

# Login Page
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']

        # Connect to the login database
        conn = mysql.connector.connect(**login_db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and check_password_hash(user['password'], password):  # Check hashed password
            session['loggedin'] = True
            session['userid'] = user['userid']
            session['name'] = user['name']
            return redirect(url_for('manage_items'))
        else:
            message = 'Invalid email or password!'

    return render_template('login.html', message=message)

# Logout
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('name', None)
    return redirect(url_for('login'))

# Registration Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Validate inputs
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9@#$%^&+=]{8,}', password):
            message = 'Password must be at least 8 characters long and contain letters, numbers, and special characters.'
        else:
            # Hash the password
            hashed_password = generate_password_hash(password)

            # Connect to the login database
            conn = mysql.connector.connect(**login_db_config)
            cursor = conn.cursor()

            try:
                # Check if the email already exists
                cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
                existing_user = cursor.fetchone()

                if existing_user:
                    message = 'This account already exists. Please log in.'
                else:
                    # Insert new user into the `user` table
                    cursor.execute(
                        "INSERT INTO user (name, email, password) VALUES (%s, %s, %s)",
                        (name, email, hashed_password)
                    )
                    conn.commit()
                    message = 'Registration successful! You can now log in.'
                    return redirect(url_for('login'))
            finally:
                cursor.close()
                conn.close()

    return render_template('register.html', message=message)

# Manage Items (Redeem Code Functionality)
@app.route('/manage')
def manage_items():
    if 'loggedin' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    db = get_redeem_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM items 
        ORDER BY 
            CASE WHEN temp_count <= 5 THEN 0 ELSE 1 END, 
            temp_count ASC
    """)
    items = cursor.fetchall()

    # Check if the user has already redeemed the item
    cursor.execute("""
        SELECT item_id FROM user_redemptions WHERE user_id = %s
    """, (session['userid'],))
    redeemed_items = {row['item_id'] for row in cursor.fetchall()}
    db.close()

    for item in items:
        created_at = item['created_at']
        deletion_time = created_at + timedelta(days=10)
        remaining_time = deletion_time - datetime.now()
        item['remaining_time'] = max(remaining_time, timedelta(0))

        # Add a flag to indicate whether the user has already redeemed the item
        item['redeemed'] = item['id'] in redeemed_items

    return render_template('index.html', items=items)

# Add Item
@app.route('/add', methods=['POST'])
def add_item():
    if 'loggedin' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    name = request.form['name']
    redeem_code = request.form['redeem_code']
    created_at = datetime.now()

    db = get_redeem_db_connection()
    cursor = db.cursor()

    try:
        retry_transaction(cursor, "INSERT INTO items (name, redeem_code, created_at) VALUES (%s, %s, %s)", (name, redeem_code, created_at))
        db.commit()
    except mysql.connector.Error as err:
        db.rollback()
        print(f"Error: {err}")
    finally:
        db.close()

    return redirect(url_for('manage_items'))

# Copy Code (Redeem Code)
@app.route('/copy/<int:id>', methods=['POST'])
def copy_code(id):
    if 'loggedin' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    db = get_redeem_db_connection()
    cursor = db.cursor()

    # Check if the user has already redeemed the item
    cursor.execute("""
        SELECT * FROM user_redemptions WHERE user_id = %s AND item_id = %s
    """, (session['userid'], id))
    redeemed = cursor.fetchone()

    if redeemed:
        db.close()
        return jsonify({"success": False, "message": "You have already redeemed this item!"}), 400  # Prevent further redemption

    # If the item has not been redeemed, proceed with redemption
    cursor.execute("UPDATE items SET temp_count = temp_count + 1 WHERE id = %s", (id,))
    cursor.execute("""
        INSERT INTO user_redemptions (user_id, item_id, redeemed_at)
        VALUES (%s, %s, NOW())
    """, (session['userid'], id))
    db.commit()
    db.close()

    return jsonify({"success": True}), 200


# Cleanup old items in the database (runs as a background thread)
def delete_old_items():
    while True:
        try:
            db = get_redeem_db_connection()
            cursor = db.cursor()

            threshold_date = datetime.now() - timedelta(days=7)
            cursor.execute("DELETE FROM items WHERE created_at < %s", (threshold_date,))

            cursor.execute("DELETE FROM items WHERE temp_count > 10")

            db.commit()
            db.close()
        except Exception as e:
            print(f"Error while deleting old items: {e}")
        time.sleep(24 * 60 * 60)  # Cleanup every 24 hours

threading.Thread(target=delete_old_items, daemon=True).start()

if __name__ == "__main__":
    app.run(debug=True)
