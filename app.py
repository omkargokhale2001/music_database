from flask import Flask, render_template, request, session, redirect, url_for
from flask_mysqldb import MySQL
import yaml
import MySQLdb.cursors
import re
from flask_bcrypt import Bcrypt
import pandas as pd

app = Flask(__name__)

app.secret_key = 'your secret key'

# Configuring db
db = yaml.load(open('db.yaml'))
list_db = db.split(" ")
db_fin = {}
for i in list_db:
    temp = i.split(":")
    db_fin[temp[0]] = temp[1]
db = db_fin
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)
bcrypt = Bcrypt(app)



def insert_excel(dict_info):
    msg = ""
    song_name = dict_info['song_name']
    song_url = dict_info['song_url']
    date = dict_info['date']
    artist_name = dict_info['artist_name']
    album_name = dict_info['album_name']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Songs WHERE song_name=%s", [song_name])
    song = cur.fetchall()
    if not song:
        cur.execute("SELECT * FROM Album WHERE album_name=%s", [album_name])
        album = cur.fetchall()
        if not album:
            cur.execute("SELECT * FROM Artist WHERE name=%s", [artist_name])
            artist = cur.fetchall()
            if not artist:
                cur.execute("SELECT MAX(artist_id) FROM Artist")
                curr_artist_id = cur.fetchall()
                curr_artist_id = curr_artist_id[0][0]
                curr_artist_id += 1
                cur.execute("INSERT INTO Artist VAlUES(%s,%s)", [artist_name, curr_artist_id])
                mysql.connection.commit()
                cur.execute("SELECT * FROM Artist WHERE name=%s", [artist_name])
                artist = cur.fetchall()
            curr_artist_id = int(artist[0][1])
            cur.execute("SELECT MAX(album_id) FROM Album")
            curr_album_id = cur.fetchall()[0][0] + 1
            cur.execute("INSERT INTO Album VALUES(%s,%s,%s,%s)", [curr_album_id, curr_artist_id, album_name, date])
            mysql.connection.commit()
            cur.execute("SELECT * FROM Album WHERE album_name=%s", [album_name])
            album = cur.fetchall()
        curr_album_id = int(album[0][0])
        curr_artist_id = int(album[0][1])
        cur.execute("SELECT MAX(song_id) FROM Songs")
        song = cur.fetchall()
        song_id = int(song[0][0]) + 1
        cur.execute("INSERT INTO Songs VALUES(%s,%s,%s,%s,%s)",
                        [song_id, song_name, song_url, curr_album_id, curr_artist_id])
        mysql.connection.commit()
        msg = "Song entered successfully"
    return msg

def run_excel():
    df = df = pd.read_csv("songs.csv")
    df = df.drop([16, 20], axis=0)

    def change_date(date):
        date = date[6:] + "-" + date[3:5] + "-" + date[0:2]
        return date
    df['Release date of album'] = df['Release date of album'].apply(lambda x: change_date(x))
    df = df.drop([0, 1, 2, 3, 4, 5], axis=0)
    df = df.reset_index()
    for j in range(len(df)):
        dict_info = dict()
        dict_info['song_name'] = df['Song name'].iloc[j]
        dict_info['album_name'] = df['Album name'].iloc[j]
        dict_info['artist_name'] = df['Artist Name'].iloc[j]
        dict_info['date'] = df['Release date of album'].iloc[j]
        dict_info['song_url'] = df['Embedded URL'].iloc[j]
        insert_excel(dict_info)





@app.route('/', methods=['GET'])
def index():
    if session:
        name = session['name']
        msg = "Welcome " + str(name)
        return render_template('index.html', msg=msg)
    else:
        return render_template('login.html')

@app.route('/insert_excel', methods=['GET'])
def add_from_excel():
    if session:
        if session['name'] == "admin":
            run_excel()
        else:
            return render_template('page_not_found.html')
    else:
        return render_template('page_not_found.html')


