# Campus Gate Entry & Vehicle Management System

A web application designed for campus security gate operations and executive administration, built with **Python Flask**, **SQLite Database**, **Tailwind CSS**, and **Chart.js**.

## 🌟 Key Features

### 1. Guard Gate Dashboard
- **Top Metrics Cards**: Today's Total Vehicle Entries, Currently Inside Campus (Exit Pending), and Vehicles Exited Today.
- **New Vehicle Entry Form**:
  - Student / Visitor Name input.
  - **Auto-Uppercase Vehicle Number**: Automatically formats input string (`mp04ab1234` -> `MP04AB1234`).
  - Category / Year selection (1st, 2nd, 3rd, 4th Year, Visitor / Staff).
  - Purpose of visit selection (Class, Exam, Library, Official Work, Other).
  - Entry Time auto-captured timestamp with edit override option.
  - Auto-tagged logged-in duty guard name & ID.
  - Duplicate entry prevention if vehicle is already inside campus.
- **Exit Management**: One-click **"Mark Exit"** button for active vehicles currently inside campus.
- **Last 7 Days History Log**: Searchable and filterable data table showing date, vehicle plate, name, purpose, entry time, exit time, and duty guard.

### 2. Principal / Admin Executive Dashboard
- **Executive Analytics Cards**: Today's traffic, 7-day total volume, currently active vehicles on campus, and guard registration status.
- **Peak Entry Hours Interactive Bar Chart**: Powered by Chart.js displaying hourly traffic distribution between 07:00 and 20:00.
- **Filter Panel**: Filter logs by From/To Date, Category/Branch, Duty Guard, or Vehicle Plate search.
- **Data Exporting**: One-click **Download CSV** and **Download Excel (.xlsx)** buttons.

### 3. Role-Based Authentication & Guard Registration
- **Guard Sign-Up & Login**: Guard registration using 10-digit mobile phone number & password. Supports up to **3 separate guard accounts**.
- **Admin Login**: Pre-configured admin access (`admin` / `admin123`) using password hashing.

### 4. Design & Theme
- **Strict Light Mode Only**: Built using Tailwind CSS (`#F8FAFC` background, `#334155` text, `#2563EB` blue accent, `#0D9488` teal accent).
- **Mobile & Tablet Responsive**: Touch-friendly inputs and responsive layout for guard tablets or smartphones.

---

## 📁 File Structure

```
Campus vehicle management/
├── app.py                   # Main Flask Backend Server
├── database.py              # SQLite Database Schema, CRUD Operations, & 7-Day Seed Generator
├── campus_vehicle.db        # SQLite Database File
├── requirements.txt         # Dependencies
├── test_app.py              # Automated Unit Test Suite
├── templates/
│   ├── base.html            # Shared Light-Mode Layout (Tailwind CSS, FontAwesome)
│   ├── login.html           # Login & Guard Registration Modal with Demo Quick-Fill Buttons
│   ├── guard_dashboard.html # Guard Dashboard Page
│   └── admin_dashboard.html # Principal / Admin Dashboard Page
└── README.md                # Project Documentation
```

---

## 🚀 Quick Start Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```

Open your browser and navigate to: **`http://127.0.0.1:5000`**

### 3. Pre-Configured Demo Credentials

| Role | Username / Phone | Password | Access |
| :--- | :--- | :--- | :--- |
| **Principal Admin** | `admin` (or `9999999999`) | `admin123` | Executive Stats, Peak Hours Chart, Reports, CSV & Excel Download |
| **Duty Guard 1** | `9876543210` | `guard123` | Guard Dashboard, Entry Form, Mark Exit, 7-Day Logs |
| **Duty Guard 2** | `9876543211` | `guard123` | Guard Gate Entry & Exit Management |
| **Duty Guard 3** | `9876543212` | `guard123` | Guard Gate Entry & Exit Management |

---

## 🧪 Running Unit Tests

Run the included automated test suite to verify database integrity, phone/vehicle validations, guard registration limits, and export APIs:

```bash
python test_app.py
```
