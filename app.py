from flask import Flask, render_template, request, jsonify, escape, redirect
import sqlite3
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


@app.route("/api/anime/list")
def api_anime_list():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    anime = c.execute('''SELECT title, title_original, strftime('%d.%m.%Y %H:%M:%S', release_date), series_count, description
    FROM anime_list ORDER BY id ASC LIMIT 50;''').fetchall()
    anime = [[escape(a), escape(b), c, d, escape(e)] for a, b, c, d, e in anime]
    return jsonify(anime_list=anime)


@app.route('/api/anime/add', methods=['POST'])
def api_anime_add():
    anime = request.get_json()
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''INSERT INTO anime_list(title, title_original, release_date, series_count, description)
VALUES(?, ?, ?, ?, ?);''', (anime['title'], anime['title_original'], anime['release_date'], anime['series_count'],
                            anime['description']))
    conn.commit()
    return 'OK'


if __name__ == "__main__":
    app.run()
