from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import mysql.connector
import os
import re


app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "college_department_management_secret_key_2026"
)


# =====================================================
# DATABASE CONNECTION
# =====================================================

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="---",
        database="college_department_db"
    )


# =====================================================
# DATABASE INITIALIZATION
# =====================================================

_db_initialized = False


def init_db():
    """Create required tables if they do not already exist."""

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                role ENUM('Admin', 'Staff') NOT NULL DEFAULT 'Staff',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Departments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                department_id INT AUTO_INCREMENT PRIMARY KEY,
                department_name VARCHAR(100) NOT NULL,
                department_code VARCHAR(20) NOT NULL,
                hod_name VARCHAR(100),
                email VARCHAR(100),
                phone VARCHAR(20)
            )
        """)

        # Faculty table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS faculty (
                faculty_id INT AUTO_INCREMENT PRIMARY KEY,
                faculty_name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL,
                phone VARCHAR(20),
                designation VARCHAR(100),
                department_id INT,
                FOREIGN KEY (department_id)
                    REFERENCES departments(department_id)
                    ON DELETE RESTRICT
            )
        """)

        # Students table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id INT AUTO_INCREMENT PRIMARY KEY,
                student_name VARCHAR(100) NOT NULL,
                roll_number VARCHAR(50) NOT NULL,
                email VARCHAR(100),
                phone VARCHAR(20),
                year VARCHAR(20) NOT NULL,
                department_id INT,
                FOREIGN KEY (department_id)
                    REFERENCES departments(department_id)
                    ON DELETE RESTRICT
            )
        """)

        # Courses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                course_id INT AUTO_INCREMENT PRIMARY KEY,
                course_name VARCHAR(100) NOT NULL,
                course_code VARCHAR(20) NOT NULL,
                credits INT NOT NULL,
                department_id INT,
                FOREIGN KEY (department_id)
                    REFERENCES departments(department_id)
                    ON DELETE RESTRICT
            )
        """)

        connection.commit()
        cursor.close()
        connection.close()

    except Exception as e:
        print(f"Database initialization notice: {e}")


@app.before_request
def ensure_db_initialized():
    global _db_initialized

    if not _db_initialized:
        _db_initialized = True
        init_db()


# =====================================================
# AUTHENTICATION & ACCESS CONTROL
# =====================================================

ADMIN_SECRET_KEY = os.environ.get(
    "ADMIN_SECRET_KEY",
    "AdminSecureKey2026"
)


def is_admin(role):
    return role == "Admin"


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for("login"))

        if not is_admin(session.get("role")):
            flash(
                "Access denied: Staff members cannot delete records. "
                "Only Administrators have delete permissions.",
                "error"
            )
            return redirect(url_for("index"))

        return f(*args, **kwargs)

    return decorated_function


# =====================================================
# LOGIN
# =====================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if "user_id" in session:
        return redirect(url_for("index"))

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please provide both email and password.", "error")
            return render_template("login.html")

        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                "SELECT * FROM users WHERE email = %s",
                (email,)
            )

            user = cursor.fetchone()

            cursor.close()
            connection.close()

            if user and check_password_hash(
                user["password_hash"],
                password
            ):

                # Keep the database role exactly as Admin or Staff
                user_role = "Admin" if is_admin(user.get("role")) else "Staff"

                session["user_id"] = user["user_id"]
                session["name"] = user["name"]
                session["email"] = user["email"]
                session["role"] = user_role

                display_role = (
                    "Administrator"
                    if user_role == "Admin"
                    else "Staff"
                )

                flash(
                    f"Welcome back, {user['name']}! "
                    f"Logged in as {display_role}.",
                    "success"
                )

                return redirect(url_for("index"))

            else:
                flash(
                    "Invalid email or password. Please try again.",
                    "error"
                )

        except mysql.connector.Error as e:
            flash(
                f"Database connection error: {e}",
                "error"
            )

    return render_template("login.html")


