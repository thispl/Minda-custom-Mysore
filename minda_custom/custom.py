import frappe,os
import random
from datetime import datetime
from frappe.utils.data import today, add_days
from dateutil.relativedelta import relativedelta
from datetime import timedelta

@frappe.whitelist()
def get_check():
    checkin = frappe.db.sql(
        """select * from `tabEmployee Checkin` where skip_auto_attendance = 0 order by time""", as_dict=1)
    if checkin:
        for c in checkin:
            att = attendance(c.device_id,c.time,c.log_date,c.log_time,c.user_id,c.device_log_id,c.log_type)
            if att == "ok":
                frappe.db.set_value("Employee Checkin",c.name, "skip_auto_attendance", "1")
        return "ok"

@frappe.whitelist()
def attendance(device_id,l_date,log_date,log_time,user_id,device_log_id,log_type):
    min_time = datetime.strptime('07:00', '%H:%M')
    a_min_time = datetime.strptime('05:00', '%H:%M')
    a_max_time = datetime.strptime('07:30', '%H:%M')
    b_min_time = datetime.strptime('13:30', '%H:%M')
    b_max_time = datetime.strptime('15:30', '%H:%M')
    c_min_time = datetime.strptime('21:00', '%H:%M')
    c_max_time = datetime.strptime('23:59', '%H:%M')
    g_min_time = datetime.strptime('07:30', '%H:%M')
    g_max_time = datetime.strptime('10:30', '%H:%M')
    userid = user_id
    stgid = device_id
    time_with_date = l_date
    employee = frappe.db.get_value("Employee", {
        "name": userid, "status": "Active"})
    if employee:
        date = log_date
        time_m = log_time
        # time_with_date_f = time_with_date
        # doc = frappe.get_doc("Employee",employee)
        # if doc.employment_type != 'Contract':
        #     userid = user_id
        #     biotime = log_time
        #     stgid = device_id

        prev_day = False
        g_time = datetime.strptime(str(log_time), '%H:%M:%S')
        if g_time < min_time:
            date = add_days(date, -1)
            attendance_id = frappe.db.get_value("Attendance", {
                "employee": employee, "attendance_date": date})
            prev_day = True
        else:
            attendance_id = frappe.db.get_value("Attendance", {
                "employee": employee, "attendance_date": date})
        if attendance_id:
            attendance = frappe.get_doc(
                "Attendance", attendance_id)
            attendance.out_date = l_date
            attendance.out_time = l_date
            attendance.db_update()
            frappe.db.commit()
            frappe.response.type = "text"
            return "ok"
        else:
            attendance = frappe.new_doc("Attendance")
            ctime = datetime.strftime(l_date, '%Y-%m-%d %H:%M:%S')
            in_time = datetime.strptime(ctime, '%Y-%m-%d %H:%M:%S').time()
            intime = datetime.strptime(str(in_time), '%H:%M:%S')
            # print type(intime)
            # print intime
            late_entry = 0
            if intime >= a_min_time and intime <= a_max_time:
                shift = "A"
            elif intime >= b_min_time and intime <= b_max_time:
                shift = "B"
            elif intime >= c_min_time and intime <= c_max_time:
                shift = "C"
            elif intime >= g_min_time and intime <= g_max_time:
                shift = "G"
            else:
                shift = ""
                late_entry = 1
            attendance.update({
                "employee": employee,
                # "employee_name": doc.employee_name,
                # "contractor": doc.contractor,
                # "employment_type": doc.employment_type,
                # "line": doc.line,
                "attendance_date": date,
                "status": "Present",
                "shift": shift,
                "late_entry": late_entry,
                # "service_tag_id": stgid,
                "in_time": l_date,
                # "out_time": "00:00:00",
                # "company": doc.company
            })
            attendance.save(ignore_permissions=True)
            attendance.submit()
            frappe.db.commit()
            frappe.response.type = "text"
            return "ok"
    else:
        # employee = user_id
        # date = log_date
        # ure_id = frappe.db.get_value("Unregistered Employee", {
        #     "employee": employee, "attendance_date": date})
        # if ure_id:
        #     attendance = frappe.get_doc(
        #         "Unregistered Employee", ure_id)
        #     out_time = log_time
        #     times = [str(out_time), str(attendance.in_time)]
        #     attendance.out_time = max(times)
        #     attendance.in_time = min(times)
        #     attendance.db_update()
        #     frappe.db.commit()
        # else:
        #     attendance = frappe.new_doc("Unregistered Employee")
        #     in_time = log_time
        #     attendance.update({
        #         "employee": employee,
        #         "attendance_date": date,
        #         "stgid": device_id,
        #         "in_time": in_time,
        #     })
        #     attendance.save(ignore_permissions=True)
        #     frappe.db.commit()
        # frappe.response.type = "text"
        return "no"