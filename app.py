import os, sqlite3
from datetime import date
from functools import wraps
from flask import Flask, g, render_template, request, redirect, url_for, session, flash
from flask_wtf.csrf import CSRFProtect, generate_csrf
from markupsafe import Markup
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "geu-dehradun-secret-key-2026")
CSRFProtect(app)
app.jinja_env.globals["csrf"] = lambda: Markup(f'<input type="hidden" name="csrf_token" value="{generate_csrf()}">')
DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN('admin','faculty','student')));
CREATE TABLE IF NOT EXISTS departments(id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL, description TEXT);
CREATE TABLE IF NOT EXISTS faculty(id INTEGER PRIMARY KEY, user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL, designation TEXT, qualification TEXT, department_id INTEGER REFERENCES departments(id));
CREATE TABLE IF NOT EXISTS courses(id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL,
  department_id INTEGER NOT NULL REFERENCES departments(id), faculty_id INTEGER REFERENCES faculty(id) ON DELETE SET NULL);
CREATE TABLE IF NOT EXISTS students(id INTEGER PRIMARY KEY, user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL, roll_no TEXT UNIQUE NOT NULL, department_id INTEGER REFERENCES departments(id), course_id INTEGER REFERENCES courses(id));
CREATE TABLE IF NOT EXISTS admissions(id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL, phone TEXT NOT NULL,
  dob TEXT NOT NULL, gender TEXT NOT NULL, address TEXT NOT NULL, department_id INTEGER REFERENCES departments(id),
  course TEXT NOT NULL, qualification TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Pending', created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS attendance(id INTEGER PRIMARY KEY, student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE, date TEXT NOT NULL, present INTEGER NOT NULL CHECK(present IN(0,1)),
  UNIQUE(student_id,course_id,date));
CREATE TABLE IF NOT EXISTS results(id INTEGER PRIMARY KEY, student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE, marks REAL NOT NULL CHECK(marks BETWEEN 0 AND 100),
  UNIQUE(student_id,course_id));
