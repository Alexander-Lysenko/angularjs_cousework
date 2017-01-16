from flask import Flask, render_template, request, jsonify, escape, redirect
app = Flask(__name__)
app.debug = True


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        return request.get_json()
    return render_template('signup.html')


@app.route("/login")
def login():
    return render_template('login.html')


@app.route("/profile", methods=['GET', 'POST'])
def profile():
    return render_template('profile.html')


@app.route("/edit")
def edit():
    return render_template('edit.html')

if __name__ == "__main__":
    app.run()
