from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Database configuration using environment variables
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Surya2003@@',
    'database': 'redeem_codes_db'
}



def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def init_database():
    """Create tables inside already selected database"""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()

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
        
        # Create copies table
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
        
        # Create user_suspensions table for tracking misuse
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_suspensions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                reason VARCHAR(255) NOT NULL,
                suspended_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                suspended_until TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Create misuse_logs table for detailed tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS misuse_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                action_type VARCHAR(50) NOT NULL,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        connection.commit()
        cursor.close()
        connection.close()
        print("Database initialized successfully!")

def check_user_suspension(user_id):
    """Check if user is currently suspended"""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT suspended_until, reason FROM user_suspensions 
            WHERE user_id = %s AND is_active = TRUE AND suspended_until > NOW()
            ORDER BY suspended_at DESC LIMIT 1
        """, (user_id,))
        suspension = cursor.fetchone()
        cursor.close()
        connection.close()
        return suspension
    return None

def log_misuse_activity(user_id, action_type, details):
    """Log misuse activity for monitoring"""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO misuse_logs (user_id, action_type, details) 
            VALUES (%s, %s, %s)
        """, (user_id, action_type, details))
        connection.commit()
        cursor.close()
        connection.close()

def check_rapid_copying_pattern(user_id):
    """Check if user has been copying codes too rapidly"""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        
        # Get last 5 copies by this user in the last 2 minutes
        cursor.execute("""
            SELECT copied_at FROM copies 
            WHERE user_id = %s AND copied_at >= DATE_SUB(NOW(), INTERVAL 2 MINUTE)
            ORDER BY copied_at DESC LIMIT 5
        """, (user_id,))
        
        recent_copies = cursor.fetchall()
        cursor.close()
        connection.close()
        
        if len(recent_copies) >= 3:
            # Check if any 3 consecutive copies were within 20 seconds of each other
            rapid_sequences = 0
            
            for i in range(len(recent_copies) - 2):
                time1 = recent_copies[i][0]
                time2 = recent_copies[i + 1][0]
                time3 = recent_copies[i + 2][0]
                
                # Check if all 3 copies happened within 60 seconds total
                if (time1 - time3).total_seconds() <= 60:
                    # Check if any two consecutive copies were within 20 seconds
                    if ((time1 - time2).total_seconds() <= 20 or 
                        (time2 - time3).total_seconds() <= 20):
                        rapid_sequences += 1
            
            if rapid_sequences >= 1:
                return True, len(recent_copies)
        
        return False, len(recent_copies) if recent_copies else 0
    
    return False, 0

def suspend_user(user_id, reason):
    """Suspend user until end of day"""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        
        # Calculate suspension until end of day
        tomorrow = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Deactivate any existing suspensions
        cursor.execute("""
            UPDATE user_suspensions SET is_active = FALSE 
            WHERE user_id = %s AND is_active = TRUE
        """, (user_id,))
        
        # Add new suspension
        cursor.execute("""
            INSERT INTO user_suspensions (user_id, reason, suspended_until) 
            VALUES (%s, %s, %s)
        """, (user_id, reason, tomorrow))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        # Log the suspension
        log_misuse_activity(user_id, 'SUSPENDED', f'Reason: {reason}')
        
        return True
    return False

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
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
                # Check if user is suspended
                suspension = check_user_suspension(user[0])
                if suspension:
                    suspended_until = suspension[0]
                    reason = suspension[1]
                    flash(f'Your account is suspended until {suspended_until.strftime("%Y-%m-%d %H:%M:%S")}. Reason: {reason}', 'error')
                    return render_template('login.html')
                
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
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                flash('Email already registered. Please login.', 'error')
                cursor.close()
                connection.close()
                return redirect(url_for('login'))
            
            hashed_password = generate_password_hash(password)
            cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
            connection.commit()
            user_id = cursor.lastrowid
            cursor.close()
            connection.close()
            
            session['user_id'] = user_id
            session['user_name'] = name
            session['user_email'] = email
            flash('Registration successful!', 'success')
            return redirect(url_for('home'))
    
    return render_template('register.html')

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Check if user is suspended
    suspension = check_user_suspension(session['user_id'])
    if suspension:
        session.clear()
        flash(f'Your account has been suspended for misuse. Suspension ends: {suspension[0].strftime("%Y-%m-%d %H:%M:%S")}', 'error')
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
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
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Check if user is suspended
    suspension = check_user_suspension(session['user_id'])
    if suspension:
        session.clear()
        flash(f'Your account has been suspended for misuse. Suspension ends: {suspension[0].strftime("%Y-%m-%d %H:%M:%S")}', 'error')
        return redirect(url_for('login'))
    
    return render_template('account.html')

