<<<<<<< HEAD
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





=======
# Google Pay Redeem Code Distributor

A Flask web application for managing and distributing Google Pay redeem codes with user authentication and tracking.

## Features

- **User Authentication**: Registration and login system
- **Code Management**: Add, view, and copy redeem codes
- **Copy Tracking**: Track how many times each code has been copied
- **User Dashboard**: View personal statistics
- **Responsive Design**: Works on desktop and mobile devices

## Setup Instructions

### Prerequisites

- Python 3.7+
- MySQL Server
- pip (Python package installer)

### Installation

1. **Clone or download the project files**

2. **Install Python dependencies**:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

3. **Set up MySQL Database**:
   - Install MySQL Server if not already installed
   - Create a database user with appropriate permissions
   - Update the database configuration in `app.py`:
     ```python
     DB_CONFIG = {
         'host': 'localhost',
         'user': 'your_mysql_username',
         'password': 'your_mysql_password',
         'database': 'redeem_codes_db'
     }
     \`\`\`

4. **Run the application**:
   \`\`\`bash
   python app.py
   \`\`\`

5. **Access the application**:
   - Open your web browser
   - Navigate to `http://localhost:5000`
   - The application will automatically create the necessary database tables

## Usage

### First Time Setup

1. **Registration**: Create a new account with your name, email, and password
2. **Login**: Use your credentials to log in
3. **Add Codes**: Start adding redeem codes with titles and codes
4. **Copy Codes**: Browse and copy codes added by other users

### Features Overview

- **Home Page**: View all available redeem codes in card format
- **Account Page**: View your profile information and logout
- **Add Code Page**: Add new redeem codes to share with others
- **Dashboard**: View your activity statistics
- **Copy Tracking**: Each code can only be copied once per user

## Database Schema

### Users Table
- `id`: Primary key
- `name`: User's full name
- `email`: User's email (unique)
- `password`: Hashed password
- `created_at`: Registration timestamp

### Redeem Codes Table
- `id`: Primary key
- `title`: Code title/description
- `code`: The actual redeem code
- `user_id`: Foreign key to users table
- `created_at`: Creation timestamp

### Copies Table
- `id`: Primary key
- `user_id`: Foreign key to users table
- `redeem_code_id`: Foreign key to redeem_codes table
- `copied_at`: Copy timestamp
- Unique constraint on (user_id, redeem_code_id)

## Security Features

- Password hashing using Werkzeug
- Session management
- SQL injection prevention using parameterized queries
- Unique constraints to prevent duplicate copies

## Customization

You can customize the application by:

- Modifying the CSS styles in `templates/base.html`
- Changing the color scheme and layout
- Adding additional fields to the forms
- Implementing additional features like code categories

## Troubleshooting

### Common Issues

1. **Database Connection Error**: 
   - Verify MySQL is running
   - Check database credentials in `app.py`
   - Ensure the database user has proper permissions

2. **Module Import Error**:
   - Install missing dependencies: `pip install -r requirements.txt`

3. **Port Already in Use**:
   - Change the port in `app.py`: `app.run(debug=True, port=5001)`

## Contributing

Feel free to fork this project and submit pull requests for improvements.

## License

This project is open source and available under the MIT License.
>>>>>>> cd45fd5 (version 2)
