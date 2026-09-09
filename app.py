from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

import sqlite3
from functools import wraps


app = Flask(__name__)

# Secret key is required for sessions and flash messages
app.secret_key = "my-secret-key"


DATABASE = "database.db"


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# --------------------------------------------------
# CREATE DATABASE
# --------------------------------------------------

def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            course TEXT NOT NULL,
            gender TEXT NOT NULL,
            date_of_birth TEXT,
            address TEXT,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# --------------------------------------------------
# ADMIN LOGIN REQUIRED
# --------------------------------------------------

def login_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if "logged_in" not in session:
            return redirect(url_for("login"))

        return function(*args, **kwargs)

    return wrapper


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        # Simple login for learning purposes
        if username == "admin" and password == "admin123":

            session["logged_in"] = True
            session["username"] = username

            flash("Login successful!", "success")

            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "danger")

    return render_template("login.html")


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

@app.route("/logout")
def logout():

    session.clear()

    flash("You have been logged out.", "success")

    return redirect(url_for("login"))


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------
@app.route("/")
@login_required
def dashboard():

    connection = get_db_connection()

    # -----------------------------------------
    # BASIC STATISTICS
    # -----------------------------------------

    total_students = connection.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    total_courses = connection.execute(
        "SELECT COUNT(DISTINCT course) FROM students"
    ).fetchone()[0]

    male_students = connection.execute(
        "SELECT COUNT(*) FROM students WHERE gender = 'Male'"
    ).fetchone()[0]

    female_students = connection.execute(
        "SELECT COUNT(*) FROM students WHERE gender = 'Female'"
    ).fetchone()[0]


    # -----------------------------------------
    # STUDENTS BY COURSE
    # -----------------------------------------

    course_data = connection.execute("""
        SELECT course, COUNT(*) AS total
        FROM students
        GROUP BY course
        ORDER BY total DESC
    """).fetchall()


    # -----------------------------------------
    # STUDENTS BY GENDER
    # -----------------------------------------

    gender_data = connection.execute("""
        SELECT gender, COUNT(*) AS total
        FROM students
        GROUP BY gender
    """).fetchall()


    # -----------------------------------------
    # RECENT STUDENTS
    # -----------------------------------------

    recent_students = connection.execute("""
        SELECT *
        FROM students
        ORDER BY id DESC
        LIMIT 5
    """).fetchall()


    # -----------------------------------------
    # MONTHLY REGISTRATIONS
    # -----------------------------------------

    monthly_data = connection.execute("""
        SELECT
            strftime('%Y-%m', registration_date) AS month,
            COUNT(*) AS total
        FROM students
        GROUP BY month
        ORDER BY month
    """).fetchall()


    connection.close()


    # -----------------------------------------
    # PREPARE DATA FOR CHARTS
    # -----------------------------------------

    course_labels = [
        row["course"]
        for row in course_data
    ]

    course_values = [
        row["total"]
        for row in course_data
    ]


    gender_labels = [
        row["gender"]
        for row in gender_data
    ]

    gender_values = [
        row["total"]
        for row in gender_data
    ]


    monthly_labels = [
        row["month"]
        for row in monthly_data
    ]

    monthly_values = [
        row["total"]
        for row in monthly_data
    ]


    return render_template(
        "dashboard.html",

        total_students=total_students,
        total_courses=total_courses,
        male_students=male_students,
        female_students=female_students,

        recent_students=recent_students,

        course_labels=course_labels,
        course_values=course_values,

        gender_labels=gender_labels,
        gender_values=gender_values,

        monthly_labels=monthly_labels,
        monthly_values=monthly_values
    )


# --------------------------------------------------
# READ / SEARCH / FILTER STUDENTS
# --------------------------------------------------

@app.route("/students")
@login_required
def students():

    search = request.args.get("search", "")
    course = request.args.get("course", "")

    conn = get_db_connection()

    query = "SELECT * FROM students WHERE 1=1"
    parameters = []

    if search:

        query += """
            AND (
                name LIKE ?
                OR email LIKE ?
                OR phone LIKE ?
            )
        """

        search_value = f"%{search}%"

        parameters.extend([
            search_value,
            search_value,
            search_value
        ])

    if course:

        query += " AND course = ?"

        parameters.append(course)

    query += " ORDER BY id DESC"

    students = conn.execute(
        query,
        parameters
    ).fetchall()

    courses = conn.execute("""
        SELECT DISTINCT course
        FROM students
        ORDER BY course
    """).fetchall()

    conn.close()

    return render_template(
        "index.html",
        students=students,
        courses=courses,
        search=search,
        selected_course=course
    )


# --------------------------------------------------
# CREATE STUDENT
# --------------------------------------------------

@app.route("/add", methods=["GET", "POST"])
@login_required
def add_student():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        course = request.form["course"]
        gender = request.form["gender"]
        date_of_birth = request.form["date_of_birth"]
        address = request.form["address"]

        if not name or not email or not phone or not course:

            flash("Please fill in all required fields.", "danger")

            return render_template("add.html")

        conn = get_db_connection()

        try:

            conn.execute("""
                INSERT INTO students
                (
                    name,
                    email,
                    phone,
                    course,
                    gender,
                    date_of_birth,
                    address
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                email,
                phone,
                course,
                gender,
                date_of_birth,
                address
            ))

            conn.commit()

            flash(
                "Student added successfully!",
                "success"
            )

        except sqlite3.IntegrityError:

            flash(
                "A student with this email already exists.",
                "danger"
            )

        finally:

            conn.close()

        return redirect(url_for("students"))

    return render_template("add.html")


# --------------------------------------------------
# VIEW STUDENT DETAILS
# --------------------------------------------------

@app.route("/student/<int:id>")
@login_required
def details(id):

    conn = get_db_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (id,)
    ).fetchone()

    conn.close()

    if student is None:

        return render_template("404.html"), 404

    return render_template(
        "details.html",
        student=student
    )


# --------------------------------------------------
# UPDATE STUDENT
# --------------------------------------------------

@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_student(id):

    conn = get_db_connection()

    student = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (id,)
    ).fetchone()

    if student is None:

        conn.close()

        return render_template("404.html"), 404

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        course = request.form["course"]
        gender = request.form["gender"]
        date_of_birth = request.form["date_of_birth"]
        address = request.form["address"]

        try:

            conn.execute("""
                UPDATE students
                SET
                    name = ?,
                    email = ?,
                    phone = ?,
                    course = ?,
                    gender = ?,
                    date_of_birth = ?,
                    address = ?
                WHERE id = ?
            """, (
                name,
                email,
                phone,
                course,
                gender,
                date_of_birth,
                address,
                id
            ))

            conn.commit()

            flash(
                "Student updated successfully!",
                "success"
            )

        except sqlite3.IntegrityError:

            flash(
                "Another student is already using this email.",
                "danger"
            )

        finally:

            conn.close()

        return redirect(url_for("students"))

    conn.close()

    return render_template(
        "edit.html",
        student=student
    )


# --------------------------------------------------
# DELETE STUDENT
# --------------------------------------------------

@app.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete_student(id):

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM students WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    flash(
        "Student deleted successfully!",
        "success"
    )

    return redirect(url_for("students"))


# --------------------------------------------------
# 404 ERROR
# --------------------------------------------------

@app.errorhandler(404)
def page_not_found(error):

    return render_template("404.html"), 404


# --------------------------------------------------
# START APPLICATION
# --------------------------------------------------

if __name__ == "__main__":

    init_db()

    app.run(debug=True)