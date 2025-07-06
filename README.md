# gpay-reward-application

## 📌 Project Overview
The GPay Reward Application is a web-based system that allows users to log in, register, and redeem rewards using a unique redeem code system. The platform ensures secure user authentication, tracks redeemed codes, and automatically deletes expired rewards to maintain a clean database.

## 🚀 Features

- ✅ **User Authentication (Login, Register, Logout)**  
  Enables users to securely create accounts, log in to access features, and log out to protect session data. Ensures only verified users can access the platform.

- 🔐 **Secure Password Storage (using `werkzeug.security`)**  
  Protects user credentials by storing passwords as cryptographic hashes instead of plain text, enhancing security against data breaches.

- 🔄 **Redeem Code Management (Add, View, Copy)**  
  Allows users to add new redeem codes with titles, view available codes from others, and copy them within defined limits.

- 🧠 **Intelligent Misuse Detection System**  
  Prevents abuse and ensures fair usage:
  - Detects rapid copy attempts that resemble bot behavior
  - Automatically suspends accounts until the end of the day if misuse is detected
  - Logs all misuse attempts for transparency and future analysis

- 📊 **Dashboard to Track User Activity**  
  Gives users insight into their usage patterns by showing:
  - Number of codes they’ve added
  - Number of codes they’ve copied

- 🕵️ **Copy Limit Restriction**  
  Maintains code fairness:
  - A maximum of 5 users can copy a code
  - Each user can copy a specific code only once

- 📁 **Archive Page for Code History**  
  Displays codes that are no longer active due to:
  - Expiration (older than 7 days)
  - Exhaustion (already copied 5 times)  
  Helps users track old and unavailable codes along with their status: **Active**, **Expired**, or **Exhausted**.

- 👁️‍🗨️ **Misuse Logs & Suspension History Tracking**  
  Administrators or the system can monitor suspicious behavior, with logs showing when users were suspended and the reasons behind it.

- 🔐 **Session-Based Access Control**  
  Ensures secure access to user-specific pages and operations. Only logged-in users can view or perform actions on sensitive pages like add, copy, or view dashboard.

- 🧹 **Automatic Table Initialization on First Run**  
  Simplifies deployment by creating all necessary tables when the app runs for the first time. No need for manual SQL execution during setup.


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
<img width="1366" height="765" alt="Image" src="https://github.com/user-attachments/assets/773c48bf-0e32-4933-b05a-45b4d38ccfff" />
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
