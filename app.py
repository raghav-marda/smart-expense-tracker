from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATABASE = 'expenses.db'


# ---------------- DATABASE ---------------- #
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')

    # EXPENSES TABLE
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            amount REAL,
            category TEXT,
            date TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()


init_db()


# ---------------- LOGIN ---------------- #
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        action = request.form.get('action')

        conn = get_db()
        cursor = conn.cursor()

        if action == 'signup':
            try:
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, password)
                )
                conn.commit()
                flash("Signup successful 🎉 Please login.", "success")
            except:
                flash("User already exists!", "error")

        elif action == 'login':
            cursor.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (username, password)
            )
            user = cursor.fetchone()

            if user:
                session['user_id'] = user['id']
                session['username'] = user['username']
                return redirect(url_for('home'))
            else:
                flash("Invalid credentials!", "error")

        conn.close()

    return render_template('login.html')


# ---------------- HOME ---------------- #
@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM expenses WHERE user_id=?",
        (session['user_id'],)
    )
    expenses = cursor.fetchall()

    # TOTAL
    total = sum(exp['amount'] for exp in expenses)

    # CATEGORY TOTALS (FOR CHART)
    food_total = sum(exp['amount'] for exp in expenses if exp['category'] == 'Food')
    travel_total = sum(exp['amount'] for exp in expenses if exp['category'] == 'Travel')
    shopping_total = sum(exp['amount'] for exp in expenses if exp['category'] == 'Shopping')
    other_total = sum(exp['amount'] for exp in expenses if exp['category'] == 'Other')

    conn.close()

    return render_template(
        'index.html',
        expenses=expenses,
        total=total,
        user=session['username'],
        food_total=food_total,
        travel_total=travel_total,
        shopping_total=shopping_total,
        other_total=other_total
    )


# ---------------- ADD EXPENSE ---------------- #
@app.route('/add', methods=['POST'])
def add_expense():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    title = request.form['name']  # MATCHES HTML
    amount = float(request.form['amount'])
    category = request.form['category']

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO expenses (user_id, title, amount, category, date)
        VALUES (?, ?, ?, ?, date('now'))
    ''', (session['user_id'], title, amount, category))

    conn.commit()
    conn.close()

    flash("Expense Added Successfully!", "success")

    return redirect(url_for('home'))


# ---------------- DELETE EXPENSE ---------------- #
@app.route('/delete/<int:id>')
def delete_expense(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM expenses WHERE id=?", (id,))
    conn.commit()
    conn.close()

    flash("Expense Deleted!", "success")

    return redirect(url_for('home'))


# ---------------- LOGOUT ---------------- #
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ---------------- RUN APP (DEPLOY READY) ---------------- #
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))