# =====================================================
# PUBLIC REGISTRATION
# =====================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if "user_id" in session:
        return redirect(url_for("index"))

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        admin_key = request.form.get("admin_key", "").strip()

        if not name or not email or not password or not confirm_password:
            flash(
                "All required fields must be filled.",
                "error"
            )
            return render_template("register.html")

        if len(password) < 6:
            flash(
                "Password must be at least 6 characters long.",
                "error"
            )
            return render_template("register.html")

        if password != confirm_password:
            flash(
                "Passwords do not match. Please verify and try again.",
                "error"
            )
            return render_template("register.html")

        # Normal registration creates Staff
        role = "Staff"

        # Administrator registration requires security key
        if admin_key:

            if admin_key == ADMIN_SECRET_KEY:
                role = "Admin"

            else:
                flash(
                    "Invalid Administrator Security Key.",
                    "error"
                )
                return render_template("register.html")

        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                "SELECT user_id FROM users WHERE email = %s",
                (email,)
            )

            if cursor.fetchone():

                cursor.close()
                connection.close()

                flash(
                    "An account with this email address already exists. "
                    "Please log in.",
                    "error"
                )

                return redirect(url_for("login"))

            password_hash = generate_password_hash(password)

            cursor.execute("""
                INSERT INTO users
                (name, email, password_hash, role)
                VALUES (%s, %s, %s, %s)
            """, (
                name,
                email,
                password_hash,
                role
            ))

            connection.commit()

            cursor.close()
            connection.close()

            display_role = (
                "Administrator"
                if role == "Admin"
                else "Staff"
            )

            flash(
                f"Registration successful! "
                f"You can now log in as {display_role}.",
                "success"
            )

            return redirect(url_for("login"))

        except mysql.connector.Error as e:

            flash(
                f"Database error during registration: {e}",
                "error"
            )

            return render_template("register.html")

    return render_template("register.html")


# =====================================================
# ADMIN REGISTER
# =====================================================

@app.route("/admin/register", methods=["POST"])
@login_required
@admin_required
def admin_register():

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    role = request.form.get("role", "Staff").strip()
    password = request.form.get("password", "")

    if not name or not email or not password:
        flash(
            "All fields are required.",
            "error"
        )
        return redirect(url_for("index"))

    # Database accepts only Admin or Staff
    if role not in ["Admin", "Staff"]:
        role = "Staff"

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT user_id FROM users WHERE email = %s",
            (email,)
        )

        if cursor.fetchone():

            cursor.close()
            connection.close()

            flash(
                "An account with this email address already exists.",
                "error"
            )

            return redirect(url_for("index"))

        password_hash = generate_password_hash(password)

        cursor.execute("""
            INSERT INTO users
            (name, email, password_hash, role)
            VALUES (%s, %s, %s, %s)
        """, (
            name,
            email,
            password_hash,
            role
        ))

        connection.commit()

        cursor.close()
        connection.close()

        display_role = (
            "Administrator"
            if role == "Admin"
            else "Staff"
        )

        flash(
            f"New {display_role} account for {name} "
            f"created successfully.",
            "success"
        )

        return redirect(url_for("index"))

    except mysql.connector.Error as e:

        flash(
            f"Database error: {e}",
            "error"
        )

        return redirect(url_for("index"))


# =====================================================
# LOGOUT
# =====================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been successfully logged out.",
        "success"
    )

    return redirect(url_for("login"))


# =====================================================
# DASHBOARD
# =====================================================

