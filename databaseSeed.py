# script to populate my Databases with tables
import sqlite3

Conn = sqlite3.connect('./botgru.db') # open database
c = Conn.cursor() # make cursor for db

c.executescript('''
    CREATE TABLE IF NOT EXISTS users (
        uid integer PRIMARY KEY,
        name text NOT NULL,
        digestType text,
        nextDigest text,
        UNIQUE(uid)
    );

    CREATE TABLE IF NOT EXISTS events (
        eid text PRIMARY KEY,
        title text NOT NULL,
        desc text,
        date text,
        user_id integer,
        FOREIGN KEY (user_id) REFERENCES users (uid)
    );

    CREATE TABLE IF NOT EXISTS notes (
        nid text PRIMARY KEY,
        note text NOT NULL,
        date text,
        timer text,
        user_id integer,
        FOREIGN KEY (user_id) REFERENCES users (uid)
    );
    ''')

Conn.commit()
Conn.close()