from flask import Flask, request, render_template_string

app = Flask(__name__)

PAGE = """
<html>
<body>
    <h2>Feedback</h2>
    <div>%s</div>
</body>
</html>
"""

@app.route('/feedback')
def feedback():
    text = request.args.get('text', '')

    return render_template_string(PAGE % text)

if __name__ == '__main__':
    app.run(debug=True)
    print("This is Majid Babaei IRAN!")