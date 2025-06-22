-- Create database
CREATE DATABASE IF NOT EXISTS redeem_codes_db;
USE redeem_codes_db;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create redeem_codes table
CREATE TABLE IF NOT EXISTS redeem_codes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    code VARCHAR(100) NOT NULL,
    user_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create copies table to track who copied what
CREATE TABLE IF NOT EXISTS copies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    redeem_code_id INT,
    copied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (redeem_code_id) REFERENCES redeem_codes(id),
    UNIQUE KEY unique_user_code (user_id, redeem_code_id)
);

-- Insert sample data (optional)
INSERT INTO users (name, email, password) VALUES 
('John Doe', 'john@example.com', 'scrypt:32768:8:1$example_hash'),
('Jane Smith', 'jane@example.com', 'scrypt:32768:8:1$example_hash');

INSERT INTO redeem_codes (title, code, user_id) VALUES 
('Google Pay ₹100 Cashback', 'GPAY100ABC', 1),
('Google Pay ₹50 Reward', 'GPAY50XYZ', 2);
