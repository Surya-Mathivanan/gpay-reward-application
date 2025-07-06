# gpay-reward-application

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

## Images:
### LoginPage
![Image](https://github.com/user-attachments/assets/3cdf1947-c983-497f-a55d-81a5440605ec)
### RegisterPage
![Image](https://github.com/user-attachments/assets/771d5513-d5df-41ca-a1e2-fdf811ee7f18)
### HomePage
<img width="1366" height="765" alt="Image" src="https://github.com/user-attachments/assets/669f72d1-43e5-476a-8cd7-cd06759ff1bb" />
### AccountPage
<img width="1366" height="765" alt="Image" src="[https://github.com/user-attachments/assets/1728571d-de53-41c9-b757-4c6d1e706944](https://github-production-user-asset-6210df.s3.amazonaws.com/153536787/457637871-95e30b15-08cc-4bbc-8176-506cc81bd8bf.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAVCODYLSA53PQK4ZA%2F20250706%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20250706T141721Z&X-Amz-Expires=300&X-Amz-Signature=34b0541f6be4a1d1f51eb0d6f6289e2f52ae393d0cb96df7b761f38b2accb55c&X-Amz-SignedHeaders=host)" />
### CodeAddingPage
<img width="1366" height="765" alt="Image" src="https://github.com/user-attachments/assets/1728571d-de53-41c9-b757-4c6d1e706944" />
### DashBoardPage
<img width="1366" height="765" alt="Image" src="https://github.com/user-attachments/assets/e27510bb-3cc5-45c1-a724-d4cc6f0e15fe" />


### ArchivePage
![Image](https://github.com/user-attachments/assets/587f4268-8f2b-4f48-9d70-abdfb59ee9af)
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
```
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your-password',
    'database': 'redeem_codes_db'
}
```
## Database Tables
- users:
   - id, name, email, password, created_at
- redeem_codes:
   - id, title, code, user_id, created_at
- copies:
   - id, user_id, redeem_code_id, copied_at
- user_suspensions:
   - id, user_id, reason, suspended_at, suspended_until, is_active
- misuse_logs:
   - user_id, action_type, details, created_at

## Security Measures
- Passwords stored as hashes (no plain-text)

- Session-based access control

- SQL injection protection via parameterized queries

- Misuse tracking with account suspension

## 📌 Future Enhancements
- Implement OTP-based authentication
- Add reward expiration notifications
- Develop a mobile-friendly UI

## 💡 Contributing
Feel free to fork this repository, make changes, and submit a pull request.



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
