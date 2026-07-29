import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.host = os.getenv('DB_HOST')
        self.database = os.getenv('DB_NAME')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')
        self.port = int(os.getenv('DB_PORT', '3306'))
        self.ssl_ca = os.getenv('DB_SSL_CA')

        # Vercel menjalankan function dari working directory yang bukan root repo,
        # jadi path relatif harus diikat ke lokasi file ini.
        if self.ssl_ca and not os.path.isabs(self.ssl_ca):
            self.ssl_ca = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.ssl_ca)

    def connect(self):
        try:
            options = {
                'host': self.host,
                'database': self.database,
                'user': self.user,
                'password': self.password,
                'port': self.port
            }

            if self.ssl_ca:
                options['ssl_ca'] = self.ssl_ca

            connection = mysql.connector.connect(**options)
            return connection
        except Error as e:
            print(f"Error: {e}")
            return None
    
    def save_chat(self, user_id, user_message, ai_response, model):
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor()
                query = """INSERT INTO chat_history 
                          (user_id, user_message, ai_response, model) 
                          VALUES (%s, %s, %s, %s)"""
                cursor.execute(query, (user_id, user_message, ai_response, model))
                conn.commit()
                return cursor.lastrowid
            finally:
                cursor.close()
                conn.close()
    
    def get_history(self, user_id='anonymous', limit=50):
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                query = """SELECT * FROM chat_history 
                          WHERE user_id = %s 
                          ORDER BY timestamp DESC 
                          LIMIT %s"""
                cursor.execute(query, (user_id, limit))
                return cursor.fetchall()
            finally:
                cursor.close()
                conn.close()
        return []
    
    def get_all_history(self, limit=100):
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                query = """SELECT * FROM chat_history 
                          ORDER BY timestamp DESC 
                          LIMIT %s"""
                cursor.execute(query, (limit,))
                return cursor.fetchall()
            finally:
                cursor.close()
                conn.close()
        return []
    
    def delete_chat(self, chat_id):
        conn = self.connect()
        if conn:
            try:
                cursor = conn.cursor()
                query = "DELETE FROM chat_history WHERE id = %s"
                cursor.execute(query, (chat_id,))
                conn.commit()
                return cursor.rowcount > 0
            finally:
                cursor.close()
                conn.close()
        return False

db = Database()
