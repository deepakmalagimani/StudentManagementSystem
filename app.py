from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)

# Secret key for flash messages
app.secret_key = "student-management-secret"

DATABASE = "students.db"


# -------------------------------
# Database Connection
# -------------------------------

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# -------------------------------
# Create Students Table
# -------------------------------

def create_table():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            usn TEXT NOT NULL UNIQUE,
            branch TEXT NOT NULL,
            semester INTEGER NOT NULL,
            marks REAL NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# -------------------------------
# Home Page
# -------------------------------

@app.route("/")
def home():

    conn = get_db_connection()

    total_students = conn.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        total_students=total_students
    )


# -------------------------------
# Add Student
# -------------------------------

@app.route("/add", methods=["GET", "POST"])
def add_student():

    if request.method == "POST":

        name = request.form["name"]
        usn = request.form["usn"]
        branch = request.form["branch"]
        semester = request.form["semester"]
        marks = request.form["marks"]

        conn = get_db_connection()

        try:

            conn.execute("""
                INSERT INTO students
                (name, usn, branch, semester, marks)
                VALUES (?, ?, ?, ?, ?)
            """, (name, usn, branch, semester, marks))

            conn.commit()

            flash("Student added successfully!", "success")

        except sqlite3.IntegrityError:

            flash("USN already exists!", "error")

            conn.close()

            return redirect(url_for("add_student"))

        conn.close()

        return redirect(url_for("view_students"))

    return render_template("add_student.html")


# -------------------------------
# View Students
# -------------------------------

@app.route("/students")
def view_students():

    conn = get_db_connection()

    students = conn.execute(
        "SELECT * FROM students"
    ).fetchall()

    conn.close()

    return render_template(
        "view_students.html",
        students=students
    )


# -------------------------------
# Edit Student
# -------------------------------

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_student(id):

    conn = get_db_connection()

    if request.method == "POST":

        name = request.form["name"]
        usn = request.form["usn"]
        branch = request.form["branch"]
        semester = request.form["semester"]
        marks = request.form["marks"]

        try:

            conn.execute("""
                UPDATE students
                SET name = ?,
                    usn = ?,
                    branch = ?,
                    semester = ?,
                    marks = ?
                WHERE id = ?
            """, (name, usn, branch, semester, marks, id))

            conn.commit()

            flash("Student updated successfully!", "success")

        except sqlite3.IntegrityError:

            flash("USN already exists!", "error")

            conn.close()

            return redirect(url_for("edit_student", id=id))

        conn.close()

        return redirect(url_for("view_students"))

    student = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (id,)
    ).fetchone()

    conn.close()

    return render_template(
        "edit_student.html",
        student=student
    )


# -------------------------------
# Delete Student
# -------------------------------

@app.route("/delete/<int:id>")
def delete_student(id):

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM students WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    flash("Student deleted successfully!", "success")

    return redirect(url_for("view_students"))


# -------------------------------
# Search Student
# -------------------------------

@app.route("/search", methods=["GET", "POST"])
def search():

    students = []

    if request.method == "POST":

        keyword = request.form["keyword"]

        conn = get_db_connection()

        students = conn.execute("""
            SELECT * FROM students
            WHERE name LIKE ?
            OR usn LIKE ?
        """, (
            f"%{keyword}%",
            f"%{keyword}%"
        )).fetchall()

        conn.close()

    return render_template(
        "search.html",
        students=students
    )


# -------------------------------
# Run Application
# -------------------------------

create_table()

if __name__ == "__main__":
    app.run(debug=True)