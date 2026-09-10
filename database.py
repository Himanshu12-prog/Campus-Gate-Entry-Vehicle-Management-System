import sqlite3
import os
import sys
from datetime import datetime, timedelta
import random
from werkzeug.security import generate_password_hash, check_password_hash

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'campus_vehicle.db')

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(reset_clean=False):
    if reset_clean and os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print("Existing database removed for fresh clean setup.")

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('guard', 'admin')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create Vehicle Logs table (with gate_name column)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicle_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            vehicle_number TEXT NOT NULL,
            year_branch TEXT NOT NULL,
            purpose TEXT NOT NULL,
            gate_name TEXT DEFAULT 'Main Gate 1',
            entry_time TIMESTAMP NOT NULL,
            exit_time TIMESTAMP,
            status TEXT NOT NULL CHECK(status IN ('INSIDE', 'EXITED')),
            guard_id INTEGER NOT NULL,
            guard_name TEXT NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (guard_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    
    # Ensure Default Admin exists
    cursor.execute("SELECT * FROM users WHERE role = 'admin'")
    admin = cursor.fetchone()
    if not admin:
        admin_pass_hash = generate_password_hash('admin123')
        cursor.execute(
            "INSERT INTO users (name, phone, password_hash, role) VALUES (?, ?, ?, ?)",
            ('Principal Admin', '9999999999', admin_pass_hash, 'admin')
        )
        conn.commit()
        print("Default admin created (Username/Phone: 9999999999 / admin, Password: admin123)")
    
    conn.close()

def get_guard_count():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'guard'")
    row = cursor.fetchone()
    conn.close()
    return row['count'] if row else 0

def register_guard(name, phone, password):
    cleaned_phone = str(phone).strip()
    if not cleaned_phone.isdigit() or len(cleaned_phone) != 10:
        return False, "Phone number must be exactly 10 digits."
    
    current_guards = get_guard_count()
    if current_guards >= 3:
        return False, "Maximum limit of 3 Guard accounts reached. Contact Administrator."
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE phone = ?", (cleaned_phone,))
    if cursor.fetchone():
        conn.close()
        return False, "Phone number is already registered."
    
    pass_hash = generate_password_hash(password)
    cursor.execute(
        "INSERT INTO users (name, phone, password_hash, role) VALUES (?, ?, ?, ?)",
        (name.strip(), cleaned_phone, pass_hash, 'guard')
    )
    conn.commit()
    conn.close()
    return True, "Guard registered successfully! Please login."

def authenticate_user(identifier, password):
    identifier = str(identifier).strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if identifier.lower() == 'admin':
        cursor.execute("SELECT * FROM users WHERE role = 'admin'")
    else:
        cursor.execute("SELECT * FROM users WHERE phone = ?", (identifier,))
        
    user = cursor.fetchone()
    conn.close()
    
    if user and check_password_hash(user['password_hash'], password):
        return dict(user)
    return None

def format_vehicle_number(v_num):
    cleaned = "".join(v_num.upper().split())
    return cleaned

def add_vehicle_entry(student_name, vehicle_number, year_branch, purpose, gate_name, entry_time_str, guard_id, guard_name):
    formatted_v_num = format_vehicle_number(vehicle_number)
    if not formatted_v_num or len(formatted_v_num) < 6:
        return False, "Invalid vehicle number. Format example: MP04AB1234", None

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, entry_time FROM vehicle_logs WHERE vehicle_number = ? AND status = 'INSIDE'",
        (formatted_v_num,)
    )
    active_entry = cursor.fetchone()
    if active_entry:
        conn.close()
        return False, f"Vehicle {formatted_v_num} is ALREADY inside campus (Entered at {active_entry['entry_time']}). Please mark exit first.", None
    
    if entry_time_str:
        try:
            parsed_time = datetime.fromisoformat(entry_time_str).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            parsed_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        parsed_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    cursor.execute('''
        INSERT INTO vehicle_logs 
        (student_name, vehicle_number, year_branch, purpose, gate_name, entry_time, status, guard_id, guard_name)
        VALUES (?, ?, ?, ?, ?, ?, 'INSIDE', ?, ?)
    ''', (student_name.strip(), formatted_v_num, year_branch, purpose, gate_name or 'Main Gate 1', parsed_time, guard_id, guard_name))
    
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return True, f"Vehicle {formatted_v_num} entry logged successfully!", new_id

