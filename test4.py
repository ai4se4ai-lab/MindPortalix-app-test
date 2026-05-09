from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route('/check')
def check():
    target = request.args.get('target')

    result = subprocess.getoutput(f"traceroute {target}")

    return f"<pre>{result}</pre>"

if __name__ == '__main__':
    app.run(port=8080)