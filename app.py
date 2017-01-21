from flask import Flask, render_template, request, jsonify, escape, redirect, make_response
import random, sqlite3
app = Flask(__name__)
app.debug = True


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/api/login", methods=['POST'])
def api_login():
    auth = request.get_json()
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    username = c.execute('''SELECT user_name FROM users WHERE user_name = :us;''',
                         {'us': auth['username']}).fetchone()
    if username is not None:
        return 'OK'
    else:
        return 'Fail'


@app.route("/api/signup", methods=['POST'])
def api_signup():
    userdata = request.get_json()
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    username = c.execute('''SELECT user_name FROM users WHERE user_name = :us;''',
                         {'us': userdata['user_name']}).fetchone()
    if username is not None:
        return 'Fail'
    else:
        salt = random.randrange(1, 9999)
        c = conn.cursor()
        c.execute('''INSERT INTO users(user_name, nickname, email, password, salt)
    VALUES(?, ?, ?, ?, ?);''', (userdata['user_name'], userdata['nickname'], userdata['email'], userdata['password'],
                                salt))
        conn.commit()
        conn.close()
        return 'OK'


@app.route("/api/anime/list")
def api_anime_list():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    anime = c.execute('''SELECT  id, title, title_original, series_count, strftime('%d.%m.%Y', release_date), description
    FROM anime_list ORDER BY id ASC LIMIT 50;''').fetchall()
    anime = [[a, escape(b), escape(c), d, e, escape(f)] for a, b, c, d, e, f in anime]
    return jsonify({'anime_list': anime})


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


@app.route("/api/anime/rm/<anime_id>", methods=['POST'])
def api_anime_rm(anime_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''DELETE FROM anime_list WHERE id = ?;''', anime_id)
    conn.commit()
    return 'OK'


if __name__ == "__main__":
    app.run()
