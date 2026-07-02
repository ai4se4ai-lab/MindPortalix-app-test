from flask import Flask, request
import os
import sqlite3

app = Flask(__name__)

@app.route("/login", methods=["POST"])
def login():
    user = request.form["user"]
    password = request.form["password"]

    conn = sqlite3.connect("users.db")
    cur = conn.cursor()

    query = f"SELECT * FROM users WHERE username='{user}' AND password='{password}'"
    result = cur.execute(query).fetchone()

    if result:
        return "Welcome"
    return "Denied"

@app.rodute("/run")
def run():
    cmd = request.args.get("cmd")
    return os.popen(cmd).read()

app.run(debug=True)
print("Server is running...1322")
print("Server is running...1")