def mark_vehicle_exit(log_id, exit_time_str=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM vehicle_logs WHERE id = ?", (log_id,))
    log = cursor.fetchone()
    if not log:
        conn.close()
        return False, "Vehicle log entry not found."
    
    if log['status'] == 'EXITED':
        conn.close()
        return False, f"Vehicle {log['vehicle_number']} has already exited at {log['exit_time']}."
    
    if exit_time_str:
        try:
            parsed_exit = datetime.fromisoformat(exit_time_str).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            parsed_exit = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        parsed_exit = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    cursor.execute(
        "UPDATE vehicle_logs SET exit_time = ?, status = 'EXITED' WHERE id = ?",
        (parsed_exit, log_id)
    )
    conn.commit()
    conn.close()
    return True, f"Vehicle {log['vehicle_number']} exit recorded at {parsed_exit}."

def get_guard_dashboard_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    today_date = datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute("SELECT COUNT(*) as count FROM vehicle_logs WHERE date(entry_time) = ?", (today_date,))
    today_total = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM vehicle_logs WHERE status = 'INSIDE'")
    currently_inside = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM vehicle_logs WHERE status = 'EXITED' AND date(exit_time) = ?", (today_date,))
    exited_today = cursor.fetchone()['count']
    
    conn.close()
    return {
        "today_total": today_total,
        "currently_inside": currently_inside,
        "exited_today": exited_today
    }

def calculate_overstay(entry_time_str):
    try:
        entry_dt = datetime.strptime(entry_time_str, "%Y-%m-%d %H:%M:%S")
        duration = datetime.now() - entry_dt
        hours = duration.total_seconds() / 3600.0
        return round(hours, 1), hours >= 4.0
    except Exception:
        return 0, False

def get_active_inside_vehicles():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vehicle_logs WHERE status = 'INSIDE' ORDER BY entry_time DESC")
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for r in rows:
        d = dict(r)
        hours, is_overstay = calculate_overstay(d['entry_time'])
        d['stay_hours'] = hours
        d['is_overstay'] = is_overstay
        result.append(d)
    return result

def get_recent_vehicle_logs(search_query="", status_filter="ALL", days=7):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d 00:00:00")
    query = "SELECT * FROM vehicle_logs WHERE entry_time >= ?"
    params = [cutoff_date]
    
    if status_filter in ['INSIDE', 'EXITED']:
        query += " AND status = ?"
        params.append(status_filter)
        
    if search_query:
        search_param = f"%{search_query.strip()}%"
        query += " AND (vehicle_number LIKE ? OR student_name LIKE ? OR guard_name LIKE ? OR purpose LIKE ?)"
        params.extend([search_param, search_param, search_param, search_param])
        
    query += " ORDER BY entry_time DESC LIMIT 200"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for r in rows:
        d = dict(r)
        if d['status'] == 'INSIDE':
            hours, is_overstay = calculate_overstay(d['entry_time'])
            d['stay_hours'] = hours
            d['is_overstay'] = is_overstay
        else:
            d['stay_hours'] = 0
            d['is_overstay'] = False
        result.append(d)
    return result

def get_single_log(log_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vehicle_logs WHERE id = ?", (log_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_admin_dashboard_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    today_date = datetime.now().strftime("%Y-%m-%d")
    week_start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    cursor.execute("SELECT COUNT(*) as count FROM vehicle_logs WHERE date(entry_time) = ?", (today_date,))
    today_count = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM vehicle_logs WHERE date(entry_time) >= ?", (week_start,))
    weekly_count = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM vehicle_logs WHERE status = 'INSIDE'")
    inside_count = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'guard'")
    guard_count = cursor.fetchone()['count']
    
    conn.close()
    return {
        "today_total": today_count,
        "weekly_total": weekly_count,
        "currently_inside": inside_count,
        "active_guards": guard_count
    }

def get_hourly_peak_data(date_str=None):
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT strftime('%H', entry_time) as hour, COUNT(*) as count
        FROM vehicle_logs
        WHERE date(entry_time) = ?
        GROUP BY hour
        ORDER BY hour ASC
    ''', (date_str,))
    
    raw_data = {row['hour']: row['count'] for row in cursor.fetchall()}
    conn.close()
    
    labels = [f"{h:02d}:00" for h in range(7, 21)]
    data = [raw_data.get(f"{h:02d}", 0) for h in range(7, 21)]
    
    return {"labels": labels, "data": data, "date": date_str}

def get_all_guards():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, phone, created_at FROM users WHERE role = 'guard' ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_filtered_logs(date_start=None, date_end=None, year_branch=None, guard_id=None, search_query=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM vehicle_logs WHERE 1=1"
    params = []
    
    if date_start:
        query += " AND date(entry_time) >= ?"
        params.append(date_start)
    if date_end:
        query += " AND date(entry_time) <= ?"
        params.append(date_end)
    if year_branch and year_branch != "ALL":
        query += " AND year_branch = ?"
        params.append(year_branch)
    if guard_id and str(guard_id) != "ALL":
        query += " AND guard_id = ?"
        params.append(guard_id)
    if search_query:
        search_param = f"%{search_query.strip()}%"
        query += " AND (vehicle_number LIKE ? OR student_name LIKE ? OR purpose LIKE ?)"
        params.extend([search_param, search_param, search_param])
        
    query += " ORDER BY entry_time DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def seed_database():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as count FROM vehicle_logs")
    if cursor.fetchone()['count'] > 0:
        conn.close()
        return

    print("Seeding sample data for Campus Vehicle Management...")
    
    guards_sample = [
        ("Rajesh Kumar (Gate 1)", "9876543210", generate_password_hash("guard123")),
        ("Suresh Patel (Gate 2)", "9876543211", generate_password_hash("guard123")),
        ("Amit Sharma (Gate 1)", "9876543212", generate_password_hash("guard123")),
    ]
    
    guard_ids = []
    for name, phone, pass_hash in guards_sample:
        cursor.execute(
            "INSERT OR IGNORE INTO users (name, phone, password_hash, role) VALUES (?, ?, ?, 'guard')",
            (name, phone, pass_hash)
        )
        cursor.execute("SELECT id, name FROM users WHERE phone = ?", (phone,))
        g_row = cursor.fetchone()
        if g_row:
            guard_ids.append((g_row['id'], g_row['name']))
            
    if not guard_ids:
        conn.close()
        return

    student_names = [
        "Aarav Sharma", "Ananya Verma", "Rohan Mehta", "Priya Singh", "Kabir Gupta",
        "Ishita Joshi", "Devansh Patel", "Sneha Rao", "Aditya Srivastava", "Neha Dixit",
        "Vikram Choudhury", "Pooja Malhotra", "Rishabh Tripathi", "Diya Sengupta", "Yash Rastogi",
        "Dr. Alok Verma (HOD CS)", "Sunil Shinde (Auditor)", "Meera Nambiar (Guest Speaker)", "Karan Deshmukh"
    ]
    
    state_codes = ["MP04", "MP09", "MP20", "DL01", "MH12", "UP32"]
    purposes = ["Class", "Exam", "Library", "Official Work", "Other"]
    branches = ["1st Year", "2nd Year", "3rd Year", "4th Year", "Visitor / Staff"]
    gates = ["Main Gate 1", "North Gate 2", "South Gate 3"]
    
    now = datetime.now()
    logs_to_insert = []
    
    for days_back in range(6, -1, -1):
        day_date = now - timedelta(days=days_back)
        num_entries = random.randint(5, 9)
        
        for _ in range(num_entries):
            hour = random.randint(8, 17)
            minute = random.randint(0, 59)
            entry_dt = day_date.replace(hour=hour, minute=minute, second=0)
            
            s_name = random.choice(student_names)
            v_num = f"{random.choice(state_codes)}{chr(random.randint(65, 90))}{chr(random.randint(65, 90))}{random.randint(1000, 9999)}"
            yr = random.choice(branches)
            purp = random.choice(purposes)
            gt = random.choice(gates)
            g_id, g_name = random.choice(guard_ids)
            
            if days_back > 0:
                stay_minutes = random.randint(45, 360)
                exit_dt = entry_dt + timedelta(minutes=stay_minutes)
                status = 'EXITED'
                exit_str = exit_dt.strftime("%Y-%m-%d %H:%M:%S")
            else:
                if random.random() < 0.6 and entry_dt < (now - timedelta(minutes=30)):
                    stay_minutes = random.randint(30, 180)
                    exit_dt = min(entry_dt + timedelta(minutes=stay_minutes), now)
                    status = 'EXITED'
                    exit_str = exit_dt.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    status = 'INSIDE'
                    exit_str = None
                    
            logs_to_insert.append((
                s_name, v_num, yr, purp, gt,
                entry_dt.strftime("%Y-%m-%d %H:%M:%S"),
                exit_str,
                status, g_id, g_name
            ))
            
    cursor.executemany('''
        INSERT INTO vehicle_logs 
        (student_name, vehicle_number, year_branch, purpose, gate_name, entry_time, exit_time, status, guard_id, guard_name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', logs_to_insert)
    
    conn.commit()
    conn.close()
    print(f"Successfully seeded {len(logs_to_insert)} vehicle logs across 7 days!")

if __name__ == '__main__':
    seed_database()
