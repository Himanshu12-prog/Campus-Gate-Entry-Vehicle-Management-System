import unittest
import os
import json
import database as db
from app import app

class TestCampusVehicleManagement(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test_secret_key'
        self.client = app.test_client()
        db.seed_database()

    def test_database_initialization_and_seed(self):
        stats = db.get_guard_dashboard_stats()
        self.assertIn('today_total', stats)
        self.assertIn('currently_inside', stats)
        self.assertIn('exited_today', stats)

        admin_stats = db.get_admin_dashboard_stats()
        self.assertGreater(admin_stats['weekly_total'], 0)
        self.assertGreaterEqual(admin_stats['active_guards'], 1)

    def test_guard_registration_validation(self):
        # Invalid phone (less than 10 digits)
        success, msg = db.register_guard("Test Guard", "12345", "password")
        self.assertFalse(success)
        self.assertIn("10 digits", msg)

        # Check guard count
        cnt = db.get_guard_count()
        if cnt < 3:
            # Register up to 3
            success, msg = db.register_guard("New Guard", "9876543999", "pass123")
            self.assertTrue(success)

        # Attempt exceeding limit (4th guard)
        # Ensure count is 3
        while db.get_guard_count() < 3:
            phone_num = f"987654300{db.get_guard_count()}"
            db.register_guard("Temp Guard", phone_num, "pass123")

        success, msg = db.register_guard("Excess Guard", "9988776655", "pass123")
        self.assertFalse(success)
        self.assertIn("Maximum limit of 3 Guard accounts reached", msg)

    def test_vehicle_entry_formatting_and_duplicate_check(self):
        # Format check
        formatted = db.format_vehicle_number(" mp 04  ab 9999 ")
        self.assertEqual(formatted, "MP04AB9999")

        # Add entry
        success, msg, new_id = db.add_vehicle_entry(
            student_name="Test Student",
            vehicle_number="MP04XYZ100",
            year_branch="3rd Year",
            purpose="Exam",
            entry_time_str=None,
            guard_id=1,
            guard_name="Rajesh Guard"
        )
        self.assertTrue(success)
        self.assertIsNotNone(new_id)

        # Duplicate entry check (trying to enter same vehicle while inside)
        success_dup, msg_dup, _ = db.add_vehicle_entry(
            student_name="Test Student",
            vehicle_number="mp04xyz100",  # uppercase check
            year_branch="3rd Year",
            purpose="Exam",
            entry_time_str=None,
            guard_id=1,
            guard_name="Rajesh Guard"
        )
        self.assertFalse(success_dup)
        self.assertIn("ALREADY inside campus", msg_dup)

        # Mark Exit
        exit_success, exit_msg = db.mark_vehicle_exit(new_id)
        self.assertTrue(exit_success)

    def test_authentication_and_routes(self):
        # Test Admin Auth
        admin_user = db.authenticate_user("admin", "admin123")
        self.assertIsNotNone(admin_user)
        self.assertEqual(admin_user['role'], 'admin')

        # Test Guard Auth
        guard_user = db.authenticate_user("9876543210", "guard123")
        self.assertIsNotNone(guard_user)
        self.assertEqual(guard_user['role'], 'guard')

        # Test Login Session Endpoint
        res = self.client.post('/login', data={'action': 'login', 'identifier': 'admin', 'password': 'admin123'})
        self.assertEqual(res.status_code, 302)

    def test_admin_chart_api_and_exports(self):
        # Login as Admin
        with self.client as c:
            c.post('/login', data={'action': 'login', 'identifier': 'admin', 'password': 'admin123'})

            # Hourly chart API
            chart_res = c.get('/api/admin/hourly_chart')
            self.assertEqual(chart_res.status_code, 200)
            json_data = chart_res.get_json()
            self.assertIn('labels', json_data)
            self.assertIn('data', json_data)

            # Export CSV
            csv_res = c.get('/admin/export/csv')
            self.assertEqual(csv_res.status_code, 200)
            self.assertEqual(csv_res.mimetype, 'text/csv')

            # Export Excel
            excel_res = c.get('/admin/export/excel')
            self.assertEqual(excel_res.status_code, 200)
            self.assertEqual(excel_res.mimetype, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

if __name__ == '__main__':
    unittest.main()
