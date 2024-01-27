import mysql.connector
from mysql.connector import Error


class Database:
    def __init__(self, db_name):
        self.db_config = {
            "host": "140.114.71.158",
            "port": "3306",
            "user": "root",
            "password": "0807",
        }
        self.db_name = db_name
        self.connect()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            self.cursor = self.connection.cursor()
            self.cursor.execute(f"USE {self.db_name}")
        except Error as e:
            print(f"Error connecting to MySQL: {e}")

    def reconnect(self):
        try:
            if not self.connection.is_connected():
                print("Reconnecting to MySQL database...")
                self.connect()
        except Error as e:
            print(f"Error reconnecting to MySQL: {e}")

    def update_data(
        self, table_name, unique_id, latitude_p, longitude_p, distance, get_t
    ):
        try:
            update_query = f"""
            UPDATE {table_name}
            SET latitude_p = %s, longitude_p = %s, distance = %s, get_t = %s
            WHERE unique_id = %s;
            """
            values = (latitude_p, longitude_p, distance, get_t, unique_id)
            self.cursor.execute(update_query, values)
            self.connection.commit()
        except mysql.connector.Error as e:
            print(f"Error in insert_data: {e}")
            self.reconnect()

    def close(self):
        self.cursor.close()
        self.connection.close()
