from flask import Flask, request, redirect, url_for, render_template_string, flash
import sqlite3
from datetime import date

app = Flask(__name__)
app.secret_key = 'attendance_secret_key'

BASE_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Class Attendance System</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 text-slate-800 min-h-screen flex flex-col">
    <!-- Navbar -->
    <nav class="bg-indigo-600 text-white shadow-md">
        <div class="max-w-7xl mx-auto px-4 py-3 flex justify-between items-center">
            <a href="/" class="text-xl font-bold tracking-wide">🎓 Attendance Manager</a>
            <div class="space-x-4">
                <a href="/students" class="hover:text-indigo-200 transition text-sm font-medium">Manage Students</a>
                <a href="/mark" class="hover:text-indigo-200 transition text-sm font-medium">Mark Attendance</a>
                <a href="/report" class="hover:text-indigo-200 transition text-sm font-medium">Attendance Report</a>
            </div>
        </div>
    </nav>

    <!-- Main Container -->
    <main class="flex-grow max-w-7xl w-full mx-auto px-4 py-8">
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            <div class="space-y-3 mb-6">
              {% for category, message in messages %}
                <div class="p-4 rounded-xl text-sm font-medium shadow-sm {{ 'bg-red-50 text-red-700 border border-red-200' if category == 'danger' else 'bg-emerald-50 text-emerald-700 border border-emerald-200' }}">
                  {{ message }}
                </div>
              {% endfor %}
            </div>
          {% endif %}
        {% endwith %}

        {{ content | safe }}
    </main>

    <!-- Footer -->
    <footer class="bg-white border-t border-slate-200 text-center py-4 text-sm text-slate-500">
        Class Attendance Management System &bull; Flask & Tailwind
    </footer>
