import sqlite3

connect = sqlite3.connect('resume_app.db')

cursor = connect.cursor()

cursor.execute('''
                CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        profession TEXT NOT NULL,
        experience TEXT NOT NULL
    );
    ''')

connect.commit()
connect.close()

print("База данных успешно создана")