CREATE TABLE IF NOT EXISTS notices(id INTEGER PRIMARY KEY, title TEXT NOT NULL, body TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL, event_date TEXT NOT NULL, venue TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS contact_messages(id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL, message TEXT NOT NULL, created_at TEXT NOT NULL);
"""

def init_db():
    c = sqlite3.connect(DB); c.execute("PRAGMA foreign_keys=ON"); c.executescript(SCHEMA)
    if not c.execute("SELECT 1 FROM users").fetchone():
        h = generate_password_hash; t = date.today().isoformat()
        c.executemany("INSERT INTO departments(name,description) VALUES(?,?)", [
            ("Computer Science & Engineering", "Computing, AI & ML, Data Science, Cyber Security and High-Performance Systems."),
            ("Computer Applications", "Full-Stack Software Development, Cloud Architecture, BCA and MCA programs."),
            ("Management Studies", "MBA, BBA, Financial Engineering, Marketing, HR and Business Analytics."),
            ("Electronics & Communication", "VLSI Design, Embedded Systems, IoT, Robotics and Wireless Communication."),
            ("Mechanical & Aerospace Engineering", "Robotics, Thermal Engineering, CAD/CAM, Autonomous Vehicles and Aeronautics."),
            ("Life Sciences & Biotechnology", "Biotechnology, Microbiology, Genomics, Bioinformatics and Food Technology."),
            ("Commerce & Accounting", "B.Com (Hons), Corporate Accounting, Financial Analysis, Audit and Taxation."),
            ("Humanities & Social Sciences", "Psychology, Economics, English, Mass Communication and Journalism.")
        ])
        c.executemany("INSERT INTO users(username,email,password_hash,role) VALUES(?,?,?,?)", [
            ("admin", "admin@geu.ac.in", h("admin123"), "admin"),
            ("faculty1", "faculty1@geu.ac.in", h("faculty123"), "faculty"),
            ("faculty2", "faculty2@geu.ac.in", h("faculty123"), "faculty"),
            ("student1", "student1@geu.ac.in", h("student123"), "student"),
            ("student2", "student2@geu.ac.in", h("student123"), "student"),
            ("student3", "student3@geu.ac.in", h("student123"), "student")
        ])
        c.executemany("INSERT INTO faculty(user_id,name,designation,qualification,department_id) VALUES(?,?,?,?,?)", [
            (2, "Prof. (Dr.) Devesh Pratap Singh", "Professor & Dean", "Ph.D. Computer Science & Engineering", 1),
            (3, "Prof. (Dr.) Ankush Mittal", "Professor & Director Research", "Ph.D. (IIT Delhi), Senior IEEE Member", 1)
        ])
        c.executemany("INSERT INTO courses(name,department_id,faculty_id) VALUES(?,?,?)", [
            ("B.Tech Computer Science & Engineering", 1, 1),
            ("B.Tech AI & Machine Learning", 1, 2),
            ("BCA (Bachelor of Computer Applications)", 2, 1),
            ("MCA (Master of Computer Applications)", 2, 2),
            ("MBA (Master of Business Administration)", 3, None),
            ("BBA (Bachelor of Business Administration)", 3, None),
            ("B.Sc (Hons) Biotechnology", 6, None),
            ("B.Com (Hons) Professional", 7, None)
        ])
        c.executemany("INSERT INTO students(user_id,name,roll_no,department_id,course_id) VALUES(?,?,?,?,?)", [
            (4, "Rohan Sharma", "GEU2024001", 1, 1),
            (5, "Meera Joshi", "GEU2024002", 1, 1),
            (6, "Ayush Verma", "GEU2024003", 1, 2)
        ])
        c.executemany("INSERT INTO notices(title,body,created_at) VALUES(?,?,?)", [
            ("Grafest 2026: Annual Techno-Cultural Fest Registrations Open",
             "Graphic Era University's flagship annual techno-cultural festival Grafest 2026 is scheduled for next month. Student registrations for hackathons, battle of bands, dance, fashion show and star night passes are now live on the portal.", t),
            ("Graphic Era Placement Drive: Highest Package Record ₹84.88 LPA",
             "Campus recruitment drive for 2026 commenced with premier recruiters including Google, Microsoft, Adobe, Amazon and Morgan Stanley visiting the Clement Town campus.", t),
            ("Admissions Open 2026-27 (UG / PG / Ph.D. Programs)",
             "Applications are invited for B.Tech, BCA, MCA, MBA, and Allied Sciences for the academic session 2026-27. Apply online or visit Clement Town campus.", t),
            ("End-Semester Examination Timetable Announced",
             "The final examination schedule for all undergraduate and postgraduate programs has been published on the student ERP portal.", t)
        ])
        c.executemany("INSERT INTO events(title,description,event_date,venue) VALUES(?,?,?,?)", [
            ("Grafest 2026 - Mega Star Night & Cultural Conclave",
             "Celebrity live musical concert, national battle of bands, fashion panorama, and technical project exhibitions.",
             "2026-11-28", "Main University Sports Grounds, Clement Town"),
            ("National Hackathon & AI Innovation Summit",
             "36-hour non-stop hackathon on Generative AI, Cyber Security, and Green Tech with cash prizes up to ₹5 Lakhs.",
             "2026-12-10", "Chanakya Block High-Performance Lab"),
            ("Annual Corporate Placement & Alumni Conclave",
             "Interactive mentorship and placement networking session with top CXOs and Graphic Era alumni.",
             "2027-01-15", "Prof. K.P. Nautiyal Central Auditorium"),
            ("International Conference on Emerging Computing & IoT",
             "Peer-reviewed IEEE technical paper presentations and keynotes by global computer science researchers.",
             "2027-02-05", "Convention Centre, GEU Dehradun")
        ])
        c.executemany("INSERT INTO results(student_id,course_id,marks) VALUES(?,?,?)", [
            (1, 1, 88.5),
            (2, 1, 76.0),
            (3, 2, 92.0)
        ])
        c.executemany("INSERT INTO attendance(student_id,course_id,date,present) VALUES(?,?,?,?)", [
            (1, 1, t, 1),
            (2, 1, t, 1),
            (3, 2, t, 1)
        ])
    c.commit(); c.close()

def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB); g.db.row_factory = sqlite3.Row; g.db.execute("PRAGMA foreign_keys=ON")
    return g.db

@app.teardown_appcontext
def _close(e):
    d = g.pop("db", None)
    if d: d.close()

def q(sql, a=(), one=False):
    r = db().execute(sql, a).fetchall()
    return (r[0] if r else None) if one else r

def run(sql, a=()):
    db().execute(sql, a); db().commit()

def role_required(role):
    def deco(f):
        @wraps(f)
        def w(*a, **k):
            if session.get("role") != role:
                flash("Please log in with the correct account.", "danger"); return redirect(url_for("login"))
            return f(*a, **k)
        return w
    return deco

def grade(m):
    return "A+" if m >= 90 else "A" if m >= 80 else "B" if m >= 70 else "C" if m >= 55 else "D" if m >= 40 else "F"

# ---------- public ----------
@app.route("/")
def index():
    stats = {k: q(f"SELECT COUNT(*) n FROM {k}", one=True)["n"] for k in ("students", "faculty", "departments", "courses")}
    return render_template("index.html", stats=stats, depts=q("SELECT * FROM departments"),
        faculty=q("SELECT f.*, d.name dept FROM faculty f LEFT JOIN departments d ON d.id=f.department_id"),
        notices=q("SELECT * FROM notices ORDER BY id DESC LIMIT 4"), events=q("SELECT * FROM events ORDER BY event_date LIMIT 4"))

@app.post("/apply")
def apply():
    f = {k: request.form.get(k, "").strip() for k in ("name", "email", "phone", "dob", "gender", "address", "department_id", "course", "qualification")}
    if not all(f.values()) or "@" not in f["email"] or not f["phone"].replace("+", "").replace("-", "").isdigit() or not f["department_id"].isdigit():
        flash("Please fill every admission field with valid values.", "danger"); return redirect(url_for("admissions"))
    run("INSERT INTO admissions(name,email,phone,dob,gender,address,department_id,course,qualification,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
        (*f.values(), date.today().isoformat()))
    flash("Application submitted successfully. Graphic Era Admissions Office will contact you shortly.", "success"); return redirect(url_for("admissions"))

@app.post("/contact")
def contact():
    n, e, m = (request.form.get(k, "").strip() for k in ("name", "email", "message"))
    if not (n and m and "@" in e):
        flash("Please complete all contact form fields.", "danger")
    else:
        run("INSERT INTO contact_messages(name,email,message,created_at) VALUES(?,?,?,?)", (n, e, m, date.today().isoformat()))
        flash("Thank you for contacting Graphic Era University. We will respond soon!", "success")
    return redirect(url_for("contact_page"))

# ---------- auth ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        ident, pw = request.form.get("username", "").strip(), request.form.get("password", "")
        u = q("SELECT * FROM users WHERE username=? OR email=?", (ident, ident), one=True)
        if u and check_password_hash(u["password_hash"], pw):
            session.clear(); session.update(uid=u["id"], role=u["role"])
            return redirect(url_for(u["role"]))
        flash("Invalid username/email or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear(); flash("Logged out successfully.", "success"); return redirect(url_for("index"))

# ---------- public pages ----------
PAGES = {
    "about": "about.html",
    "academics": "departments.html",
    "events": "events.html",
    "notices": "notices.html",
    "contact": "contact.html",
    "admissions": "admissions.html",
    "faculty-members": "faculty_public.html"
}

def _public(name, tpl):
    def view():
        return render_template(tpl,
            depts=q("SELECT d.*, (SELECT COUNT(*) FROM courses c WHERE c.department_id=d.id) nc FROM departments d"),
            events=q("SELECT * FROM events ORDER BY event_date"),
            notices=q("SELECT * FROM notices ORDER BY id DESC"),
            faculty=q("SELECT f.*, d.name dept FROM faculty f LEFT JOIN departments d ON d.id=f.department_id"))
    return view

for _p, _t in PAGES.items():
    app.add_url_rule("/" + _p, {"contact": "contact_page"}.get(_p, _p.replace("-", "_")), _public(_p, _t))

def _admin_page(ep, path, tpl, extra):
    def view():
        return render_template(tpl, **extra())
    view.__name__ = ep
    app.add_url_rule(path, ep, role_required("admin")(view))

@app.route("/admin")
@role_required("admin")
def admin():
    s = {"Students": "students", "Faculty": "faculty", "Departments": "departments", "Courses": "courses", "Events": "events", "Notices": "notices"}
    stats = {k: q(f"SELECT COUNT(*) n FROM {t}", one=True)["n"] for k, t in s.items()}
    stats["Pending Admissions"] = q("SELECT COUNT(*) n FROM admissions WHERE status='Pending'", one=True)["n"]
    dc = [[r["n"], r["c"]] for r in q("SELECT d.name n, COUNT(s.id) c FROM departments d LEFT JOIN students s ON s.department_id=d.id GROUP BY d.id")]
    ac = [[r["n"], r["c"]] for r in q("SELECT status n, COUNT(*) c FROM admissions GROUP BY status")]
    return render_template("admin_dash.html", stats=stats, dc=dc, ac=ac)

_admin_page("admin_students", "/admin/students", "admin_students.html", lambda: dict(
    courses=q("SELECT * FROM courses"),
    depts=q("SELECT * FROM departments"),
    students=q("""SELECT s.*, d.name dept, c.name course FROM students s
                  LEFT JOIN departments d ON d.id=s.department_id
                  LEFT JOIN courses c ON c.id=s.course_id
                  WHERE s.name LIKE ? AND (?='' OR s.department_id=?) ORDER BY s.id""",
               (f"%{request.args.get('s', '')}%", request.args.get("d", ""), request.args.get("d", "")))
))

_admin_page("admin_faculty", "/admin/faculty", "admin_faculty.html", lambda: dict(
    depts=q("SELECT * FROM departments"),
    faculty=q("SELECT f.*, d.name dept FROM faculty f LEFT JOIN departments d ON d.id=f.department_id")
))

_admin_page("admin_admissions", "/admin/admissions", "admin_admissions.html", lambda: dict(
    admissions=q("SELECT a.*, d.name dept FROM admissions a LEFT JOIN departments d ON d.id=a.department_id ORDER BY a.id DESC"),
    msgs=q("SELECT * FROM contact_messages ORDER BY id DESC")
))

_admin_page("admin_events", "/admin/events", "admin_events.html", lambda: dict(
    events=q("SELECT * FROM events ORDER BY event_date"),
    e=q("SELECT * FROM events WHERE id=?", (request.args.get("edit", 0),), one=True)
))

_admin_page("admin_notices", "/admin/notices", "admin_notices.html", lambda: dict(
    notices=q("SELECT * FROM notices ORDER BY id DESC")
))

@app.post("/admin/events/save")
@role_required("admin")
def save_event():
    t, d, dt, v = (request.form.get(k, "").strip() for k in ("title", "description", "event_date", "venue"))
    if not (t and d and dt and v):
        flash("All event fields are required.", "danger")
    elif request.form.get("id", "").isdigit():
        run("UPDATE events SET title=?,description=?,event_date=?,venue=? WHERE id=?", (t, d, dt, v, request.form["id"]))
        flash("Event updated successfully.", "success")
    else:
        run("INSERT INTO events(title,description,event_date,venue) VALUES(?,?,?,?)", (t, d, dt, v))
        flash("Event published successfully.", "success")
    return redirect(url_for("admin_events"))

@app.post("/admin/events/<int:eid>/delete")
@role_required("admin")
def del_event(eid):
    run("DELETE FROM events WHERE id=?", (eid,))
    flash("Event deleted.", "success")
    return redirect(url_for("admin_events"))

@app.post("/admin/faculty/add")
@role_required("admin")
def add_faculty():
    n, e, des, qu = (request.form.get(k, "").strip() for k in ("name", "email", "designation", "qualification"))
    did = request.form.get("department_id", "")
    if not (n and "@" in e and did.isdigit()):
        flash("Name, valid email and department are required.", "danger")
    else:
        try:
            uname = e.split("@")[0].lower()
            cur = db().execute("INSERT INTO users(username,email,password_hash,role) VALUES(?,?,?,'faculty')",
                              (uname, e, generate_password_hash("Faculty@123")))
            db().execute("INSERT INTO faculty(user_id,name,designation,qualification,department_id) VALUES(?,?,?,?,?)",
                        (cur.lastrowid, n, des, qu, did))
            db().commit()
            flash(f"Faculty added. Login username: {uname} (Password: Faculty@123)", "success")
        except sqlite3.IntegrityError:
            db().rollback()
            flash("Username or email already exists.", "danger")
    return redirect(url_for("admin_faculty"))

@app.post("/admin/faculty/<int:fid>/delete")
@role_required("admin")
def del_faculty(fid):
    f = q("SELECT user_id FROM faculty WHERE id=?", (fid,), one=True)
    if f:
        run("DELETE FROM users WHERE id=?", (f["user_id"],))
        flash("Faculty member deleted.", "success")
    return redirect(url_for("admin_faculty"))

@app.post("/admin/student")
@role_required("admin")
def add_student():
    n, r, e = (request.form.get(k, "").strip() for k in ("name", "roll_no", "email"))
    cid = request.form.get("course_id", "")
    course = q("SELECT * FROM courses WHERE id=?", (cid,), one=True) if cid.isdigit() else None
    if not (n and r and "@" in e and course):
        flash("Name, roll number, valid email and course are required.", "danger")
    else:
        try:
            cur = db().execute("INSERT INTO users(username,email,password_hash,role) VALUES(?,?,?,'student')",
                              (r.lower(), e, generate_password_hash("Student@123")))
            db().execute("INSERT INTO students(user_id,name,roll_no,department_id,course_id) VALUES(?,?,?,?,?)",
                        (cur.lastrowid, n, r, course["department_id"], course["id"]))
            db().commit()
            flash(f"Student enrolled. Login: {r.lower()} (Password: Student@123)", "success")
        except sqlite3.IntegrityError:
            db().rollback()
            flash("Roll number or email already exists.", "danger")
    return redirect(url_for("admin_students"))

@app.post("/admin/student/<int:sid>/delete")
@role_required("admin")
def del_student(sid):
    s = q("SELECT user_id FROM students WHERE id=?", (sid,), one=True)
    if s:
        run("DELETE FROM users WHERE id=?", (s["user_id"],))
        flash("Student deleted.", "success")
    return redirect(url_for("admin_students"))

@app.post("/admin/admission/<int:aid>/<act>")
@role_required("admin")
def decide(aid, act):
    if act in ("Approved", "Rejected"):
        run("UPDATE admissions SET status=? WHERE id=?", (act, aid))
        flash(f"Application {act.lower()}.", "success")
    return redirect(url_for("admin_admissions"))

@app.post("/admin/notice")
@role_required("admin")
def add_notice():
    t, b = request.form.get("title", "").strip(), request.form.get("body", "").strip()
    if t and b:
        run("INSERT INTO notices(title,body,created_at) VALUES(?,?,?)", (t, b, date.today().isoformat()))
        flash("Notice published.", "success")
    else:
        flash("Title and body are required.", "danger")
    return redirect(url_for("admin_notices"))

@app.post("/admin/notice/<int:nid>/delete")
@role_required("admin")
def del_notice(nid):
    run("DELETE FROM notices WHERE id=?", (nid,))
    flash("Notice deleted.", "success")
    return redirect(url_for("admin_notices"))

# ---------- student ----------
@app.route("/student")
@role_required("student")
def student():
    s = q("""SELECT s.*, d.name dept, c.name course FROM students s
             LEFT JOIN departments d ON d.id=s.department_id
             LEFT JOIN courses c ON c.id=s.course_id WHERE s.user_id=?""", (session["uid"],), one=True)
    a = q("SELECT COUNT(*) n, COALESCE(SUM(present),0) p FROM attendance WHERE student_id=?", (s["id"],), one=True)
    pct = round(100 * a["p"] / a["n"], 1) if a["n"] else 0
    res = [dict(r, grade=grade(r["marks"])) for r in q("""SELECT r.marks, c.name course FROM results r
                                                           JOIN courses c ON c.id=r.course_id WHERE r.student_id=?""", (s["id"],))]
    return render_template("student.html", s=s, pct=pct, res=res, notices=q("SELECT * FROM notices ORDER BY id DESC LIMIT 5"))

# ---------- faculty ----------
@app.route("/faculty")
@role_required("faculty")
def faculty():
    f = q("SELECT * FROM faculty WHERE user_id=?", (session["uid"],), one=True)
    courses = [{"c": c, "students": q("""SELECT s.*, (SELECT present FROM attendance WHERE student_id=s.id AND course_id=? AND date=?) today,
        (SELECT marks FROM results WHERE student_id=s.id AND course_id=?) marks FROM students s WHERE s.course_id=?""",
        (c["id"], date.today().isoformat(), c["id"], c["id"]))} for c in q("SELECT * FROM courses WHERE faculty_id=?", (f["id"],))]
    return render_template("faculty.html", f=f, courses=courses, today=date.today().isoformat())

@app.post("/faculty/save/<int:cid>")
@role_required("faculty")
def save(cid):
    f = q("SELECT id FROM faculty WHERE user_id=?", (session["uid"],), one=True)
    if not q("SELECT 1 FROM courses WHERE id=? AND faculty_id=?", (cid, f["id"]), one=True):
        flash("You can only manage your own courses.", "danger"); return redirect(url_for("faculty"))
    for s in q("SELECT id FROM students WHERE course_id=?", (cid,)):
        run("""INSERT INTO attendance(student_id,course_id,date,present) VALUES(?,?,?,?)
               ON CONFLICT(student_id,course_id,date) DO UPDATE SET present=excluded.present""",
            (s["id"], cid, date.today().isoformat(), 1 if request.form.get(f"p_{s['id']}") else 0))
        m = request.form.get(f"m_{s['id']}", "").strip()
        if m:
            try:
                m = float(m); assert 0 <= m <= 100
                run("INSERT INTO results(student_id,course_id,marks) VALUES(?,?,?) ON CONFLICT(student_id,course_id) DO UPDATE SET marks=excluded.marks", (s["id"], cid, m))
            except (ValueError, AssertionError):
                flash("Marks must be between 0 and 100.", "danger")
    flash("Attendance and examination marks saved successfully.", "success")
    return redirect(url_for("faculty"))

init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=True)
