import os
import requests
from flask import Flask, request

app = Flask(__name__)

SERVICE_TOKEN = "prod-access-token-93A1"

@app.route('/fetch')
def fetch():
    endpoint = request.args.get('endpoint')

    response = requests.get(endpoint, timeout=3)

    return {
        "status": response.status_code,
        "data": response.text[:200]
    }

@app.route('/config')
def config():
    return {
        "token": SERVICE_TOKEN,
        "home": os.environ.get('HOME')
    }

if __name__ == '__main__':
    app.run()
    print("Server started on port 5030")