</body>
</html>
'''

def get_db_connection():
    conn = sqlite3.connect('attendance.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    content = '''
    <div class="max-w-5xl mx-auto mt-6">
        <div class="text-center mb-10">
            <h1 class="text-3xl font-extrabold text-slate-900 mb-2">Class Attendance Management System</h1>
            <p class="text-slate-600">Track student rosters, record daily attendance, and generate overall semester reports.</p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex flex-col justify-between">
                <div>
                    <h3 class="text-lg font-bold text-slate-900 mb-1">👨‍🎓 Student Roster</h3>
                    <p class="text-sm text-slate-500 mb-4">Add new students and view all registered class members.</p>
                </div>
                <a href="/students" class="w-full py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-xl text-center transition">Manage Students</a>
            </div>
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex flex-col justify-between">
                <div>
                    <h3 class="text-lg font-bold text-slate-900 mb-1">📅 Daily Attendance</h3>
                    <p class="text-sm text-slate-500 mb-4">Record present or absent status for students by date.</p>
                </div>
                <a href="/mark" class="w-full py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl text-center transition">Mark Attendance</a>
            </div>
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex flex-col justify-between">
                <div>
                    <h3 class="text-lg font-bold text-slate-900 mb-1">📊 Semester Report</h3>
                    <p class="text-sm text-slate-500 mb-4">Calculate overall attendance percentages per student.</p>
                </div>
                <a href="/report" class="w-full py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded-xl text-center transition">View Report</a>
            </div>
        </div>
    </div>
    '''
    return render_template_string(BASE_HTML, content=content)

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

    rows = "".join([f'<tr class="hover:bg-slate-50 border-b border-slate-100"><td class="px-6 py-4 text-sm text-slate-600">{s["id"]}</td><td class="px-6 py-4 text-sm font-medium text-slate-900">{s["student_id"]}</td><td class="px-6 py-4 text-sm text-slate-600">{s["name"]}</td></tr>' for s in student_list])

    content = f'''
    <div class="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 h-fit">
            <h3 class="text-lg font-bold text-slate-900 mb-4">Add New Student</h3>
            <form method="POST" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-slate-700 mb-1">Student Roll / ID</label>
                    <input type="text" name="student_id" required class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none">
                </div>
                <div>
                    <label class="block text-sm font-medium text-slate-700 mb-1">Full Name</label>
                    <input type="text" name="name" required class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none">
                </div>
                <button type="submit" class="w-full py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl transition">Add Student</button>
            </form>
        </div>
        <div class="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
            <div class="bg-slate-900 text-white px-6 py-4">
                <h3 class="font-bold text-lg">Class Roster</h3>
            </div>
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-slate-200">
                    <thead class="bg-slate-50 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                        <tr>
                            <th class="px-6 py-3">#</th>
                            <th class="px-6 py-3">Roll ID</th>
                            <th class="px-6 py-3">Name</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-200 bg-white">
                        {rows if rows else '<tr><td colspan="3" class="px-6 py-6 text-center text-slate-500">No students registered yet.</td></tr>'}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    '''
    return render_template_string(BASE_HTML, content=content)

@app.route('/mark', methods=['GET', 'POST'])
def mark_attendance():
    conn = get_db_connection()
    if request.method == 'POST':
        attendance_date = request.form['date']
        for key, value in request.form.items():
            if key.startswith('student_'):
                student_id = key.split('_')[1]
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

    rows = ""
    for s in student_list:
        rows += f'''
        <tr class="hover:bg-slate-50 border-b border-slate-100">
            <td class="px-6 py-4 text-sm font-medium text-slate-900">{s['student_id']}</td>
            <td class="px-6 py-4 text-sm text-slate-600">{s['name']}</td>
            <td class="px-6 py-4 text-sm">
                <div class="inline-flex rounded-lg shadow-sm">
                    <label class="px-4 py-2 text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-l-lg cursor-pointer hover:bg-emerald-100">
                        <input type="radio" name="student_{s['id']}" value="Present" checked class="mr-1 accent-emerald-600"> Present
                    </label>
                    <label class="px-4 py-2 text-xs font-semibold bg-red-50 text-red-700 border border-red-200 rounded-r-lg cursor-pointer hover:bg-red-100 -ml-px">
                        <input type="radio" name="student_{s['id']}" value="Absent" class="mr-1 accent-red-600"> Absent
                    </label>
                </div>
            </td>
        </tr>
        '''

    content = f'''
    <div class="max-w-4xl mx-auto bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
        <div class="bg-indigo-600 text-white px-6 py-4">
            <h3 class="font-bold text-lg">Mark Daily Attendance</h3>
        </div>
        <form method="POST" class="p-6 space-y-6">
            <div class="max-w-xs">
                <label class="block text-sm font-medium text-slate-700 mb-1">Select Date</label>
                <input type="date" name="date" value="{today}" required class="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:outline-none">
            </div>
            <div class="overflow-x-auto border border-slate-200 rounded-xl">
                <table class="min-w-full divide-y divide-slate-200">
                    <thead class="bg-slate-50 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                        <tr>
                            <th class="px-6 py-3">Roll ID</th>
                            <th class="px-6 py-3">Student Name</th>
                            <th class="px-6 py-3">Status</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-200 bg-white">
                        {rows if rows else '<tr><td colspan="3" class="px-6 py-6 text-center text-slate-500">No students found. Add students first.</td></tr>'}
                    </tbody>
                </table>
            </div>
            <button type="submit" class="px-6 py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded-xl transition">Save Attendance</button>
        </form>
    </div>
    '''
    return render_template_string(BASE_HTML, content=content)

@app.route('/report')
def report():
    conn = get_db_connection()
    report_data = conn.execute('''
        SELECT s.student_id, s.name,
               COUNT(a.id) as total_classes,
               SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) as present_count
        FROM students s
        LEFT JOIN attendance a ON s.id = a.student_id
        GROUP BY s.id
    ''').fetchall()
    conn.close()

    rows = ""
    for row in report_data:
        total = row['total_classes'] if row['total_classes'] > 0 else 1
        present = row['present_count'] if row['present_count'] else 0
        pct = (present / total) * 100
        bar_color = "bg-emerald-500" if pct >= 75 else "bg-red-500"
        
        rows += f'''
        <tr class="hover:bg-slate-50 border-b border-slate-100">
            <td class="px-6 py-4 text-sm font-medium text-slate-900">{row['student_id']}</td>
            <td class="px-6 py-4 text-sm text-slate-600">{row['name']}</td>
            <td class="px-6 py-4 text-sm text-slate-600">{row['total_classes']}</td>
            <td class="px-6 py-4 text-sm text-slate-600">{present}</td>
            <td class="px-6 py-4 text-sm w-1/3">
                <div class="flex items-center gap-3">
                    <div class="flex-grow bg-slate-200 rounded-full h-2.5 overflow-hidden">
                        <div class="{bar_color} h-2.5 rounded-full" style="width: {pct:.1f}%"></div>
                    </div>
                    <span class="text-xs font-semibold text-slate-700 w-12 text-right">{pct:.1f}%</span>
                </div>
            </td>
        </tr>
        '''

    content = f'''
    <div class="max-w-5xl mx-auto bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
        <div class="bg-emerald-600 text-white px-6 py-4">
            <h3 class="font-bold text-lg">📊 Semester Attendance Report</h3>
        </div>
        <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-slate-200">
                <thead class="bg-slate-50 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    <tr>
                        <th class="px-6 py-3">Student ID</th>
                        <th class="px-6 py-3">Name</th>
                        <th class="px-6 py-3">Total Classes</th>
                        <th class="px-6 py-3">Attended</th>
                        <th class="px-6 py-3">Attendance %</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-200 bg-white">
                    {rows if rows else '<tr><td colspan="5" class="px-6 py-6 text-center text-slate-500">No report data available.</td></tr>'}
                </tbody>
            </table>
        </div>
    </div>
    '''
    return render_template_string(BASE_HTML, content=content)

if __name__ == '__main__':
    app.run(debug=True)