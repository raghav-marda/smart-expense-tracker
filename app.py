from flask import Flask, render_template, request, jsonify, redirect, session, flash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------------- DB INIT ----------------
def init_db():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            name TEXT,
            amount INTEGER,
            category TEXT,
            date TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# ---------------- ROUTES ----------------

@app.route('/')
def root():
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')
        action = request.form.get('action')

        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()

        if action == "signup":
            try:
                c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                session['user'] = username
                flash("Signup successful 🎉", "success")
                return redirect('/home')
            except:
                flash("User already exists ❌", "error")

        elif action == "login":
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = c.fetchone()
            conn.close()

            if user:
                session['user'] = username
                flash("Login successful ✅", "success")
                return redirect('/home')
            else:
                flash("Invalid credentials ❌", "error")

    return render_template('login.html')


@app.route('/home')
def home():
    if 'user' not in session:
        return redirect('/login')
    return render_template('index.html', user=session['user'])


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully 👋", "success")
    return redirect('/login')


# ---------------- EXPENSE ----------------

# ➕ ADD
@app.route('/add', methods=['POST'])
def add_expense():
    data = request.get_json()

    name = data.get('name')
    amount = data.get('amount')
    category = data.get('category')
    user = session.get('user')

    today = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()

    c.execute(
        "INSERT INTO expenses (user_id, name, amount, category, date) VALUES (?, ?, ?, ?, ?)",
        (user, name, amount, category, today)
    )

    conn.commit()
    conn.close()

    return jsonify({'status': 'success'})


# 📥 GET (WITH MONTH FILTER + CATEGORY FIX)
@app.route('/get')
def get_expenses():
    user = session.get('user')
    month = request.args.get('month')

    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()

    if month:
        c.execute("""
            SELECT * FROM expenses 
            WHERE user_id=? AND strftime('%m', date)=?
        """, (user, month))
    else:
        c.execute("SELECT * FROM expenses WHERE user_id=?", (user,))

    data = c.fetchall()
    conn.close()

    valid_categories = ["Food", "Travel", "Shopping", "Other"]

    expenses = []
    for row in data:
        category = row[4] if row[4] in valid_categories else "Other"

        expenses.append({
            'id': row[0],
            'name': row[2],
            'amount': row[3],
            'category': category
        })

    return jsonify(expenses)


# ❌ DELETE
@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_expense(id):
    user = session.get('user')

    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()

    c.execute("DELETE FROM expenses WHERE id=? AND user_id=?", (id, user))

    conn.commit()
    conn.close()

    return jsonify({'status': 'deleted'})


# ✏️ EDIT (WITH CATEGORY FIX)
@app.route('/edit/<int:id>', methods=['PUT'])
def edit_expense(id):
    user = session.get('user')
    data = request.get_json()

    name = data.get('name')
    amount = data.get('amount')
    category = data.get('category')

    valid_categories = ["Food", "Travel", "Shopping", "Other"]
    if category not in valid_categories:
        category = "Other"

    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()

    c.execute("""
        UPDATE expenses 
        SET name=?, amount=?, category=? 
        WHERE id=? AND user_id=?
    """, (name, amount, category, id, user))

    conn.commit()
    conn.close()

    return jsonify({'status': 'updated'})


# 📊 MONTHLY SUMMARY (FIXED LINE CHART)
@app.route('/monthly-summary')
def monthly_summary():
    user = session.get('user')

    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()

    c.execute("""
        SELECT strftime('%m', date), SUM(amount)
        FROM expenses
        WHERE user_id=?
        GROUP BY strftime('%m', date)
        ORDER BY strftime('%m', date)
    """, (user,))

    data = c.fetchall()
    conn.close()

    result = {}
    for row in data:
        result[row[0]] = row[1]

    return jsonify(result)


# 📥 EXPORT CSV
@app.route('/export')
def export_data():
    user = session.get('user')

    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()

    c.execute("SELECT name, amount, category, date FROM expenses WHERE user_id=?", (user,))
    data = c.fetchall()
    conn.close()

    content = "Name,Amount,Category,Date\n"
    for row in data:
        content += f"{row[0]},{row[1]},{row[2]},{row[3]}\n"

    return content, 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': 'attachment; filename=expenses.csv'
    }


# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))