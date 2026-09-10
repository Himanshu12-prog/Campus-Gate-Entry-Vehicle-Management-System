import os
import io
from functools import wraps
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect, url_for, 
    session, flash, jsonify, send_file
)
import pandas as pd
from dotenv import load_dotenv

import database as db

# Load environment configuration
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'campus_gate_security_prod_secret_key_2026_x89q')

# Initialize database
db.init_db()

# Authentication & Access Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in to access the system.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash("Please sign in to proceed.", "warning")
                return redirect(url_for('login'))
            if session.get('user_role') != required_role:
                flash(f"Unauthorized access. Requires {required_role.capitalize()} privileges.", "danger")
                if session.get('user_role') == 'guard':
                    return redirect(url_for('guard_dashboard'))
                else:
                    return redirect(url_for('admin_dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('user_role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('guard_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
        
    guard_count = db.get_guard_count()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'signup':
            name = request.form.get('name', '').strip()
            phone = request.form.get('phone', '').strip()
            password = request.form.get('password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()
            
            if not name or not phone or not password:
                flash("All fields are required for guard registration.", "danger")
                return render_template('login.html', guard_count=guard_count, active_tab='signup')
                
            if password != confirm_password:
                flash("Passwords do not match.", "danger")
                return render_template('login.html', guard_count=guard_count, active_tab='signup')
                
            success, message = db.register_guard(name, phone, password)
            if success:
                flash(message, "success")
                return render_template('login.html', guard_count=db.get_guard_count(), active_tab='login')
            else:
                flash(message, "danger")
                return render_template('login.html', guard_count=guard_count, active_tab='signup')
                
        elif action == 'login':
            identifier = request.form.get('identifier', '').strip()
            password = request.form.get('password', '').strip()
            
            if not identifier or not password:
                flash("Please provide phone/username and password.", "danger")
                return render_template('login.html', guard_count=guard_count, active_tab='login')
                
            user = db.authenticate_user(identifier, password)
            if user:
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                session['user_phone'] = user['phone']
                session['user_role'] = user['role']
                flash(f"Welcome back, {user['name']}!", "success")
                
                if user['role'] == 'admin':
                    return redirect(url_for('admin_dashboard'))
                return redirect(url_for('guard_dashboard'))
            else:
                flash("Invalid phone number / username or password.", "danger")
                return render_template('login.html', guard_count=guard_count, active_tab='login')
                
    return render_template('login.html', guard_count=guard_count, active_tab='login')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been signed out safely.", "info")
    return redirect(url_for('login'))

# GUARD DASHBOARD ROUTES
@app.route('/guard/dashboard')
@login_required
@role_required('guard')
def guard_dashboard():
    stats = db.get_guard_dashboard_stats()
    inside_vehicles = db.get_active_inside_vehicles()
    
    search_q = request.args.get('search', '').strip()
    status_f = request.args.get('status', 'ALL').strip()
    
    recent_logs = db.get_recent_vehicle_logs(search_query=search_q, status_filter=status_f, days=7)
    now_iso = datetime.now().strftime("%Y-%m-%dT%H:%M")
    
    return render_template(
        'guard_dashboard.html',
        stats=stats,
        inside_vehicles=inside_vehicles,
        recent_logs=recent_logs,
        search_q=search_q,
        status_f=status_f,
        now_iso=now_iso
    )

@app.route('/api/entry', methods=['POST'])
@login_required
@role_required('guard')
def add_entry():
    student_name = request.form.get('student_name', '').strip()
    vehicle_number = request.form.get('vehicle_number', '').strip()
    year_branch = request.form.get('year_branch', '').strip()
    purpose = request.form.get('purpose', '').strip()
    gate_name = request.form.get('gate_name', 'Main Gate 1').strip()
    entry_time = request.form.get('entry_time', '').strip()
    
    if not student_name or not vehicle_number or not year_branch or not purpose:
        flash("Please fill in all vehicle entry details.", "danger")
        return redirect(url_for('guard_dashboard'))
        
    success, message, new_id = db.add_vehicle_entry(
        student_name=student_name,
        vehicle_number=vehicle_number,
        year_branch=year_branch,
        purpose=purpose,
        gate_name=gate_name,
        entry_time_str=entry_time,
        guard_id=session['user_id'],
        guard_name=session['user_name']
    )
    
    if success:
        flash(message, "success")
    else:
        flash(message, "danger")
        
    return redirect(url_for('guard_dashboard'))

@app.route('/api/exit/<int:log_id>', methods=['POST'])
@login_required
@role_required('guard')
def mark_exit(log_id):
    success, message = db.mark_vehicle_exit(log_id)
    if success:
        flash(message, "success")
    else:
        flash(message, "danger")
    return redirect(url_for('guard_dashboard'))

@app.route('/guard/print_slip/<int:log_id>')
@login_required
def print_slip(log_id):
    log = db.get_single_log(log_id)
    if not log:
        flash("Log entry not found.", "danger")
        return redirect(url_for('index'))
    return render_template('gate_slip.html', log=log)

# ADMIN / PRINCIPAL DASHBOARD ROUTES
@app.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    stats = db.get_admin_dashboard_stats()
    guards = db.get_all_guards()
    inside_vehicles = db.get_active_inside_vehicles()
    
    date_start = request.args.get('date_start', '')
    date_end = request.args.get('date_end', '')
    year_branch = request.args.get('year_branch', 'ALL')
    guard_id = request.args.get('guard_id', 'ALL')
    search_q = request.args.get('search', '').strip()
    
    logs = db.get_filtered_logs(
        date_start=date_start,
        date_end=date_end,
        year_branch=year_branch,
        guard_id=guard_id,
        search_query=search_q
    )
    
    return render_template(
        'admin_dashboard.html',
        stats=stats,
        guards=guards,
        inside_vehicles=inside_vehicles,
        logs=logs,
        date_start=date_start,
        date_end=date_end,
        year_branch=year_branch,
        guard_id=guard_id,
        search_q=search_q
    )

@app.route('/api/admin/hourly_chart')
@login_required
@role_required('admin')
def hourly_chart_api():
    date_str = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))
    chart_data = db.get_hourly_peak_data(date_str)
    return jsonify(chart_data)

@app.route('/admin/reset_data', methods=['POST'])
@login_required
@role_required('admin')
def admin_reset_data():
    mode = request.form.get('mode', 'clean')
    if mode == 'seed':
        db.seed_database()
        flash("Sample demo dataset seeded successfully!", "success")
    else:
        db.init_db(reset_clean=True)
        flash("Database reset to 100% CLEAN production state!", "warning")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/export/csv')
@login_required
@role_required('admin')
def export_csv():
    date_start = request.args.get('date_start', '')
    date_end = request.args.get('date_end', '')
    year_branch = request.args.get('year_branch', 'ALL')
    guard_id = request.args.get('guard_id', 'ALL')
    search_q = request.args.get('search', '').strip()
    
    logs = db.get_filtered_logs(date_start, date_end, year_branch, guard_id, search_q)
    
    df_data = []
    for l in logs:
        df_data.append({
            'Log ID': l['id'],
            'Date': l['entry_time'].split(' ')[0] if l['entry_time'] else '',
            'Vehicle Number': l['vehicle_number'],
            'Student / Visitor Name': l['student_name'],
            'Year / Branch': l['year_branch'],
            'Purpose of Visit': l['purpose'],
            'Gate Location': l['gate_name'] if 'gate_name' in l.keys() else 'Main Gate 1',
            'Entry Timestamp': l['entry_time'],
            'Exit Timestamp': l['exit_time'] if l['exit_time'] else 'INSIDE CAMPUS',
            'Status': l['status'],
            'Duty Guard': l['guard_name']
        })
        
    df = pd.DataFrame(df_data)
    output = io.BytesIO()
    df.to_csv(output, index=False, encoding='utf-8')
    output.seek(0)
    
    filename = f"Campus_Vehicle_Logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

@app.route('/admin/export/excel')
@login_required
@role_required('admin')
def export_excel():
    date_start = request.args.get('date_start', '')
    date_end = request.args.get('date_end', '')
    year_branch = request.args.get('year_branch', 'ALL')
    guard_id = request.args.get('guard_id', 'ALL')
    search_q = request.args.get('search', '').strip()
    
    logs = db.get_filtered_logs(date_start, date_end, year_branch, guard_id, search_q)
    
    df_data = []
    for l in logs:
        df_data.append({
            'Log ID': l['id'],
            'Date': l['entry_time'].split(' ')[0] if l['entry_time'] else '',
            'Vehicle Number': l['vehicle_number'],
            'Student / Visitor Name': l['student_name'],
            'Year / Branch': l['year_branch'],
            'Purpose of Visit': l['purpose'],
            'Gate Location': l['gate_name'] if 'gate_name' in l.keys() else 'Main Gate 1',
            'Entry Timestamp': l['entry_time'],
            'Exit Timestamp': l['exit_time'] if l['exit_time'] else 'INSIDE CAMPUS',
            'Status': l['status'],
            'Duty Guard': l['guard_name']
        })
        
    df = pd.DataFrame(df_data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Campus Vehicle Logs', index=False)
    output.seek(0)
    
    filename = f"Campus_Vehicle_Logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    print("Starting Campus Gate Entry & Vehicle Management System...")
    print(f"Local Server running on http://{host}:{port}")
    app.run(host=host, port=port, debug=True)
