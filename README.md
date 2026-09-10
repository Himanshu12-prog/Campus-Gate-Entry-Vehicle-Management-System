# Campus Gate Entry & Vehicle Management System 🚗🛡️
> A modern, mobile-responsive, production-ready Web Application for Campus Security Gate Control & Principal Traffic Analytics.

![Tech Stack](https://img.shields.io/badge/Tech%20Stack-Python%20%7C%20Flask%20%7C%20Tailwind%20CSS%20%7C%20Chart.js-blue)
![Database](https://img.shields.io/badge/Database-SQLite-emerald)
![Deployment](https://img.shields.io/badge/Deployment-Render%20%7C%20Docker-purple)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🌟 Key Features

### 👮 Gate Guard Operations
- **Account Registration**: Guards register securely using their 10-digit mobile phone number and password.
- **New Vehicle Entry Form**:
  - Auto-uppercase vehicle plate formatting (`mp04ab1234` $\rightarrow$ `MP04AB1234`).
  - Category selector (1st, 2nd, 3rd, 4th Year Student, Visitor / Staff).
  - Multi-Gate location selector (Main Gate 1, North Gate 2, South Gate 3).
  - Purpose of visit selection (Class, Exam, Library, Official Work, Other).
  - Duplicate active vehicle entry prevention.
- **Printable Visitor Gate Pass**: One-click **Print Pass** button generating a printable gate slip token with barcode and vehicle details.
- **Overstay Warnings**: Highlights vehicles inside campus for more than 4 hours with an **Overstay Alert Badge**.
- **Quick Exit Action**: One-click **Mark Exit** button auto-stamping exit time.

### 🎓 Principal & Executive Administration
- **Admin Registration & Auth**: Dedicated Admin registration and login portal.
- **Real-Time Campus Analytics**: Live vehicle volume, weekly traffic counts, active on-campus count, and duty guards list.
- **Peak Entry Hours Chart**: Interactive bar chart powered by **Chart.js** displaying hourly traffic (07:00 to 20:00).
- **Guard Management**: Admin can view registered guards, delete guard accounts, or reset guard passwords.
- **Centralized Reports & Filters**: Filter logs by From/To Date, Category, Gate, Duty Guard, or Vehicle Plate search.
- **One-Click Exports**: Download filtered or full logs as **CSV** or formatted **Excel (.xlsx)** spreadsheets.

---

## 🏗️ Tech Stack

- **Backend**: Python 3.11+, Flask Web Framework, Werkzeug Security Hashing.
- **Database**: SQLite3 (Clean Production Schema with automatic migration handlers).
- **Frontend & Styling**: HTML5, Vanilla JavaScript, Tailwind CSS (Strict Light Theme `#F8FAFC`), FontAwesome 6 icons.
- **Data Visualization**: Chart.js.
- **Report Exports**: Pandas, OpenPyXL.
- **Production Server**: Gunicorn (Linux/Cloud) / Waitress (Windows).

---

## 🚀 Quick Start & Local Setup

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/Himanshu12-prog/Campus-Gate-Entry-Vehicle-Management-System.git
cd Campus-Gate-Entry-Vehicle-Management-System
pip install -r requirements.txt
```

### 2. Run Locally
- **Windows 1-Click**: Double-click `start_app.bat`
- **Manual Command**:
```bash
python app.py
```
Open your browser at **`http://127.0.0.1:5000`**

---

## 🌐 Deploying to Render.com (100% Free Public Web Hosting)

1. Fork or push this repository to your GitHub account.
2. Go to [Render.com](https://render.com) and create a **New Web Service**.
3. Connect your GitHub repository.
4. Set the following settings:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
5. Click **Create Web Service**. Your app will be live in ~2 minutes with a free HTTPS URL!

---

## 📁 Repository File Structure

```
Campus-Gate-Entry-Vehicle-Management-System/
├── app.py                   # Main Flask Backend Application & Endpoints
├── database.py              # SQLite Schema, CRUD operations, & Migrations
├── wsgi.py                  # Production WSGI Server Entrypoint (Waitress/Gunicorn)
├── reset_db.py              # Production Database Reset Utility
├── requirements.txt         # Dependencies
├── Procfile                 # Cloud Hosting Start Command for Render / Railway
├── Dockerfile               # Container configuration for Docker deployment
├── docker-compose.yml       # Docker Compose setup
├── .env                     # Production environment variables
├── .gitignore               # Ignored cache & temporary files
├── templates/
│   ├── base.html            # Shared Light-Mode Layout (Tailwind CSS, Navbar, Footer)
│   ├── login.html           # Unified Sign In & Account Creation (Guard & Admin)
│   ├── guard_dashboard.html # Guard Gate Dashboard
│   ├── admin_dashboard.html # Principal / Admin Dashboard
│   └── gate_slip.html       # Printable Visitor Gate Pass Token
└── README.md                # Project Documentation
```

---

## 📄 License
Licensed under the [MIT License](LICENSE). Developed for Campus Security & Vehicle Management.
