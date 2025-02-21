# gpay-reward-card

## 📌 Project Overview
The GPay Reward Application is a web-based system that allows users to log in, register, and redeem rewards using a unique redeem code system. The platform ensures secure user authentication, tracks redeemed codes, and automatically deletes expired rewards to maintain a clean database.

## 🚀 Features
- User Authentication (Login, Register, Logout)
- Secure Password Storage (Using werkzeug.security)
- Redeem Code Management
- Auto Deletion of Expired Items (Using a background thread)
- Session-Based Access Control
- Database Transactions with Retry Mechanism
## 🛠️ Tech Stack
- Backend: Flask (Python)
- Database: MySQL
- Frontend: HTML, CSS, JavaScript
- Security: Hashed Passwords (werkzeug.security)
- Concurrency: Background Thread for Cleanup
## 📂 Project Structure
```
/gpay-reward-app
│── /templates         # HTML Templates (Login, Register, Dashboard)
│── /static            # CSS & JavaScript files
│── app.py             # Main Flask application
│── requirements.txt   # Required dependencies
│── README.md          # Project Documentation
│── database.sql       # Database Schema
```
## 🏗️ Setup Instructions
  - 🔹 Prerequisites
  - Install Python (>=3.8)
  - Install MySQL Server
  - Install pip
## Database Configuration

- Create two MySQL databases: login_details and redeemcode_database
- Run the database.sql file to create necessary tables

## Security Measures
- Hashed Passwords (No plaintext storage)
- Session-Based Authentication
- Retry Mechanism for Database Transactions
## 📌 Future Enhancements
- Implement OTP-based authentication
- Add reward expiration notifications
- Develop a mobile-friendly UI
## 💡 Contributing
Feel free to fork this repository, make changes, and submit a pull request.





