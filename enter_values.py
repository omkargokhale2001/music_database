# from flask import Flask, render_template, request, session, redirect, url_for
# from flask_mysqldb import MySQL
# import yaml
# import MySQLdb.cursors
# import re
# from flask_bcrypt import Bcrypt
# import pandas as pd
#
# def insert_excel(dict_info):
#     msg = ""
#     song_name = dict_info['song_name']
#     song_url = dict_info['song_url']
#     date = dict_info['date']
#     artist_name = dict_info['artist_name']
#     album_name = dict_info['album_name']
#     cur = mysql.connection.cursor()
#     cur.execute("SELECT * FROM Songs WHERE song_name=%s", [song_name])
#     song = cur.fetchall()
#     if not song:
#         cur.execute("SELECT * FROM Album WHERE album_name=%s", [album_name])
#         album = cur.fetchall()
#         if not album:
#             cur.execute("SELECT * FROM Artist WHERE name=%s", [artist_name])
#             artist = cur.fetchall()
#             if not artist:
#                 cur.execute("SELECT MAX(artist_id) FROM Artist")
#                 curr_artist_id = cur.fetchall()
#                 curr_artist_id = curr_artist_id[0][0]
#                 curr_artist_id += 1
#                 cur.execute("INSERT INTO Artist VAlUES(%s,%s)", [artist_name, curr_artist_id])
#                 mysql.connection.commit()
#                 cur.execute("SELECT * FROM Artist WHERE name=%s", [artist_name])
#                 artist = cur.fetchall()
#             curr_artist_id = int(artist[0][1])
#             cur.execute("SELECT MAX(album_id) FROM Album")
#             curr_album_id = cur.fetchall()[0][0] + 1
#             cur.execute("INSERT INTO Album VALUES(%s,%s,%s,%s)", [curr_album_id, curr_artist_id, album_name, date])
#             mysql.connection.commit()
#             cur.execute("SELECT * FROM Album WHERE album_name=%s", [album_name])
#             album = cur.fetchall()
#         curr_album_id = int(album[0][0])
#         curr_artist_id = int(album[0][1])
#         cur.execute("SELECT MAX(song_id) FROM Songs")
#         song = cur.fetchall()
#         song_id = int(song[0][0]) + 1
#         cur.execute("INSERT INTO Songs VALUES(%s,%s,%s,%s,%s)",
#                         [song_id, song_name, song_url, curr_album_id, curr_artist_id])
#         mysql.connection.commit()
#         msg = "Song entered successfully"
#     return msg
#
# def run_excel():
#     df = df = pd.read_csv("songs.csv")
#     df = df.drop([16, 20], axis=0)
#
#     def change_date(date):
#         date = date[6:] + "-" + date[3:5] + "-" + date[0:2]
#         return date
#     df['Release date of album'] = df['Release date of album'].apply(lambda x: change_date(x))
#     df = df.drop([0, 1, 2, 3, 4, 5], axis=0)
#     df = df.reset_index()
#     for j in range(len(df)):
#         dict_info = dict()
#         dict_info['song_name'] = df['Song name'].iloc[j]
#         dict_info['album_name'] = df['Album name'].iloc[j]
#         dict_info['artist_name'] = df['Artist name'].iloc[j]
#         dict_info['date'] = df['Release date of album'].iloc[j]
#         dict_info['song_url'] = df['Embedded URL'].iloc[j]
#         insert_excel(dict_info)