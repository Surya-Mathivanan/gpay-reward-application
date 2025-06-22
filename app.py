from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Surya2003@@',
    'database': 'redeem_codes_db'
}

def get_db_connection():
    """Get database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def init_database():
    """Initialize database and create tables"""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        
        # Create database if not exists
        cursor.execute("CREATE DATABASE IF NOT EXISTS redeem_codes_db")
        cursor.execute("USE redeem_codes_db")
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create redeem_codes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS redeem_codes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                code VARCHAR(100) NOT NULL,
                user_id INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Create copies table to track who copied what
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS copies (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                redeem_code_id INT,
                copied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (redeem_code_id) REFERENCES redeem_codes(id),
                UNIQUE KEY unique_user_code (user_id, redeem_code_id)
            )
        """)
        
        connection.commit()
        cursor.close()
        connection.close()
        print("Database initialized successfully!")

@app.route('/')
def index():
    """Redirect to login page"""
    if 'user_id' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id, name, password FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            cursor.close()
            connection.close()
            
            if user and check_password_hash(user[2], password):
                session['user_id'] = user[0]
                session['user_name'] = user[1]
                session['user_email'] = email
                flash('Login successful!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid email or password. Please register if you don\'t have an account.', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                flash('Email already registered. Please login.', 'error')
                cursor.close()
                connection.close()
                return redirect(url_for('login'))
            
            # Create new user
            hashed_password = generate_password_hash(password)
            cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                         (name, email, hashed_password))
            connection.commit()
            
            # Get the new user ID
            user_id = cursor.lastrowid
            cursor.close()
            connection.close()
            
            # Log in the user
            session['user_id'] = user_id
            session['user_name'] = name
            session['user_email'] = email
            flash('Registration successful!', 'success')
            return redirect(url_for('home'))
    
    return render_template('register.html')

@app.route('/home')
def home():
    """Home page displaying all redeem codes"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        
        # Get all redeem codes with copy status for current user, ordered by copy count (ascending)
        # Exclude codes older than 7 days or with 5 or more copies
        cursor.execute("""
            SELECT rc.id, rc.title, rc.code, rc.created_at, u.name,
                   COUNT(c.id) as total_copies,
                   MAX(CASE WHEN c.user_id = %s THEN 1 ELSE 0 END) as user_copied
            FROM redeem_codes rc
            JOIN users u ON rc.user_id = u.id
            LEFT JOIN copies c ON rc.id = c.redeem_code_id
            WHERE rc.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            GROUP BY rc.id, rc.title, rc.code, rc.created_at, u.name
            HAVING total_copies < 5
            ORDER BY total_copies ASC, rc.created_at DESC
        """, (session['user_id'],))
        
        redeem_codes = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return render_template('home.html', redeem_codes=redeem_codes)
    
    return render_template('home.html', redeem_codes=[])

@app.route('/account')
def account():
    """Account page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('account.html')

@app.route('/add_code', methods=['GET', 'POST'])
def add_code():
    """Add redeem code page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        code = request.form['code']
        
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO redeem_codes (title, code, user_id) VALUES (%s, %s, %s)",
                         (title, code, session['user_id']))
            connection.commit()
            cursor.close()
            connection.close()
            
            flash('Redeem code added successfully!', 'success')
            return redirect(url_for('home'))
    
    return render_template('add_code.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard page showing user statistics"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        
        # Get user's copy statistics
        cursor.execute("SELECT COUNT(*) FROM copies WHERE user_id = %s", (session['user_id'],))
        total_copies = cursor.fetchone()[0]
        
        # Get user's added codes count
        cursor.execute("SELECT COUNT(*) FROM redeem_codes WHERE user_id = %s", (session['user_id'],))
        added_codes = cursor.fetchone()[0]
        
        cursor.close()
        connection.close()
        
        return render_template('dashboard.html', total_copies=total_copies, added_codes=added_codes)
    
    return render_template('dashboard.html', total_copies=0, added_codes=0)

@app.route('/archive')
def archive():
    """Archive page showing expired and exhausted codes"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        
        # Get archived codes (older than 7 days OR 5 or more copies)
        cursor.execute("""
            SELECT rc.id, rc.title, rc.code, rc.created_at, u.name,
                   COUNT(c.id) as total_copies,
                   MAX(CASE WHEN c.user_id = %s THEN 1 ELSE 0 END) as user_copied,
                   CASE 
                       WHEN rc.created_at < DATE_SUB(NOW(), INTERVAL 7 DAY) THEN 'Expired'
                       WHEN COUNT(c.id) >= 5 THEN 'Exhausted'
                       ELSE 'Active'
                   END as status
            FROM redeem_codes rc
            JOIN users u ON rc.user_id = u.id
            LEFT JOIN copies c ON rc.id = c.redeem_code_id
            WHERE rc.created_at < DATE_SUB(NOW(), INTERVAL 7 DAY) 
               OR rc.id IN (
                   SELECT redeem_code_id 
                   FROM copies 
                   GROUP BY redeem_code_id 
                   HAVING COUNT(*) >= 5
               )
            GROUP BY rc.id, rc.title, rc.code, rc.created_at, u.name
            ORDER BY rc.created_at DESC
        """, (session['user_id'],))
        
        archived_codes = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return render_template('archive.html', archived_codes=archived_codes)
    
    return render_template('archive.html', archived_codes=[])

@app.route('/copy_code', methods=['POST'])
def copy_code():
    """Handle code copying"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    redeem_code_id = request.json.get('redeem_code_id')
    
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        
        # First check if the code has already reached the limit
        cursor.execute("SELECT COUNT(*) FROM copies WHERE redeem_code_id = %s", (redeem_code_id,))
        current_copies = cursor.fetchone()[0]

        if current_copies >= 5:
            cursor.close()
            connection.close()
            return jsonify({'success': False, 'message': 'Copy limit reached'})
        
        try:
            # Insert copy record (will fail if already exists due to unique constraint)
            cursor.execute("INSERT INTO copies (user_id, redeem_code_id) VALUES (%s, %s)",
                         (session['user_id'], redeem_code_id))
            connection.commit()
            
            # Get updated copy count
            cursor.execute("SELECT COUNT(*) FROM copies WHERE redeem_code_id = %s", (redeem_code_id,))
            copy_count = cursor.fetchone()[0]
            
            cursor.close()
            connection.close()
            
            return jsonify({'success': True, 'copy_count': copy_count})
            
        except mysql.connector.IntegrityError:
            # User already copied this code
            cursor.close()
            connection.close()
            return jsonify({'success': False, 'message': 'Already copied'})
    
    return jsonify({'success': False, 'message': 'Database error'})

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_database()
    app.run(debug=True)
