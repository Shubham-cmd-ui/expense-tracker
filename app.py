from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            note TEXT
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/add", methods=["GET", "POST"])
def add_expense():
    if request.method == "POST":
        amount = request.form["amount"]
        category = request.form["category"]
        date = request.form["date"]
        note = request.form["note"]

        conn = get_db()
        conn.execute(
            "INSERT INTO expenses (amount, category, date, note) VALUES (?, ?, ?, ?)",
            (amount, category, date, note)
        )
        conn.commit()
        conn.close()
        return redirect("/expenses")
    return render_template("add_expense.html")

@app.route("/expenses")
def expenses():
    conn = get_db()
    all_expenses = conn.execute("SELECT * FROM expenses ORDER BY date DESC").fetchall()
    total = conn.execute("SELECT SUM(amount) FROM expenses").fetchone()[0] or 0
    conn.close()
    return render_template("expenses.html", expenses=all_expenses, total=total)

@app.route("/delete/<int:id>")
def delete_expense(id):
    conn = get_db()
    conn.execute("DELETE FROM expenses WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/expenses")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_expense(id):
    conn = get_db()
    if request.method == "POST":
        amount = request.form["amount"]
        category = request.form["category"]
        date = request.form["date"]
        note = request.form["note"]
        conn.execute(
            "UPDATE expenses SET amount = ?, category = ?, date = ?, note = ? WHERE id = ?",
            (amount, category, date, note, id)
        )
        conn.commit()
        conn.close()
        return redirect("/expenses")
    expense = conn.execute("SELECT * FROM expenses WHERE id = ?", (id,)).fetchone()
    conn.close()
    return render_template("edit_expense.html", expense=expense)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)