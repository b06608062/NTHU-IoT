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
            self.check_and_create_database()
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

    def check_and_create_database(self):
        self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_name}")

    def create_table(self, table_name):
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            unique_id VARCHAR(36),
            data TEXT,
            latitude_c DOUBLE,
            longitude_c DOUBLE,
            latitude_p DOUBLE DEFAULT NULL,
            longitude_p DOUBLE DEFAULT NULL,
            floor INT,
            distance DOUBLE DEFAULT NULL,
            mode TEXT,
            send_t DATETIME,
            get_t DATETIME DEFAULT NULL
        );
        """
        self.cursor.execute(create_table_query)
        self.connection.commit()

    def insert_data(
        self, table_name, unique_id, data, latitude_c, longitude_c, floor, mode, send_t
    ):
        try:
            insert_query = f"""
                INSERT INTO {table_name} (unique_id, data, latitude_c, longitude_c, floor, mode, send_t)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (unique_id, data, latitude_c, longitude_c, floor, mode, send_t)
            self.cursor.execute(insert_query, values)
            self.connection.commit()
        except mysql.connector.Error as e:
            print(f"Error in insert_data: {e}")
            self.reconnect()

    def close(self):
        self.cursor.close()
        self.connection.close()
