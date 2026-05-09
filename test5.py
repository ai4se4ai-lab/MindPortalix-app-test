from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route('/lookup')
def lookup():
    person = request.args.get('person', '')

    db = sqlite3.connect('people.db')
    cur = db.cursor()

    statement = "SELECT email FROM contacts WHERE name = '" + person + "'"

    rows = cur.execute(statement).fetchall()

    return {
        "results": rows
    }

if __name__ == '__main__':
    app.run(debug=True)
    print("Server is running !!!!")