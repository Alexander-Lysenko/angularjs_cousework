from flask import Flask, render_template, request, Response, jsonify, escape, redirect, url_for
import sqlite3, uuid, hashlib
from functools import wraps
app = Flask(__name__)
app.debug = True


# ==================== AUTHENTICATION ============================
def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    c = sqlite3.connect('database.db').cursor()
    passdata = c.execute('''SELECT salt, password FROM users WHERE nickname = :us;''',
                            {'us': username}).fetchone()
    if not passdata:
        return None
    if passdata[1] == hashlib.sha512((passdata[0] + str(password)).encode('utf-8')).hexdigest():
        return username and password


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response('Could not verify your access level for that URL.\nYou have to login with proper credentials',
                    401, {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


# ==================== AUTHENTICATION API ============================
@app.route('/api/login', methods=['POST'])
def api_login():
    auth = request.get_json()
    if verify(auth['username']) == 'OK':
        if check_auth(auth['username'], auth['password']):
            return 'OK'
    return 'Fail'


@app.route('/api/login/verify/<name>', methods=['POST'])
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


@app.route('/api/logout', methods=['GET'])
@requires_auth
def api_logout():
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401)


@app.route('/api/signup', methods=['POST'])
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
VALUES(?, ?, ?, ?, ?);''', (userdata['user_name'], userdata['nickname'], userdata['email'],
                            pass_hash.hexdigest(), salt))
        uid = c.execute('''SELECT id FROM users WHERE nickname = :nn''', {'nn': userdata['nickname']}).fetchone()
        c.execute('''CREATE TABLE "anime_list_'''+str(uid[0])+'''" (
        `id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        `title`	VARCHAR NOT NULL UNIQUE,
        `title_original`	VARCHAR NOT NULL UNIQUE,
        `release_date`	VARCHAR,
        `series_count`	INTEGER,
        `description`	TEXT,
        `rating`	INTEGER);''')
        conn.commit()
        conn.close()
        return 'OK'


@app.route('/secret-page')
@requires_auth
def secret_page():
    return render_template('index.html')


# ==================== MAIN ============================
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/anime/list')
@requires_auth
def api_anime_list():
    authdata = request.authorization
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    usid = c.execute('''SELECT id, user_name from users where nickname = :uu;''', {'uu':authdata['username']}).fetchone()
    anime = c.execute('''SELECT id, title, title_original, series_count, strftime('%d.%m.%Y', release_date),
description, rating FROM anime_list_''' + str(usid[0]) + ''' ORDER BY id ASC LIMIT 50;''').fetchall()
    anime = [[a, escape(b), escape(c), d, e, escape(f), g] for a, b, c, d, e, f, g in anime]
    return jsonify({'anime_list': anime, 'user_name': usid[1]})


@app.route('/api/anime/add', methods=['POST'])
@requires_auth
def api_anime_add():
    anime = request.get_json()
    authdata = request.authorization
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()        
        usid = c.execute('''SELECT id from users where nickname = :uu;''', {'uu':authdata['username']}).fetchone()
        c.execute('''INSERT INTO anime_list_''' + str(usid[0]) + '''(title, title_original, release_date, series_count, description)
VALUES(?, ?, ?, ?, ?);''', (anime['title'], anime['title_original'], anime['release_date'], anime['series_count'],
                            anime['description']))
        conn.commit()
    except sqlite3.IntegrityError:
        return 'Fail'
    return 'OK'


@app.route('/api/anime/rm/<int:anime_id>', methods=['POST'])
@requires_auth
def api_anime_rm(anime_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''DELETE FROM anime_list WHERE id = :id;''', {'id': anime_id})
    conn.commit()
    return 'OK'


# ==================== CHANGE USER DATA ============================
@app.route('/api/user/get_data')
@requires_auth
def api_user_get_data():
    authdata = request.authorization
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        usid = c.execute('''SELECT id, user_name, email, nickname, password, salt FROM users
WHERE nickname = :uu;''', {'uu': authdata['username']}).fetchone()
        conn.commit()
    except sqlite3.IntegrityError:
        return 'Fail'
    usid = [[escape(a), escape(b), escape(c), d, e, f] for a, b, c, d, e, f in usid]
    return jsonify({'user_data': usid})


@app.route('/api/user/change_info', methods=['POST'])
@requires_auth
def api_user_change_info():
    authdata = request.authorization
    user_data = request.get_json()
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''UPDATE users SET user_name = ?, email = ? where nickname = '''+str(authdata['username']),
                  user_data['user_name'], user_data['email'])
        conn.commit()
    except sqlite3.IntegrityError:
        return 'Fail'
    return 'OK'


@app.route('/api/user/change_password', methods=['POST'])
@requires_auth
def api_user_change_password():
    authdata = request.authorization
    user_data = request.get_json()
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''UPDATE users SET password = ? where nickname = '''+str(authdata['username']),
                  hashlib.sha512((user_data['salt'] + user_data['password']).encode('utf-8')))
        conn.commit()
    except sqlite3.IntegrityError:
        return 'Fail'
    return 'OK'


# ==================== START THIS APP ============================
if __name__ == "__main__":
    app.run()
