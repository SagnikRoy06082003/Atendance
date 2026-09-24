from flask import Flask, render_template, request, redirect, url_for, session
import os
import csv

app = Flask(__name__)
app.secret_key = "your_secret_key"

# File paths
ATTENDANCE_FILE = "attendance.csv"
USERS_FILE = "users.csv"

# Ensure CSV files exist
if not os.path.exists(ATTENDANCE_FILE):
    with open(ATTENDANCE_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Username", "Date", "Status"])

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Username", "Password", "Role"])  # Role: student/admin


# ---------- Home Routes ----------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")


# ---------- Authentication Routes ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role")

        if not username or not password or not role:
            return "Error: All fields are required!", 400

        with open(USERS_FILE, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([username, password, role])

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        with open(USERS_FILE, "r") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                if row and row[0] == username and row[1] == password:
                    session["user"] = username
                    session["role"] = row[2]
                    return redirect(url_for("dashboard"))

        return "Invalid credentials", 403

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# ---------- Dashboard Routes ----------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    user = session["user"]
    role = session["role"]
    attendance_records = []

    with open(ATTENDANCE_FILE, "r") as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        if role == "admin":
            attendance_records = [row for row in reader]  # Admin sees all records
        else:
            attendance_records = [row for row in reader if row[0] == user]  # Student sees own records

    return render_template("dashboard.html", username=user, role=role, attendance=attendance_records)


# ---------- Attendance Routes ----------
@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    print("Form Data:", request.form)

    student_name = request.form.get("student_name")
    entry_time = request.form.get("entry_time")
    exit_time = request.form.get("exit_time")
    duration = request.form.get("duration")
    status = request.form.get("status")

    if not (student_name and entry_time and exit_time and status):
        print("Missing fields:", {"student_name": student_name, "entry_time": entry_time, "exit_time": exit_time, "status": status})
        return "Error: Missing form fields", 400

    # Save to CSV (if needed)
    with open("attendance.csv", "a") as f:
        f.write(f"{student_name},{entry_time},{exit_time},{duration},{status}\n")

    return redirect(url_for("dashboard"))



# ---------- Run App ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
