import sqlite3 as sql


async def sql_connector():
    con = sql.connect("bot.db")
    cur = con.cursor()
    return con, cur


async def create_tables():
    con, cur = await sql_connector()

    cur.execute("""CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE
                )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS songs(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(100),
                subtitle VARCHAR(100),
                file_id TEXT
                )""")


async def add_user(user_id):
    con, cur = await sql_connector()

    user = cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    if not user:
        cur.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        con.commit()


async def add_song(audio_id, audio_title, audio_subtitle):
    con, cur = await sql_connector()

    cur.execute("INSERT INTO songs (file_id, title, subtitle) VALUES (?, ?, ?)",
                (audio_id, audio_title, audio_subtitle))
    con.commit()


async def search_song(text, limit=10, offset=1):
    con, cur = await sql_connector()

    count_songs = cur.execute("SELECT count(*) FROM songs WHERE title LIKE ? || '%'", (text,)).fetchone()
    result = cur.execute(f"SELECT * FROM songs WHERE title LIKE ? || '%' LIMIT {limit} OFFSET {offset}", (text,)).fetchall()
    return result, count_songs[0]


async def get_song_by_id(song_id):
    con, cur = await sql_connector()

    result = cur.execute("SELECT * FROM songs WHERE id = ?", (song_id,)).fetchone()
    return result







async def get_channels():
    con, cur = await sql_connector()
    
    channels = cur.execute("SELECT * FROM channels").fetchall()
    return channels



async def count_all_users():
    con, cur = await sql_connector()
    
    users = cur.execute("SELECT COUNT(*) FROM users").fetchone()
    return users[0]




async def get_all_users():
    con, cur = await sql_connector()
    
    users = cur.execute("SELECT * FROM users").fetchall()
    return users

 