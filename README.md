# Graphic Era (Deemed to be University) - College Management System
Official portal & ERP system for Graphic Era (Deemed to be University), Dehradun, Uttarakhand ([https://geu.ac.in](https://geu.ac.in)).

Built with **Flask + SQLite3 + Jinja2 + Chart.js**. Features secure password hashing (Werkzeug), CSRF protection (Flask-WTF), role-based access control (Admin, Faculty, Student), parameterized SQL queries, foreign key constraints, and mobile-responsive UI.

---

## Demo Accounts

| Role | Username | Password | Email | Access |
|---|---|---|---|---|
| **Admin** | `admin` | `admin123` | `admin@geu.ac.in` | Full ERP Control: Registry, Faculty, Admissions, Events, Notices, Analytics |
| **Faculty** | `faculty1` | `faculty123` | `faculty1@geu.ac.in` | Course Management, Student Attendance, Semester Marks Entry |
| **Student** | `student1` | `student123` | `student1@geu.ac.in` | Student Dashboard, Attendance %, Semester Results, Circulars |

*New students enrolled by Admin receive the default password `Student@123`.*  
*New faculty enrolled by Admin receive the default password `Faculty@123`.*

---

## University Credentials & Information
* **Accreditation:** NAAC Grade 'A+'
* **NIRF Rankings:** Top 55 Universities in India (48th University, 52nd Engineering, 52nd Management)
* **Campus Address:** 566/6, Bell Road, Society Area, Clement Town, Dehradun, Uttarakhand, PIN: 248002
* **Toll-Free Helpline:** 1800 890 6027
* **Official Website:** [https://geu.ac.in](https://geu.ac.in)

---

## How to Run

1. **Activate Environment & Install Requirements**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate       # macOS / Linux (Windows: venv\Scripts\activate)
   pip install -r requirements.txt
   ```

2. **Launch Application**:
   ```bash
   python app.py
   ```
   *(Database `database.db` is initialized and seeded automatically with Graphic Era schools, courses, faculty, students, events, and notices.)*

3. **Open in Browser**:
   Visit [http://127.0.0.1:5000](http://127.0.0.1:5000)