@app.route("/")
@login_required
def index():

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Departments
        cursor.execute("""
            SELECT *
            FROM departments
            ORDER BY department_id DESC
        """)

        departments = cursor.fetchall()

        # Faculty
        cursor.execute("""
            SELECT faculty.*,
                   departments.department_name
            FROM faculty
            LEFT JOIN departments
                ON faculty.department_id =
                   departments.department_id
            ORDER BY faculty.faculty_id DESC
        """)

        faculty = cursor.fetchall()

        # Students
        cursor.execute("""
            SELECT students.*,
                   departments.department_name
            FROM students
            LEFT JOIN departments
                ON students.department_id =
                   departments.department_id
            ORDER BY students.student_id DESC
        """)

        students = cursor.fetchall()

        # Courses
        cursor.execute("""
            SELECT courses.*,
                   departments.department_name
            FROM courses
            LEFT JOIN departments
                ON courses.department_id =
                   departments.department_id
            ORDER BY courses.course_id DESC
        """)

        courses = cursor.fetchall()

        # Dashboard counts
        cursor.execute(
            "SELECT COUNT(*) AS total FROM departments"
        )
        total_departments = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT COUNT(*) AS total FROM faculty"
        )
        total_faculty = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT COUNT(*) AS total FROM students"
        )
        total_students = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT COUNT(*) AS total FROM courses"
        )
        total_courses = cursor.fetchone()["total"]

        cursor.close()
        connection.close()

        return render_template(
            "index.html",
            departments=departments,
            faculty=faculty,
            students=students,
            courses=courses,
            total_departments=total_departments,
            total_faculty=total_faculty,
            total_students=total_students,
            total_courses=total_courses
        )

    except Exception as e:

        return f"Database Error: {e}"


# =====================================================
# DEPARTMENT - ADD / UPDATE
# =====================================================

@app.route("/department/save", methods=["POST"])
@login_required
def save_department():

    department_id = request.form.get("department_id")

    name = request.form.get(
        "department_name",
        ""
    ).strip()

    code = request.form.get(
        "department_code",
        ""
    ).strip()

    hod = request.form.get(
        "hod_name",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip()

    phone = request.form.get(
        "phone",
        ""
    ).strip()

    if not name or not code:

        flash(
            "Department name and code are required.",
            "error"
        )

        return redirect(
            url_for(
                "index",
                module="departments"
            )
        )

    if not re.match(r"^\d{10}$", phone):

        flash(
            "Department phone number must contain exactly "
            "10 digits (numbers only).",
            "error"
        )

        return redirect(
            url_for(
                "index",
                module="departments"
            )
        )

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        if department_id:

            cursor.execute("""
                UPDATE departments
                SET department_name = %s,
                    department_code = %s,
                    hod_name = %s,
                    email = %s,
                    phone = %s
                WHERE department_id = %s
            """, (
                name,
                code,
                hod,
                email,
                phone,
                department_id
            ))

            flash(
                "Department updated successfully.",
                "success"
            )

        else:

            cursor.execute("""
                INSERT INTO departments
                (
                    department_name,
                    department_code,
                    hod_name,
                    email,
                    phone
                )
                VALUES (%s, %s, %s, %s, %s)
            """, (
                name,
                code,
                hod,
                email,
                phone
            ))

            flash(
                "Department added successfully.",
                "success"
            )

        connection.commit()

        cursor.close()
        connection.close()

    except mysql.connector.Error as e:

        flash(
            f"Department error: {e}",
            "error"
        )

    return redirect(
        url_for(
            "index",
            module="departments"
        )
    )


# =====================================================
# DEPARTMENT - DELETE
# ADMIN ONLY
# =====================================================

@app.route(
    "/department/delete/<int:department_id>",
    methods=["POST"]
)
@admin_required
def delete_department(department_id):

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM departments WHERE department_id = %s",
            (department_id,)
        )

        connection.commit()

        cursor.close()
        connection.close()

        flash(
            "Department deleted successfully.",
            "success"
        )

    except mysql.connector.Error:

        flash(
            "This department cannot be deleted because "
            "faculty, students, or courses are linked to it.",
            "error"
        )

    return redirect(
        url_for(
            "index",
            module="departments"
        )
    )


# =====================================================
# FACULTY - ADD / UPDATE
# =====================================================