# Searching by name
@app.route('/song_search/song_name', methods=['GET','POST'])
def search_song():
    if request.method == 'POST':
        var_name = request.form['name']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Songs WHERE song_name=%s", [var_name])
        song_details = cur.fetchall()
        song_url = song_details[0][2]
        artist = song_details[0][4]
        album = song_details[0][3]
        cur.execute("SELECT album_name FROM Album WHERE album_id=%s", [album])
        album_fin = cur.fetchall()
        cur.execute("SELECT name FROM Artist WHERE artist_id=%s", [artist])
        artist_fin = cur.fetchall()
        result = str(song_details[0][1]) +" from album " +str(album_fin[0][0]) + " by " + str(artist_fin[0][0])
        cur.close()
        return render_template('songs.html', result=result, url=song_url)
    else:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Songs ORDER BY RAND() LIMIT 6")
        song_details = cur.fetchall()
        print(song_details)
        names = []
        urls = []
        for i in song_details:
            names.append(i[1])
            urls.append(i[2])
        return render_template('songs.html',names=names,urls=urls)

@app.route('/song_search/album',methods=['GET','POST'])
def album_song():
    if request.method =='POST':
        var_name = request.form['album_name']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Songs WHERE album_id=(SELECT album_id FROM Album WHERE album_name=%s)", [var_name])
        songs = cur.fetchall()
        names = []
        urls = []
        for i in songs:
            names.append(i[1])
            urls.append(i[2])
        names.append(len(names))
        urls.append(len(urls))
        return render_template('albums.html', names=names, urls=urls,album_name=var_name)
    return render_template('albums.html')

@app.route('/song_search/artist',methods=['GET','POST'])
def search_album():
    if request.method == 'POST':
        var_name = request.form['artist_name']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Songs WHERE artist_id=(SELECT artist_id FROM Artist WHERE name=%s)", [var_name])
        songs = cur.fetchall()
        names = []
        urls = []
        for i in songs:
            names.append(i[1])
            urls.append(i[2])
        names.append(len(names))
        urls.append(len(urls))
        return render_template('artists.html', names=names, urls=urls, artist_name=var_name)
    return render_template('artists.html')


@app.route('/add_song', methods=['GET', 'POST'])
def insert_song():
    msg = "Song already exists!"
    if request.method == 'POST':
        song_name = request.form['song_name']
        song_url = request.form['song_url']
        date = "2018-03-01"
        artist_name = request.form['artist_name']
        album_name = request.form['album_name']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Songs WHERE song_name=%s", [song_name])
        song = cur.fetchall()
        if not song:
            cur.execute("SELECT * FROM Album WHERE album_name=%s", [album_name])
            album = cur.fetchall()
            if not album:
                cur.execute("SELECT * FROM Artist WHERE name=%s", [artist_name])
                artist = cur.fetchall()
                if not artist:
                    cur.execute("SELECT MAX(artist_id) FROM Artist")
                    curr_artist_id = cur.fetchall()
                    curr_artist_id = curr_artist_id[0][0]
                    curr_artist_id += 1
                    cur.execute("INSERT INTO Artist VAlUES(%s,%s)", [artist_name, curr_artist_id])
                    mysql.connection.commit()
                    cur.execute("SELECT * FROM Artist WHERE name=%s", [artist_name])
                    artist = cur.fetchall()
                curr_artist_id = int(artist[0][1])
                cur.execute("SELECT MAX(album_id) FROM Album")
                curr_album_id = cur.fetchall()[0][0] + 1
                cur.execute("INSERT INTO Album VALUES(%s,%s,%s,%s)",[curr_album_id,curr_artist_id,album_name,date])
                mysql.connection.commit()
                cur.execute("SELECT * FROM Album WHERE album_name=%s", [album_name])
                album = cur.fetchall()
            curr_album_id = int(album[0][0])
            curr_artist_id = int(album[0][1])
            cur.execute("SELECT MAX(song_id) FROM Songs")
            song = cur.fetchall()
            song_id = int(song[0][0]) + 1
            cur.execute("INSERT INTO Songs VALUES(%s,%s,%s,%s,%s)", [song_id,song_name,song_url,curr_album_id,curr_artist_id])
            mysql.connection.commit()
            msg = "Song entered successfully"
    return render_template("add_song.html", msg=msg)


@app.route('/create_playlist', methods=['GET', 'POST'])
def create_playlist():
    if request.method == 'POST':
        name = request.form['playlist_name']   #p1
        cur = mysql.connection.cursor()
        query = "SELECT MAX(playlist_id) FROM All_Playlists_" + str(session['id'])
        cur.execute(query)
        id_temp = cur.fetchall()[0][0]
        print(id_temp)
        curr_id = int(id_temp) + 1
        playlist_name = name + "_" + str(session['id']).zfill(4)
        query = "CREATE TABLE " + playlist_name + "(song_id int,song_name varchar(100),song_url varchar(100),primary key(song_id))"
        cur.execute(query)
        query2 = "INSERT INTO All_Playlists_" + str(session['id'])+" values("+str(curr_id)+","
        print(query2)
        cur.execute(query2+"%s)",[playlist_name])
        mysql.connection.commit()
        cur.close()
        return render_template('create-playlist.html')
    return render_template('create-playlist.html')

