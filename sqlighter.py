import sqlite3

class SQLighter:

    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def get_subscriptions(self):
        """Получаем всех активных подписчиков бота"""
        with self.connection:
            return self.cursor.execute("SELECT user_id FROM 'users'").fetchall()

    def subscriber_exists(self, user_id):
        """Проверяем, есть ли уже юзер в базе"""
        with self.connection:
            result = self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchall()
            return bool(len(result))

    def get_link(self, user_id, url_name):
        """Получаем ссылку"""
        with self.connection:
            result = self.cursor.execute(f"SELECT {url_name} FROM users WHERE user_id = ?", (user_id,)).fetchall()
            return result[0][0]

    def get_encoded(self, user_id, week):
        """Получаем закодированное сообщение"""
        with self.connection:
            result = self.cursor.execute(f"SELECT {week} FROM users WHERE user_id = ?", (user_id,)).fetchall()
            return result[0][0]

    def get_weekday(self, user_id):
        """Получаем день недели"""
        with self.connection:
            result = self.cursor.execute("SELECT day FROM users WHERE user_id = ?", (user_id,)).fetchall()
            return result[0][0]

    def get_days_number(self, user_id):
        """Получаем количество дней недели, в которые есть занятия"""
        with self.connection:
            result = self.cursor.execute("SELECT days_number FROM users WHERE user_id = ?", (user_id,)).fetchall()
            return result[0][0]

    def add_subscriber(self, user_id):
        """Добавляем нового подписчика"""
        with self.connection:
            return self.cursor.execute("INSERT INTO 'users' (`user_id`) VALUES(?)", (user_id,))

    def update_link(self, user_id, url_name, link):
        """Обновляем link"""
        with self.connection:
            return self.cursor.execute(f"UPDATE 'users' SET {url_name} = ? WHERE `user_id` = ?",
                                       (link, user_id))

    def update_encoded(self, user_id, week, hash):
        """Обновляем закодированое сообщение"""
        with self.connection:
            return self.cursor.execute(f"UPDATE 'users' SET `{week}` = ? WHERE `user_id` = ?",
                                       (hash, user_id))

    def update_weekday(self, user_id, day_number):
        """Обновляем день недели"""
        with self.connection:
            return self.cursor.execute("UPDATE 'users' SET `day` = ? WHERE `user_id` = ?",
                                       (day_number, user_id))

    def update_days_number(self, user_id, day_number):
        """Получаем количество дней недели, в которые есть занятия"""
        with self.connection:
            return self.cursor.execute("UPDATE 'users' SET `days_number` = ? WHERE `user_id` = ?",
                                       (day_number, user_id))

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()
