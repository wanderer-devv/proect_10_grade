import sqlite3

class RequestsInBD:
    def __init__(self):
        self.connection = sqlite3.Connection('datebase_of_users.db')
        self.cursor = self.connection.cursor()

    def _commit_bd(self):
        self.connection.commit()

    def close_bd(self):
        self.connection.close()
    
    def check(self, user_id):
        all_id = self.cursor.execute('SELECT id FROM grade_of_users').fetchall()
        self._commit_bd()
        for item in all_id:
            if user_id in item:
                return False
        return True
    
    def add_user(self, user_id, grade, message):
        self.cursor.execute('INSERT INTO grade_of_users (id, username, name, grade, notifications) VALUES (?, ?, ?, ?, ?)', (user_id, message.from_user.username, message.from_user.first_name, grade, 1))
        self._commit_bd()

    def return_user_grade(self, user_id):
        self.cursor.execute(f'SELECT id, grade FROM grade_of_users WHERE id = {user_id}')
        try:
            grade = self.cursor.fetchall()[0][1]
        except:
            grade = False
            print(f'ошибка fetchall с id: {user_id} 1')
        self._commit_bd()
        return grade
    
    def get_users(self):
        self.cursor.execute('SELECT id, grade, notifications FROM grade_of_users')
        res = self.cursor.fetchall()
        self._commit_bd()
        return res
    
    def new_grade(self, grade, user_id):
        self.cursor.execute('UPDATE grade_of_users SET grade = ? WHERE id = ?', (grade, user_id))
        self._commit_bd()

    def get_notif(self, user_id):
        self.cursor.execute(f'SELECT id, notifications FROM grade_of_users WHERE id = {user_id}')
        try:
            notif = self.cursor.fetchall()[0][1]
        except:
            notif = False
            print(f'ошибка fetchall с id: {user_id} 2')
        return notif
    
    def change_notif(self, user_id, value):
        self.cursor.execute(f'UPDATE grade_of_users SET notifications = {value} WHERE id = {user_id}')
        self._commit_bd()