@app.route('/all_playlists', methods=['GET'])
def show_all_playlist():
    cur = mysql.connection.cursor()
    query = "SELECT playlist_name FROM All_Playlists_" + str(session['id'])
    cur.execute(query)
    playlists = cur.fetchall()
    final_playlists = []
    for i in playlists:
        final_playlists.append(i[0][0:-5])
    length = len(final_playlists)
    return render_template('playlists.html', playlists=final_playlists, len=length)

@app.route('/all_playlists/<name>', methods=['GET'])
def display_playlist(name):
    cur = mysql.connection.cursor()
    query = "SELECT * FROM " + name + "_" + str(session['id']).zfill(4)
    cur.execute(query)
    songs = cur.fetchall()
    names = []
    urls = []
    for i in songs:
        names.append(i[1])
        urls.append(i[2])
    names.append(len(names))
    urls.append(len(urls))
    return render_template('view_playlist.html', names=names, urls=urls, name=name)

@app.route('/all_playlists/<name>/add_songs', methods=['GET','POST'])
def add_to_playlist(name):
    if request.method == 'POST':
        song_name = request.form['song_name']
        print(song_name)
        cur = mysql.connection.cursor()
        query = "SELECT song_name FROM " + str(name) + "_" + str(session['id']).zfill(4)
        cur.execute(query)
        songs_in_playlist = cur.fetchall()
        songs_in_playlist = [i[0] for i in songs_in_playlist]
        print(songs_in_playlist)
        exists = False
        if song_name in songs_in_playlist:
            exists = True
            return render_template("add-to-playlist.html", exists=exists)
        cur.execute("SELECT song_id,song_name,song_url FROM Songs WHERE song_name=%s", [song_name])
        song_info = cur.fetchall()
        song_id = int(song_info[0][0])
        song_name = song_info[0][1]
        song_url = song_info[0][2]
        print(song_info)
        print(song_name)
        print(song_url)
        query = "INSERT INTO " + name + "_" + str(session['id']).zfill(4) + " values"
        print(query)
        cur.execute(query+"(%s,%s,%s)", [song_id, song_name, song_url])
        mysql.connection.commit()
        cur.close()
        return render_template("add-to-playlist.html", song_info=song_info, name=name,exists=exists)
    return render_template("add-to-playlist.html")

@app.route('/signup',methods=['GET','POST'])
def register():
    msg = ''

    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form:
        name = request.form['name']
        password = bcrypt.generate_password_hash(request.form['password'])
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Users WHERE email = % s', [email])
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', name):
            msg = 'Name must contain only characters and numbers !'
        elif not name or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cur = mysql.connection.cursor()
            cur.execute("SELECT MAX(id) FROM Users")
            curr_id = int(cur.fetchall()[0][0]) + 1
            all_play_name = "All_Playlists_" + str(curr_id)
            query = "CREATE TABLE "+all_play_name+"(playlist_id int,playlist_name varchar(100))"
            cursor.execute(query)
            query1 = "INSERT INTO " + all_play_name + " VALUES(0,'admin')"
            cursor.execute(query1)
            cursor.execute('INSERT INTO Users VALUES (%s, %s, %s, %s, %s)', (curr_id, name, email, password, all_play_name))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg=msg)


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        print("Flag3")
        email = request.form['email']
        password = request.form['password']
        print(password)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Users WHERE email = % s', [email])
        print("Flag2")
        account = cursor.fetchone()
        print("Flag1")
        password_check = bcrypt.check_password_hash(account['password'], password)
        if account and password_check:
            session['loggedin'] = True
            session['id'] = account['id']
            session['name'] = account['name']
            session['email'] = account['email']
            msg = 'Logged in successfully !'
            print(msg)
            return redirect(url_for("index"))
        else:
            msg = 'Incorrect username / password !'
        print(msg)
    return render_template('login.html', msg=msg)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('name', None)
    session.pop('email',None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)

# render_template('index.html', msg=msg, name=session['name'])