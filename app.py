from flask import Flask, render_template, request, redirect, url_for
import sqlite3, os, qrcode
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "static/uploads"
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs("static/qrcodes", exist_ok=True)

# Initialize DB
def init_db():
    with sqlite3.connect("students.db") as con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS students
                       (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        regno TEXT UNIQUE,
                        photo TEXT)''')
        con.commit()

init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        regno = request.form["regno"]
        photo = request.files["photo"]

        filename = secure_filename(photo.filename)
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        photo.save(photo_path)

        with sqlite3.connect("students.db") as con:
            cur = con.cursor()
            cur.execute("INSERT OR REPLACE INTO students (name, regno, photo) VALUES (?,?,?)",
                        (name, regno, photo_path))
            con.commit()
        return redirect(url_for("student", regno=regno))

    return render_template("register.html")

@app.route("/student/<regno>")
def student(regno):
    with sqlite3.connect("students.db") as con:
        cur = con.cursor()
        cur.execute("SELECT name, regno, photo FROM students WHERE regno=?",(regno,))
        student = cur.fetchone()

    if not student:
        return "Student not found"

    # Generate QR code (contains regno)
    qr_path = f"static/qrcodes/{regno}.png"
    if not os.path.exists(qr_path):
        qr = qrcode.make(regno)
        qr.save(qr_path)

    return render_template("student.html", student=student, qr_path=qr_path)

@app.route("/verify/<regno>")
def verify(regno):
    with sqlite3.connect("students.db") as con:
        cur = con.cursor()
        cur.execute("SELECT name, regno, photo FROM students WHERE regno=?",(regno,))
        student = cur.fetchone()

    if not student:
        return "❌ Invalid Temporary ID"

    return render_template("student.html", student=student, qr_path=None)

@app.route("/scanner")
def scanner():
    return render_template("scanner.html")

if __name__ == "__main__":
    app.run(debug=True)