@app.route('/add_code', methods=['GET', 'POST'])
def add_code():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Check if user is suspended
    suspension = check_user_suspension(session['user_id'])
    if suspension:
        session.clear()
        flash(f'Your account has been suspended for misuse. Suspension ends: {suspension[0].strftime("%Y-%m-%d %H:%M:%S")}', 'error')
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
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Check if user is suspended
    suspension = check_user_suspension(session['user_id'])
    if suspension:
        session.clear()
        flash(f'Your account has been suspended for misuse. Suspension ends: {suspension[0].strftime("%Y-%m-%d %H:%M:%S")}', 'error')
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM copies WHERE user_id = %s", (session['user_id'],))
        total_copies = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM redeem_codes WHERE user_id = %s", (session['user_id'],))
        added_codes = cursor.fetchone()[0]
        cursor.close()
        connection.close()
        return render_template('dashboard.html', total_copies=total_copies, added_codes=added_codes)
    
    return render_template('dashboard.html', total_copies=0, added_codes=0)

@app.route('/archive')
def archive():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Check if user is suspended
    suspension = check_user_suspension(session['user_id'])
    if suspension:
        session.clear()
        flash(f'Your account has been suspended for misuse. Suspension ends: {suspension[0].strftime("%Y-%m-%d %H:%M:%S")}', 'error')
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
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
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    user_id = session['user_id']
    
    # Check if user is suspended
    suspension = check_user_suspension(user_id)
    if suspension:
        session.clear()
        return jsonify({
            'success': False, 
            'message': 'Account suspended for misuse',
            'redirect': '/login'
        })
    
    redeem_code_id = request.json.get('redeem_code_id')
    
    # Check for rapid copying pattern BEFORE processing the copy
    is_rapid, recent_count = check_rapid_copying_pattern(user_id)
    
    if is_rapid:
        # Log the misuse attempt
        log_misuse_activity(user_id, 'RAPID_COPYING_DETECTED', 
                          f'Attempted to copy code {redeem_code_id} with {recent_count} recent copies')
        
        # Suspend the user
        suspend_user(user_id, 'Rapid copying detected - potential misuse of platform')
        
        # Clear session to force logout
        session.clear()
        
        return jsonify({
            'success': False,
            'message': 'You have misused this platform by copying codes too rapidly. Your account has been temporarily suspended for the rest of the day.',
            'suspended': True,
            'redirect': '/login'
        })
    
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM copies WHERE redeem_code_id = %s", (redeem_code_id,))
        current_copies = cursor.fetchone()[0]

        if current_copies >= 5:
            cursor.close()
            connection.close()
            return jsonify({'success': False, 'message': 'Copy limit reached'})
        
        try:
            cursor.execute("INSERT INTO copies (user_id, redeem_code_id) VALUES (%s, %s)",
                         (user_id, redeem_code_id))
            connection.commit()
            cursor.execute("SELECT COUNT(*) FROM copies WHERE redeem_code_id = %s", (redeem_code_id,))
            copy_count = cursor.fetchone()[0]
            cursor.close()
            connection.close()
            
            # Log successful copy
            log_misuse_activity(user_id, 'CODE_COPIED', f'Successfully copied code {redeem_code_id}')
            
            return jsonify({'success': True, 'copy_count': copy_count})
        except mysql.connector.IntegrityError:
            cursor.close()
            connection.close()
            return jsonify({'success': False, 'message': 'Already copied'})
    
    return jsonify({'success': False, 'message': 'Database error'})

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_database()
    app.run(debug=True)