@app.route("/faculty/save", methods=["POST"])
@login_required
def save_faculty():

    faculty_id = request.form.get("faculty_id")

    name = request.form.get(
        "faculty_name",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip()

    phone = request.form.get(
        "phone",
        ""
    ).strip()

    designation = request.form.get(
        "designation",
        ""
    ).strip()

    department_id = request.form.get(
        "department_id"
    )

    if not name or not email or not department_id:

        flash(
            "Faculty name, email and department are required.",
            "error"
        )

        return redirect(
            url_for(
                "index",
                module="faculty"
            )
        )

    if not re.match(r"^\d{10}$", phone):

        flash(
            "Faculty phone number must contain exactly "
            "10 digits (numbers only).",
            "error"
        )

        return redirect(
            url_for(
                "index",
                module="faculty"
            )
        )

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        if faculty_id:

            cursor.execute("""
                UPDATE faculty
                SET faculty_name = %s,
                    email = %s,
                    phone = %s,
                    designation = %s,
                    department_id = %s
                WHERE faculty_id = %s
            """, (
                name,
                email,
                phone,
                designation,
                department_id,
                faculty_id
            ))

            flash(
                "Faculty updated successfully.",
                "success"
            )

        else:

            cursor.execute("""
                INSERT INTO faculty
                (
                    faculty_name,
                    email,
                    phone,
                    designation,
                    department_id
                )
                VALUES (%s, %s, %s, %s, %s)
            """, (
                name,
                email,
                phone,
                designation,
                department_id
            ))

            flash(
                "Faculty added successfully.",
                "success"
            )

        connection.commit()

        cursor.close()
        connection.close()

    except mysql.connector.Error as e:

        flash(
            f"Faculty error: {e}",
            "error"
        )

    return redirect(
        url_for(
            "index",
            module="faculty"
        )
    )


# =====================================================
# FACULTY - DELETE
# ADMIN ONLY
# =====================================================

@app.route(
    "/faculty/delete/<int:faculty_id>",
    methods=["POST"]
)
@admin_required
def delete_faculty(faculty_id):

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM faculty WHERE faculty_id = %s",
            (faculty_id,)
        )

        connection.commit()

        cursor.close()
        connection.close()

        flash(
            "Faculty deleted successfully.",
            "success"
        )

    except mysql.connector.Error as e:

        flash(
            f"Delete error: {e}",
            "error"
        )

    return redirect(
        url_for(
            "index",
            module="faculty"
        )
    )


# =====================================================
# STUDENT - ADD / UPDATE
# =====================================================

