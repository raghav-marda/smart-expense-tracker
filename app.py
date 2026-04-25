from flask import Flask, render_template, request, jsonify, redirect, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"

# DB INIT
def init_db():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            amount INTEGER,
            category TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# ROOT
@app.route('/')
def root():
    return redirect('/login')

# LOGIN / SIGNUP
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')
        action = request.form.get('action')

        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()

        if action == "signup":
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()

            flash("Signup successful 🎉", "success")
            session['user'] = username
            return redirect('/home')

        elif action == "login":
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = c.fetchone()
            conn.close()

            if user:
                flash("Login successful ✅", "success")
                session['user'] = username
                return redirect('/home')
            else:
                flash("Invalid credentials ❌", "error")

    return render_template('login.html')

# HOME
@app.route('/home')
def home():
    if 'user' not in session:
        return redirect('/login')
    return render_template('index.html', user=session['user'])

# LOGOUT
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully 👋", "success")
    return redirect('/login')

# ADD EXPENSE
@app.route('/add', methods=['POST'])
def add_expense():
    data = request.json
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()

    c.execute("INSERT INTO expenses (name, amount, category) VALUES (?, ?, ?)",
              (data['name'], data['amount'], data['category']))
    conn.commit()
    conn.close()

    return jsonify({'status': 'success'})

# GET EXPENSES
@app.route('/get')
def get_expenses():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("SELECT * FROM expenses")
    data = c.fetchall()
    conn.close()

    expenses = []
    for row in data:
        expenses.append({
            'id': row[0],
            'name': row[1],
            'amount': row[2],
            'category': row[3]
        })

    return jsonify(expenses)

# DELETE
@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_expense(id):
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("DELETE FROM expenses WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'deleted'})

if __name__ == '__main__':
    app.run(debug=True)