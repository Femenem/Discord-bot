import sqlite3

with sqlite3.connect('data/movies.db') as db:
    c = db.cursor()
    c.execute("DROP TABLE IF EXISTS Movies;")
    c.execute('''
    CREATE TABLE Movies(
    ID integer PRIMARY KEY AUTOINCREMENT,
    IMDBID text UNIQUE,
    Title text,
    Length text,
    Rating real,
    Genres text,
    ReleaseDate text,
    AgeRating text,
    Summary text);
    ''')
    c.execute("DROP TABLE IF EXISTS UserNames;")
    c.execute('''
    CREATE TABLE UserNames(
    UserID integer PRIMARY KEY AUTOINCREMENT,
    DiscordID integer,
    Nicknames text);
    ''')
    c.execute("DROP TABLE IF EXISTS MovieLists;")
    c.execute('''
    CREATE TABLE MovieLists(
    ID integer PRIMARY KEY AUTOINCREMENT,
    UserID integer,
    MovieID integer);
    ''')
    db.commit()
    print("Database setup complete")
