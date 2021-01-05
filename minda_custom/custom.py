import frappe,os
import random
from datetime import datetime
from frappe.utils.data import today, add_days
from dateutil.relativedelta import relativedelta
from datetime import timedelta

@frappe.whitelist()
def get_check():
    print("call")
    checkins = frappe.db.sql(
        """select * from `tabEmployee Checkin` where skip_auto_attendance = 0 """, as_dict=1)
    if checkins:
        for c in checkins:
            att = mark_attendance_from_checkin(c.employee,c.log_date,
                             c.user_id,c.log_type,c.time)

            if att:
                frappe.db.set_value("Employee Checkin",
                                    c.name, "skip_auto_attendance", "1")
        return "ok"

def mark_attendance_from_checkin(employee,log_date,user_id,log_type,time):
    print(employee,log_date,user_id,log_type,time)
    a_min_time = datetime.strptime('05:00', '%H:%M')
    a_max_time = datetime.strptime('08:00', '%H:%M')
    b_min_time = datetime.strptime('12:00', '%H:%M')
    b_max_time = datetime.strptime('20:00', '%H:%M')
    c_min_time = datetime.strptime('20:00', '%H:%M')
    c_max_time = datetime.strptime('05:00', '%H:%M')
    c_max_time1 = datetime.strptime('06:30', '%H:%M')
    g_min_time = datetime.strptime('08:00', '%H:%M')
    g_max_time = datetime.strptime('12:00', '%H:%M')
    ot_from_time =datetime.strptime('08:00','%H:%M')
    employee = frappe.db.get_value("Employee", {
        "name": user_id, "status": "Active"})
    if employee:
        date = log_date
        time_m = time
        emp = frappe.get_doc("Employee", employee)
        c_time = datetime.strptime(str(time), '%Y-%m-%d %H:%M:%S').time()
        att_time = datetime.strptime(str(c_time), '%H:%M:%S')
        # print(att_time)
        if(log_type=="IN"):
            # print("IN")
            if att_time >= a_min_time and att_time <= a_max_time:
                shift = "A"
                status = "Present"
            elif att_time >= b_min_time and att_time <= b_max_time:
                shift = "B"
                status = "Present"
            elif att_time >= c_min_time and att_time <= c_max_time:
                shift = "C"
                status = "Present"
            elif att_time >= g_min_time and att_time <= g_max_time:
                shift ="G"
                status ="Present"    
            else:
                status = "Absent"
            # print (shift)
            # print(att_time)
            attendance = frappe.new_doc("Attendance")
            attendance.update({
                "employee": emp.employee,
                "status": status,
                "attendance_date":log_date,
                "in_time": att_time,
                "out_time":"",
                "shift": shift
            })
            attendance.save(ignore_permissions=True)
            frappe.errprint(attendance)
            attendance.submit()
            frappe.db.commit()
            frappe.response.type = "text"
            return "ok"
        elif(log_type=="OUT"):
            if att_time <= c_max_time1:
                # print(log_date,att_time)
                if frappe.db.exists("Attendance",{"attendance_date":add_days(log_date,-1),"employee":emp.name}):
                    attendance=frappe.get_doc("Attendance",{"attendance_date":add_days(log_date,-1),"employee":emp.name})
                    out_date = log_date
                    print(att_time)
                    print(attendance.name)
                    # frappe.db.set_value("Attendance",attendance.name,"out",att_time)                
                    attendance.update({
                        "out_time": att_time,
                        "out_date":out_date
                    })
                    attendance.save(ignore_permissions=True)
                        # attendance.submit()
                    frappe.db.commit()
                    frappe.response.type = "text"
                    return "ok"
            else:
                if frappe.db.exists("Attendance",{"attendance_date":log_date,"employee":emp.name}):
                    # print(log_date,att_time)
                    attendance=frappe.get_doc("Attendance",{"attendance_date":log_date,"employee":emp.name})
                    # frappe.db.set_value("Attendance",attendance.name,"out",att_time)
                    out_date = log_date
                    inti = datetime.strptime(str(attendance.intime), '%H:%M:%S')
                    print(inti)
                    at_time = datetime.strftime(att_time, '%Y-%m-%d %H:%M:%S')
                    a_time = datetime.strptime(str(at_time), '%Y-%m-%d %H:%M:%S').time()
                    att_time = datetime.strptime(str(a_time), '%H:%M:%S')
                    # att = datetime.strptime(str(att_time), '%H:%M:%S')
                    print(att_time)
                    twh={}
                    twh=(att_time-inti)
                    
                    print(twh)
                    twh = datetime.strptime(str(twh), "%H:%M:%S")
                    t =twh.strftime("%H")
                    t1=int(t)
                    print(t1)
                    if t1 >= 4 and t1 < 9:
                        status = "Present"
                        # print(status)
                    elif t1 >= 9:
                        status = "Present"
                        print(status)
                        # date=log_date
                        # at_time = datetime.strftime(da, '%Y-%m-%d %H:%M:%S')
                        # date= datetime.strptime(str(at_time), '%Y-%m-%d %H:%M:%S')
                        # print(date)
                        # print(type(date))
                        
                        from_time = attendance.intime + ot_from_time
                        f_time = from_time.time()
                        print(type(f_time))
                        from_time = datetime.combine( date,f_time)
                        print(from_time)
                        print(type(from_time))
                        a_time=att_time.time()
                        at_time =datetime.combine(date,a_time)
                        hrs=at_time-from_time
                        # time_d_ms  = hrs/ datetime.timedelta(milliseconds=1)
                        time_d_float = hrs.total_seconds()
                        hour = time_d_float // 3600
                        print(hour)
                        print(attendance.shift)     
                        ts=frappe.db.sql("""select name from `tabEmployee` where ot_applicable = 1 """, as_dict=1)
                        if ts:
                            timesheet=frappe.new_doc("Timesheet") 
                            print(emp.name)
                            # print(log_date)
                            print(type(hrs))
                            timesheet.employee=emp.name
                            timesheet.append("time_logs",{ 
                                "activity_type":"Over Time",
                                "from_time":from_time,
                                "to_time":at_time,
                                "hours":hour
                            })
                            timesheet.save(ignore_permissions=True)
                            frappe.db.commit()
                            
                    else:
                        status = "Absent"
                    attendance.update({
                        "outtime": att_time,
                        "out_date":out_date,
                        # "status": status
                    })
                    # print(attendance.outtime)
                    attendance.save(ignore_permissions=True)
                    # attendance.submit()
                    frappe.db.commit()
                    frappe.response.type = "text"
                    return "ok"
# def total_working_hours():
#     twh = frappe.db.sql(
#         """select abs(timestampdiff(hour, s.in, s.out)),s.out,s.in  from `tabAttendance` s """, as_dict=1)   
#     print(twh) 
#     if twh >= 4 and twh <= 9:
#         status = "Present"
#     elif twh >= 9:
#         status = "Present"
#         frappe.new_doc("Timesheet")    
#     else:
#         status = "Absent"
#     attendance.update({
#          "status": status
#         })    
#     return status
