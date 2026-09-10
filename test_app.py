import unittest
import os
import json
import database as db
from app import app

class TestCampusVehicleManagementProduction(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test_secret_key'
        self.client = app.test_client()
        db.init_db()

    def test_guard_registration_and_management(self):
        # Invalid phone (less than 10 digits)
        success, msg = db.register_guard("Test Guard", "12345", "password")
        self.assertFalse(success)
        self.assertIn("10 numeric digits", msg)

        # Successful Registration
        phone_num = "9876543999"
        success, msg = db.register_guard("Production Guard 1", phone_num, "pass123")
        self.assertTrue(success)
        self.assertIn("created successfully", msg)

        # Duplicate Phone check
        success_dup, msg_dup = db.register_guard("Duplicate Guard", phone_num, "pass123")
        self.assertFalse(success_dup)
        self.assertIn("already registered", msg_dup)

        # Password Reset
        guard_user = db.authenticate_user(phone_num, "pass123")
        self.assertIsNotNone(guard_user)
        res_pass, msg_pass = db.reset_guard_password(guard_user['id'], "newpass123")
        self.assertTrue(res_pass)
        self.assertIsNotNone(db.authenticate_user(phone_num, "newpass123"))

        # Guard Deletion
        del_res, del_msg = db.delete_guard(guard_user['id'])
        self.assertTrue(del_res)

    def test_vehicle_entry_and_exit(self):
        # Register a guard
        db.register_guard("Duty Guard Alpha", "9876543111", "guard123")
        guard_user = db.authenticate_user("9876543111", "guard123")

        # Format vehicle plate check
        formatted = db.format_vehicle_number(" mp 04  ab 8888 ")
        self.assertEqual(formatted, "MP04AB8888")

        # Add Entry
        success, msg, new_id = db.add_vehicle_entry(
            student_name="Production Student",
            vehicle_number="MP04AB8888",
            year_branch="1st Year",
            purpose="Class",
            gate_name="Main Gate 1",
            entry_time_str=None,
            guard_id=guard_user['id'],
            guard_name=guard_user['name']
        )
        self.assertTrue(success)
        self.assertIsNotNone(new_id)

        # Duplicate Entry Check
        dup_success, dup_msg, _ = db.add_vehicle_entry(
            student_name="Production Student",
            vehicle_number="mp04ab8888",
            year_branch="1st Year",
            purpose="Class",
            gate_name="Main Gate 1",
            entry_time_str=None,
            guard_id=guard_user['id'],
            guard_name=guard_user['name']
        )
        self.assertFalse(dup_success)
        self.assertIn("ALREADY inside campus", dup_msg)

        # Mark Exit
        exit_success, exit_msg = db.mark_vehicle_exit(new_id)
        self.assertTrue(exit_success)

    def test_admin_authentication_and_reports(self):
        # Admin auth
        admin_user = db.authenticate_user("admin", "admin123")
        self.assertIsNotNone(admin_user)

        with self.client as c:
            c.post('/login', data={'action': 'login', 'identifier': 'admin', 'password': 'admin123'})

            # Chart API
            chart_res = c.get('/api/admin/hourly_chart')
            self.assertEqual(chart_res.status_code, 200)

            # Export CSV
            csv_res = c.get('/admin/export/csv')
            self.assertEqual(csv_res.status_code, 200)

            # Export Excel
            excel_res = c.get('/admin/export/excel')
            self.assertEqual(excel_res.status_code, 200)

if __name__ == '__main__':
    unittest.main()
