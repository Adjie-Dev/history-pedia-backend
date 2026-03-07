import mysql.connector
from mysql.connector import Error

class Database:
    def __init__(self):
        self.host = 'adjiee.mysql.pythonanywhere-services.com'
        self.database = 'adjiee$default'
        self.user = 'adjiee'
        self.password = 'felirHytam69!'
    
    def connect(self):
        try:
            connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            return connection
        except Error as e:
            print(f"Error: {e}")
            return None
    
    def save_chat(self, user_id, user_message, ai_response, model='llama-3.3-70b-versatile'):
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
