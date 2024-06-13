import sqlite3


class Database:
    def __init__(self, db_path):
        self.connection = None
        self.db_path = db_path

    def get_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
        return self.connection

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def get_picture_file(self, id):
        connection = self.get_connection()

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM image WHERE id = ?", (id,))

        file_name = cursor.fetchone()

        return file_name[1]

    def get_counter(self):
        connection = self.get_connection()

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM counter")

        counter = cursor.fetchone()

        self.increment_counter()
        return counter[0]

    def increment_counter(self):
        connection = self.get_connection()

        cursor = connection.cursor()
        cursor.execute("UPDATE counter SET number = number + 1")

        connection.commit()
