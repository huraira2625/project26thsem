from flask import Flask, request, redirect, url_for, render_template_string, flash
import sqlite3
from datetime import date

app = Flask(__name__)
app.secret_key = 'attendance_secret_key'

def get_db_connection():
    conn = sqlite3.connect('attendance.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return '''
        <h2>🎓 Class Attendance Management System</h2>
        <ul>
            <li><a href="/students">Manage Students</a></li>
            <li><a href="/mark">Mark Daily Attendance</a></li>
            <li><a href="/report">View Semester Attendance Report</a></li>
        </ul>
    '''

# 1. Students Route (Add & List Students)
@app.route('/students', methods=['GET', 'POST'])
def students():
    conn = get_db_connection()
    if request.method == 'POST':
        student_id = request.form['student_id']
        name = request.form['name']
        try:
            conn.execute('INSERT INTO students (student_id, name) VALUES (?, ?)', (student_id, name))
            conn.commit()
            flash('Student added successfully!', 'success')
        except sqlite3.IntegrityError:
            flash('Student ID already exists!', 'danger')
        return redirect(url_for('students'))

    student_list = conn.execute('SELECT * FROM students').fetchall()
    conn.close()

    html = '''
        <h2>Manage Students</h2>
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            <ul>{% for cat, msg in messages %}<li style="color: {% if cat=='success' %}green{% else %}red{% endif %};">{{ msg }}</li>{% endfor %}</ul>
          {% endif %}
        {% endwith %}
        <form method="POST">
            Student ID / Roll: <input type="text" name="student_id" required><br><br>
            Student Name: <input type="text" name="name" required><br><br>
            <input type="submit" value="Add Student">
        </form>
        <h3>Registered Students</h3>
        <table border="1" cellpadding="6">
            <tr><th>ID</th><th>Roll/Student ID</th><th>Name</th></tr>
            {% for s in student_list %}
            <tr><td>{{ s.id }}</td><td>{{ s.student_id }}</td><td>{{ s.name }}</td></tr>
            {% endfor %}
        </table>
        <br><a href="/">Back to Home</a>
    '''
    return render_template_string(html, student_list=student_list)

# 2. Mark Attendance Route
@app.route('/mark', methods=['GET', 'POST'])
def mark_attendance():
    conn = get_db_connection()
    if request.method == 'POST':
        attendance_date = request.form['date']
        # request.form will contain student_<id> = 'Present' or 'Absent'
        for key, value in request.form.items():
            if key.startswith('student_'):
                student_id = key.split('_')[1]
                # Check if attendance already marked for this date/student to avoid duplicates
                existing = conn.execute('SELECT * FROM attendance WHERE student_id = ? AND date = ?', (student_id, attendance_date)).fetchone()
                if existing:
                    conn.execute('UPDATE attendance SET status = ? WHERE student_id = ? AND date = ?', (value, student_id, attendance_date))
                else:
                    conn.execute('INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)', (student_id, attendance_date, value))
        conn.commit()
        conn.close()
        flash('Attendance recorded successfully!', 'success')
        return redirect(url_for('mark_attendance'))

    student_list = conn.execute('SELECT * FROM students').fetchall()
    conn.close()
    today = date.today().isoformat()

    html = '''
        <h2>Mark Daily Attendance</h2>
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            <ul>{% for cat, msg in messages %}<li style="color: green;">{{ msg }}</li>{% endfor %}</ul>
          {% endif %}
        {% endwith %}
        <form method="POST">
            Date: <input type="date" name="date" value="'''+today+'''" required><br><br>
            <table border="1" cellpadding="6">
                <tr><th>Roll/ID</th><th>Name</th><th>Attendance Status</th></tr>
                {% for s in student_list %}
                <tr>
                    <td>{{ s.student_id }}</td>
                    <td>{{ s.name }}</td>
                    <td>
                        <label><input type="radio" name="student_{{ s.id }}" value="Present" checked> Present</label>
                        <label><input type="radio" name="student_{{ s.id }}" value="Absent"> Absent</label>
                    </td>
                </tr>
                {% endfor %}
            </table>
            <br>
            <input type="submit" value="Save Attendance">
        </form>
        <br><a href="/">Back to Home</a>
    '''
    return render_template_string(html, student_list=student_list)

# 3. Semester Attendance Report Route
@app.route('/report')
def report():
    conn = get_db_connection()
    # Calculate total distinct classes held, and classes attended per student
    report_data = conn.execute('''
        SELECT s.student_id, s.name,
               COUNT(a.id) as total_classes,
               SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) as present_count
        FROM students s
        LEFT JOIN attendance a ON s.id = a.student_id
        GROUP BY s.id
    ''').fetchall()
    conn.close()

    html = '''
        <h2>📊 Semester Attendance Report</h2>
        <table border="1" cellpadding="8">
            <tr>
                <th>Student ID</th>
                <th>Name</th>
                <th>Total Classes</th>
                <th>Classes Attended</th>
                <th>Attendance Percentage</th>
            </tr>
            {% for row in report_data %}
                {% set total = row.total_classes if row.total_classes > 0 else 1 %}
                {% set present = row.present_count if row.present_count else 0 %}
                {% set percentage = (present / total) * 100 %}
            <tr>
                <td>{{ row.student_id }}</td>
                <td>{{ row.name }}</td>
                <td>{{ row.total_classes }}</td>
                <td>{{ present }}</td>
                <td>
                    <span style="color: {% if percentage >= 75 %}green{% else %}red{% endif %}; font-weight: bold;">
                        {{ "%.2f"|format(percentage) }}%
                    </span>
                </td>
            </tr>
            {% endfor %}
        </table>
        <br><a href="/">Back to Home</a>
    '''
    return render_template_string(html, report_data=report_data)

if __name__ == '__main__':
    app.run(debug=True)