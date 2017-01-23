from flask import Flask, render_template, request, jsonify, escape
import sqlite3, uuid, hashlib
app = Flask(__name__)
app.debug = True


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/api/login/verify/<name>", methods=['POST'])
def verify(name):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    username = c.execute('''SELECT nickname FROM users WHERE nickname = :name;''',
                         {'name': name}).fetchone()
    c.close()
    conn.close()
    if username is not None:
        return 'OK'
    else:
        return 'Fail'


@app.route("/api/login", methods=['POST'])
def api_login():
    auth = request.get_json()
    if verify(auth['username']) == 'OK':
        c = sqlite3.connect('database.db').cursor()
        password = c.execute('''SELECT salt, password FROM users WHERE nickname = :us;''',
                             {'us': auth['username']}).fetchone()
        if password[1] == hashlib.sha512((password[0] + auth['password']).encode('utf-8')).hexdigest():
            return 'OK'
    return 'Fail'


@app.route("/api/signup", methods=['POST'])
def api_signup():
    userdata = request.get_json()
    if verify(userdata['nickname']) == 'OK':
        return 'Fail'
    else:
        salt = str(uuid.uuid4())
        pass_hash = hashlib.sha512((salt + userdata['password']).encode('utf-8'))
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''INSERT INTO users(user_name, nickname, email, password, salt)
VALUES(?, ?, ?, ?, ?);''', (userdata['user_name'], userdata['nickname'], userdata['email'], pass_hash.hexdigest(), salt))
#        uid = c.execute('''SELECT id FROM users WHERE nickname = :nn''', {'nn': userdata['nickname']}).fetchone()
#        c.execute('''CREATE TABLE "anime_list:uid" (
# `id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
# `title`	VARCHAR NOT NULL UNIQUE,
# `title_original`	VARCHAR NOT NULL UNIQUE,
# `release_date`	VARCHAR,
# `series_count`	INTEGER,
# `description`	TEXT,
# `rating`	INTEGER)''', {'uid': uid})
        conn.commit()
        conn.close()
        return 'OK'


@app.route("/api/anime/list")
def api_anime_list():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    anime = c.execute('''SELECT  id, title, title_original, series_count, strftime('%d.%m.%Y', release_date),
description, rating FROM anime_list ORDER BY id ASC LIMIT 50;''').fetchall()
    anime = [[a, escape(b), escape(c), d, e, escape(f), g] for a, b, c, d, e, f, g in anime]
    return jsonify({'anime_list': anime})


@app.route('/api/anime/add', methods=['POST'])
def api_anime_add():
    anime = request.get_json()
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''INSERT INTO anime_list(title, title_original, release_date, series_count, description)
VALUES(?, ?, ?, ?, ?);''', (anime['title'], anime['title_original'], anime['release_date'], anime['series_count'],
                            anime['description']))
        conn.commit()
    except sqlite3.IntegrityError:
        return 'Fail'
    return 'OK'


@app.route("/api/anime/rm/<anime_id>", methods=['POST'])
def api_anime_rm(anime_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''DELETE FROM anime_list WHERE id = :id;''', {'id': anime_id})
    conn.commit()
    return 'OK'


if __name__ == "__main__":
    app.run()
