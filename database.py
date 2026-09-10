import sqlite3
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

# Allow persistent database path override via environment variable for Cloud/Render hosting
DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'campus_vehicle.db')
DB_FILE = os.getenv('DATABASE_PATH', DEFAULT_DB_PATH)

def get_db_connection():
    # Ensure directory exists if custom path provided
    db_dir = os.path.dirname(DB_FILE)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(clean_logs_only=False):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create Users table (Stores Guards and Admin accounts permanently)
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
    
    # Create Vehicle Logs table
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
    
    # Schema Migration Check for gate_name
    cursor.execute("PRAGMA table_info(vehicle_logs)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'gate_name' not in columns:
        try:
            cursor.execute("ALTER TABLE vehicle_logs ADD COLUMN gate_name TEXT DEFAULT 'Main Gate 1'")
            conn.commit()
        except Exception:
            pass
            
    conn.commit()
    
    # Ensure Master Admin Account exists if no admin registered yet
    cursor.execute("SELECT * FROM users WHERE role = 'admin'")
    admin = cursor.fetchone()
    if not admin:
        admin_pass_hash = generate_password_hash('admin123')
        cursor.execute(
            "INSERT INTO users (name, phone, password_hash, role) VALUES (?, ?, ?, 'admin')",
            ('Principal Admin', 'admin', admin_pass_hash)
        )
        conn.commit()
        print("[✓] Initialized Master Admin Account (Username: admin, Password: admin123)")
    
    conn.close()

def get_guard_count():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'guard'")
    row = cursor.fetchone()
    conn.close()
    return row['count'] if row else 0

def register_user(name, phone_or_username, password, role='guard'):
    identifier = str(phone_or_username).strip()
    clean_name = str(name).strip()
    
    if not clean_name or not identifier or not password:
        return False, "All fields are required for registration."
        
    if role not in ['guard', 'admin']:
        return False, "Invalid account role selected."

    # If Guard, enforce 10-digit mobile number format
    if role == 'guard':
        cleaned_digits = "".join(filter(str.isdigit, identifier))
        if len(cleaned_digits) != 10:
            return False, "Guard mobile number must be exactly 10 numeric digits."
        identifier = cleaned_digits

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if phone/username already registered (case insensitive check)
    cursor.execute("SELECT id, role FROM users WHERE LOWER(phone) = LOWER(?)", (identifier,))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        existing_role = "Admin" if existing['role'] == 'admin' else "Guard"
        return False, f"Account identifier '{identifier}' is already registered as a {existing_role}."
    
    pass_hash = generate_password_hash(password)
    cursor.execute(
        "INSERT INTO users (name, phone, password_hash, role) VALUES (?, ?, ?, ?)",
        (clean_name, identifier, pass_hash, role)
    )
    conn.commit()
    conn.close()
    
    role_label = "Principal Admin" if role == 'admin' else "Gate Guard"
    return True, f"{role_label} account '{clean_name}' ({identifier}) created successfully! You can now log in."

def register_guard(name, phone, password):
    return register_user(name, phone, password, role='guard')

def authenticate_user(identifier, password):
    if not identifier or not password:
        return None
        
    clean_id = str(identifier).strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check case-insensitive match for phone / username
    cursor.execute("SELECT * FROM users WHERE LOWER(phone) = LOWER(?)", (clean_id,))
    user = cursor.fetchone()
    
    # Fallback for default 'admin' string if typed
    if not user and clean_id.lower() == 'admin':
        cursor.execute("SELECT * FROM users WHERE role = 'admin' LIMIT 1")
        user = cursor.fetchone()
        
    conn.close()
    
    if user and check_password_hash(user['password_hash'], password):
        return dict(user)
    return None

def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return False, "User account not found."
        
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True, f"Account '{user['name']}' removed successfully."

def delete_guard(guard_id):
    return delete_user(guard_id)

def reset_user_password(user_id, new_password):
    if not new_password or len(new_password) < 4:
        return False, "Password must be at least 4 characters."
        
    pass_hash = generate_password_hash(new_password)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (pass_hash, user_id))
    conn.commit()
    conn.close()
    return True, "Password updated successfully."

def reset_guard_password(guard_id, new_password):
    return reset_user_password(guard_id, new_password)

def format_vehicle_number(v_num):
    cleaned = "".join(v_num.upper().split())
    return cleaned

def add_vehicle_entry(student_name, vehicle_number, year_branch, purpose, gate_name, entry_time_str, guard_id, guard_name):
    formatted_v_num = format_vehicle_number(vehicle_number)
    if not formatted_v_num or len(formatted_v_num) < 6:
        return False, "Invalid vehicle number format. Example: MP04AB1234", None

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, entry_time FROM vehicle_logs WHERE vehicle_number = ? AND status = 'INSIDE'",
        (formatted_v_num,)
    )
    active_entry = cursor.fetchone()
    if active_entry:
        conn.close()
        return False, f"Vehicle {formatted_v_num} is ALREADY inside campus (Entered at {active_entry['entry_time']}). Mark exit first.", None
    
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
    return True, f"Vehicle {formatted_v_num} entry recorded successfully!", new_id

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
        return False, f"Vehicle {log['vehicle_number']} has already exited."
    
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

def get_recent_vehicle_logs(search_query="", status_filter="ALL", days=30):
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
        
    query += " ORDER BY entry_time DESC LIMIT 500"
    
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

def wipe_all_vehicle_logs():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vehicle_logs")
    conn.commit()
    conn.close()
    return True, "All vehicle logs cleared successfully."

if __name__ == '__main__':
    init_db()
