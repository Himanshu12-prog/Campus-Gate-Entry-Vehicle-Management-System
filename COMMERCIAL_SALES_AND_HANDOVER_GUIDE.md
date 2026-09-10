# Commercial Sales & Client Handover Guide
### Campus Gate Entry & Vehicle Management System

This document is your complete commercial handbook for pitching, demoing, selling, and deploying this system to colleges, universities, institutions, or corporate campuses.

---

## 💰 Suggested Selling Price & Business Model

| Service Package | Target Client | Recommended Price (INR) | Recommended Price (USD) | Included Services |
| :--- | :--- | :--- | :--- | :--- |
| **Basic License** | Small Schools & Colleges (1 Gate) | ₹15,000 – ₹25,000 | $200 – $350 | Full source code, SQLite database, 1-click installer |
| **Standard Commercial** | Medium Universities (2–3 Gates) | ₹35,000 – ₹60,000 | $450 – $800 | Full system, multi-gate support, printable pass slip, Excel reports, local Wi-Fi setup |
| **Enterprise + Maintenance** | Large Campus & Tech Parks | ₹75,000 + ₹10,000/yr | $1,000 + $150/yr | Custom college logo white-labeling, annual database backups, security maintenance |

---

## 🎯 High-Value Selling Points (Pitch to College Principal & Management)

1. **Strict Gate Security & Overstay Alerts**:
   - Live monitoring of vehicles currently inside campus.
   - **Automatic Overstay Badge (>4 hours)** alerts security if a vehicle stays longer than expected.
2. **Instant Gate Pass / Visitor Token Printing**:
   - Guards can generate and print a clean Gate Pass Token with vehicle plate number, visitor name, and security barcode.
3. **Automated Upper-case Plate Validation**:
   - Prevents typo entries (auto converts `mp04ab1234` to `MP04AB1234`). Prevents duplicate active entries.
4. **Executive Dashboard for Principal**:
   - Peak Entry Hours bar chart (Chart.js) showing traffic trends.
   - One-click **Download CSV** and **Download Excel (.xlsx)** reports for official university audit compliance.
5. **No Internet Needed / Runs on Local Wi-Fi**:
   - Works on the college's internal local network/Wi-Fi router. Guards on tablets/smartphones at Main Gate, North Gate, and South Gate can log entries simultaneously!

---

## 🎬 How to Showcase & Demo to a Client (Sales Pitch Walkthrough)

1. **Step 1: Load Sample Demo Dataset**:
   - Log in as Admin (`admin` / `admin123`).
   - Click the **"Seed Demo Data"** button at the top.
   - This populates 45+ realistic vehicle logs across the last 7 days, active inside vehicles, and peak hour graphs.

2. **Step 2: Show the Executive Admin Dashboard**:
   - Show the Principal the **Peak Entry Hours Bar Chart**, today's volume, and the **Excel Export** download feature.

3. **Step 3: Show the Guard Gate Mobile Dashboard**:
   - Log in as Duty Guard (`9876543210` / `guard123`).
   - Type a vehicle number in lowercase (e.g. `mp04ab9999`) and show the auto-uppercase feature.
   - Click **"Register Vehicle Gate Entry"**.
   - Click **"Pass"** to open and print the printable Visitor Slip token.
   - Click **"Mark Exit"** to demonstrate one-click exit timestamping.

---

## 📦 How to Prepare & Handover for a Paid Client (Clean Setup)

When a college buys the software from you, follow these 3 simple steps to give them a 100% clean, fresh installation:

### Step 1: Wipe Demo Data & Initialize Clean Production Database
Run the included reset script in terminal:
```bash
python reset_db.py
```
*Or log in as Admin and click the **"Clean DB (Sell Mode)"** button.*

This wipes all sample demo records and creates a brand new database with only the Master Admin account.

### Step 2: Configure College Local Network Access (Multiple Mobile/Tablet Guards)
To allow guards to use their tablets/phones on the college Wi-Fi:
1. Connect the host computer to the college Wi-Fi router.
2. Find the host computer's Local IP address:
   - On Windows: Run `ipconfig` (e.g. `192.168.1.150`).
3. Guards can now open `http://192.168.1.150:5000` on any phone, tablet, or gate laptop connected to the same Wi-Fi!

### Step 3: Deliver the 1-Click Launcher
Provide the client with the `start_app.bat` file. The client only needs to double-click `start_app.bat` to launch the server!

---

## 📁 Delivery Package Files Checklist

Ensure the following files are in your zip folder when handing over to your buyer:

- `app.py`
- `database.py`
- `reset_db.py`
- `requirements.txt`
- `start_app.bat`
- `templates/` (base.html, login.html, guard_dashboard.html, admin_dashboard.html, gate_slip.html)
- `README.md`
