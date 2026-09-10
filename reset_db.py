import os
import sys
import sqlite3
from werkzeug.security import generate_password_hash
import database as db

def reset_to_clean_production_database(admin_phone="admin", admin_password="admin123", admin_name="Principal Admin"):
    print("=" * 60)
    print("   CAMPUS GATE ENTRY & VEHICLE MANAGEMENT SYSTEM")
    print("       Production Database Reset & Setup Utility")
    print("=" * 60)
    
    db_file = db.DB_FILE
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"[OK] Deleted existing database: {db_file}")
        
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute('''
        CREATE TABLE users (
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
        CREATE TABLE vehicle_logs (
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
    
    # Create Master Admin Account
    pass_hash = generate_password_hash(admin_password)
    cursor.execute(
        "INSERT INTO users (name, phone, password_hash, role) VALUES (?, ?, ?, 'admin')",
        (admin_name, admin_phone, pass_hash)
    )
    
    conn.commit()
    conn.close()
    
    print("\n[OK] Fresh Production Database initialized successfully!")
    print(f"[i] Master Admin Created:")
    print(f"    - Name     : {admin_name}")
    print(f"    - Phone/ID : {admin_phone}")
    print(f"    - Password : {admin_password}")
    print(f"    - Role     : Admin (Full Privileges)")
    print("\n[i] The system is now 100% clean and ready for real gate entries.")
    print("=" * 60)

if __name__ == '__main__':
    reset_to_clean_production_database()
