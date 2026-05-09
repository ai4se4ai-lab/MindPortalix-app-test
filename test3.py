import yaml
from flask import Flask, request

app = Flask(__name__)

@app.route('/import', methods=['POST'])
def import_profile():
    body = request.data.decode()

    profile = yaml.load(body, Loader=yaml.Loader)

    return {
        "loaded": str(profile)
    }

if __name__ == '__main__':
    app.run()