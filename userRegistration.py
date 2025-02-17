import sqlite3

def is_valid_group_number(group_number):
    conn = sqlite3.connect('AmGU_timetableDB.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (group_number,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def user_exists(userId):
    conn = sqlite3.connect('AmGU_timetableDB.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE userId = ?", (userId,))
    existing_user = cursor.fetchone()
    conn.close()
    return existing_user is not None

# Функция для регистрации пользователя в базе данных
def register_user(userId, username, group_number):
    conn = sqlite3.connect('AmGU_timetableDB.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (userId, username, usergroup) VALUES (?, ?, ?)", (userId, username, group_number))
    conn.commit()
    conn.close()
