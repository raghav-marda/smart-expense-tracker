from flask import Flask, render_template, request, jsonify, redirect, session, flash
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------------- DB CONNECTION ----------------
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)


# ---------------- DB INIT ----------------
def init_db():
    conn = get_db_connection()
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id SERIAL PRIMARY KEY,
            user_id TEXT,
            name TEXT,
            amount INTEGER,
            category TEXT,
            date DATE
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
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

        conn = get_db_connection()
        c = conn.cursor()

        if action == "signup":
            try:
                c.execute(
                    "INSERT INTO users (username, password) VALUES (%s, %s)",
                    (username, password)
                )
                conn.commit()
                session['user'] = username
                flash("Signup successful 🎉", "success")
                return redirect('/home')
            except:
                flash("User already exists ❌", "error")

        elif action == "login":
            c.execute(
                "SELECT * FROM users WHERE username=%s AND password=%s",
                (username, password)
            )
            user = c.fetchone()

            if user:
                session['user'] = username
                flash("Login successful ✅", "success")
                return redirect('/home')
            else:
                flash("Invalid credentials ❌", "error")

        conn.close()

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

    today = datetime.now().date()

    conn = get_db_connection()
    c = conn.cursor()

    c.execute(
        "INSERT INTO expenses (user_id, name, amount, category, date) VALUES (%s, %s, %s, %s, %s)",
        (user, name, amount, category, today)
    )

    conn.commit()
    conn.close()

    return jsonify({'status': 'success'})


# 📥 GET
@app.route('/get')
def get_expenses():
    user = session.get('user')
    month = request.args.get('month')

    conn = get_db_connection()
    c = conn.cursor()

    if month:
        c.execute("""
            SELECT * FROM expenses 
            WHERE user_id=%s AND EXTRACT(MONTH FROM date)=%s
        """, (user, int(month)))
    else:
        c.execute("SELECT * FROM expenses WHERE user_id=%s", (user,))

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

    conn = get_db_connection()
    c = conn.cursor()

    c.execute(
        "DELETE FROM expenses WHERE id=%s AND user_id=%s",
        (id, user)
    )

    conn.commit()
    conn.close()

    return jsonify({'status': 'deleted'})


# ✏️ EDIT
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

    conn = get_db_connection()
    c = conn.cursor()

    c.execute("""
        UPDATE expenses 
        SET name=%s, amount=%s, category=%s 
        WHERE id=%s AND user_id=%s
    """, (name, amount, category, id, user))

    conn.commit()
    conn.close()

    return jsonify({'status': 'updated'})


# 📊 MONTHLY SUMMARY
@app.route('/monthly-summary')
def monthly_summary():
    user = session.get('user')

    conn = get_db_connection()
    c = conn.cursor()

    c.execute("""
        SELECT EXTRACT(MONTH FROM date), SUM(amount)
        FROM expenses
        WHERE user_id=%s
        GROUP BY EXTRACT(MONTH FROM date)
        ORDER BY EXTRACT(MONTH FROM date)
    """, (user,))

    data = c.fetchall()
    conn.close()

    result = {}
    for row in data:
        result[str(int(row[0])).zfill(2)] = row[1]

    return jsonify(result)


# 📥 EXPORT CSV
@app.route('/export')
def export_data():
    user = session.get('user')

    conn = get_db_connection()
    c = conn.cursor()

    c.execute(
        "SELECT name, amount, category, date FROM expenses WHERE user_id=%s",
        (user,)
    )
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