@app.route("/student/save", methods=["POST"])
@login_required
def save_student():

    student_id = request.form.get("student_id")

    name = request.form.get(
        "student_name",
        ""
    ).strip()

    roll_number = request.form.get(
        "roll_number",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip()

    phone = request.form.get(
        "phone",
        ""
    ).strip()

    year = request.form.get(
        "year"
    )

    department_id = request.form.get(
        "department_id"
    )

    if (
        not name
        or not roll_number
        or not year
        or not department_id
    ):

        flash(
            "Student name, roll number, year and "
            "department are required.",
            "error"
        )

        return redirect(
            url_for(
                "index",
                module="students"
            )
        )

    if not re.match(r"^\d{10}$", phone):

        flash(
            "Student phone number must contain exactly "
            "10 digits (numbers only).",
            "error"
        )

        return redirect(
            url_for(
                "index",
                module="students"
            )
        )

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        if student_id:

            cursor.execute("""
                UPDATE students
                SET student_name = %s,
                    roll_number = %s,
                    email = %s,
                    phone = %s,
                    year = %s,
                    department_id = %s
                WHERE student_id = %s
            """, (
                name,
                roll_number,
                email,
                phone,
                year,
                department_id,
                student_id
            ))

            flash(
                "Student updated successfully.",
                "success"
            )

        else:

            cursor.execute("""
                INSERT INTO students
                (
                    student_name,
                    roll_number,
                    email,
                    phone,
                    year,
                    department_id
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                name,
                roll_number,
                email,
                phone,
                year,
                department_id
            ))

            flash(
                "Student added successfully.",
                "success"
            )

        connection.commit()

        cursor.close()
        connection.close()

    except mysql.connector.Error as e:

        flash(
            f"Student error: {e}",
            "error"
        )

    return redirect(
        url_for(
            "index",
            module="students"
        )
    )


# =====================================================
# STUDENT - DELETE
# ADMIN ONLY
# =====================================================

@app.route(
    "/student/delete/<int:student_id>",
    methods=["POST"]
)
@admin_required
def delete_student(student_id):

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM students WHERE student_id = %s",
            (student_id,)
        )

        connection.commit()

        cursor.close()
        connection.close()

        flash(
            "Student deleted successfully.",
            "success"
        )

    except mysql.connector.Error as e:

        flash(
            f"Delete error: {e}",
            "error"
        )

    return redirect(
        url_for(
            "index",
            module="students"
        )
    )


# =====================================================
# COURSE - ADD / UPDATE
# =====================================================

@app.route("/course/save", methods=["POST"])
@login_required
def save_course():

    course_id = request.form.get("course_id")

    name = request.form.get(
        "course_name",
        ""
    ).strip()

    code = request.form.get(
        "course_code",
        ""
    ).strip()

    credits = request.form.get(
        "credits"
    )

    department_id = request.form.get(
        "department_id"
    )

    if (
        not name
        or not code
        or not credits
        or not department_id
    ):

        flash(
            "Course name, code, credits and "
            "department are required.",
            "error"
        )

        return redirect(
            url_for(
                "index",
                module="courses"
            )
        )

    try:

        credits_val = int(credits)

        if (
            credits_val < 1
            or credits_val > 6
            or str(credits_val) != str(credits).strip()
        ):

            flash(
                "Course credits must be an integer "
                "between 1 and 6.",
                "error"
            )

            return redirect(
                url_for(
                    "index",
                    module="courses"
                )
            )

        credits = credits_val

    except (ValueError, TypeError):

        flash(
            "Course credits must be a valid integer "
            "between 1 and 6.",
            "error"
        )

        return redirect(
            url_for(
                "index",
                module="courses"
            )
        )

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        if course_id:

            cursor.execute("""
                UPDATE courses
                SET course_name = %s,
                    course_code = %s,
                    credits = %s,
                    department_id = %s
                WHERE course_id = %s
            """, (
                name,
                code,
                credits,
                department_id,
                course_id
            ))

            flash(
                "Course updated successfully.",
                "success"
            )

        else:

            cursor.execute("""
                INSERT INTO courses
                (
                    course_name,
                    course_code,
                    credits,
                    department_id
                )
                VALUES (%s, %s, %s, %s)
            """, (
                name,
                code,
                credits,
                department_id
            ))

            flash(
                "Course added successfully.",
                "success"
            )

        connection.commit()

        cursor.close()
        connection.close()

    except mysql.connector.Error as e:

        flash(
            f"Course error: {e}",
            "error"
        )

    return redirect(
        url_for(
            "index",
            module="courses"
        )
    )


# =====================================================
# COURSE - DELETE
# ADMIN ONLY
# =====================================================

@app.route(
    "/course/delete/<int:course_id>",
    methods=["POST"]
)
@admin_required
def delete_course(course_id):

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM courses WHERE course_id = %s",
            (course_id,)
        )

        connection.commit()

        cursor.close()
        connection.close()

        flash(
            "Course deleted successfully.",
            "success"
        )

    except mysql.connector.Error as e:

        flash(
            f"Delete error: {e}",
            "error"
        )

    return redirect(
        url_for(
            "index",
            module="courses"
        )
    )


# =====================================================
# RUN APPLICATION
# =====================================================

if __name__ == "__main__":
    init_db()

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
