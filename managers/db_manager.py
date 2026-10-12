import mysql.connector
from mysql.connector import Error
import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

class DBManager:
    def __init__(self, host="localhost", user="root", password="", database="space_invader_aseniero"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                return True
        except Error as e:
            print(f"Error connecting to MySQL database: {e}")
            return False
        return False

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def register_player(self, username: str, password: str):
        if not username or len(username) < 3:
            return False, "Username must be at least 3 characters."
        if not password or len(password) < 4:
            return False, "Password must be at least 4 characters."

        if not self.connect():
            return False, "Cannot connect to the database."

        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT id FROM players WHERE username = %s", (username,))
            if cursor.fetchone():
                return False, f"Username '{username}' is already taken."

            pw_hash = hash_password(password)
            cursor.execute(
                "INSERT INTO players (username, password_hash) VALUES (%s, %s)",
                (username, pw_hash)
            )
            self.connection.commit()
            return True, cursor.lastrowid
        except Error as e:
            print(f"Error registering player: {e}")
            return False, "Database error during registration."
        finally:
            self.close()

    def login_player(self, username: str, password: str):
        if not self.connect():
            return None

        try:
            cursor = self.connection.cursor(dictionary=True)
            pw_hash = hash_password(password)
            cursor.execute(
                "SELECT * FROM players WHERE username = %s AND password_hash = %s",
                (username, pw_hash)
            )
            return cursor.fetchone()
        except Error as e:
            print(f"Error during login: {e}")
            return None
        finally:
            self.close()

    def get_or_create_player(self, username):
        if not self.connect():
            return None

        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT id FROM players WHERE username = %s", (username,))
            player = cursor.fetchone()
            
            if player:
                return player['id']
            
            cursor.execute("INSERT INTO players (username) VALUES (%s)", (username,))
            self.connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"Error getting/creating player: {e}")
            return None
        finally:
            self.close()

    def update_player_username(self, old_username, new_username):
        if not self.connect():
            return False

        try:
            cursor = self.connection.cursor()
            cursor.execute("UPDATE players SET username = %s WHERE username = %s", (new_username, old_username))
            self.connection.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"Error updating player username: {e}")
            return False
        finally:
            self.close()

    def get_player_profile(self, username):
        if not self.connect():
            return None

        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM players WHERE username = %s", (username,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error retrieving player profile: {e}")
            return None
        finally:
            self.close()

    def update_player_profile(self, username, ship_color=None, player_title=None, control_scheme=None, difficulty=None, left_en=None, right_en=None, fire_en=None):
        if not self.connect():
            return False

        try:
            cursor = self.connection.cursor()
            updates = []
            params = []
            
            if ship_color:
                updates.append("ship_color = %s")
                params.append(ship_color)
            if player_title:
                updates.append("player_title = %s")
                params.append(player_title)
            if control_scheme:
                updates.append("control_scheme = %s")
                params.append(control_scheme)
            if difficulty:
                updates.append("difficulty = %s")
                params.append(difficulty)
            if left_en is not None:
                updates.append("btn_left_enabled = %s")
                params.append(1 if left_en else 0)
            if right_en is not None:
                updates.append("btn_right_enabled = %s")
                params.append(1 if right_en else 0)
            if fire_en is not None:
                updates.append("btn_fire_enabled = %s")
                params.append(1 if fire_en else 0)
                
            if not updates:
                return True
                
            params.append(username)
            query = f"UPDATE players SET {', '.join(updates)} WHERE username = %s"
            
            cursor.execute(query, tuple(params))
            self.connection.commit()
            return cursor.rowcount > 0
        except Error as e:
            print(f"Error updating player profile: {e}")
            return False
        finally:
            self.close()

    def save_score(self, username, score):
        player_id = self.get_or_create_player(username)
        if not player_id or not self.connect():
            return False

        try:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO scores (player_id, score) VALUES (%s, %s)", (player_id, score))
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error saving score: {e}")
            return False
        finally:
            self.close()

    def get_top_scores(self, limit=10):
        if not self.connect():
            return []

        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT p.username, MAX(s.score) AS score, MAX(s.achieved_at) AS achieved_at 
                FROM scores s
                JOIN players p ON s.player_id = p.id
                GROUP BY p.id, p.username
                ORDER BY score DESC
                LIMIT %s
            """
            cursor.execute(query, (limit,))
            return cursor.fetchall()
        except Error as e:
            print(f"Error retrieving top scores: {e}")
            return []
        finally:
            self.close()

    def get_player_best_score(self, username):
        if not self.connect():
            return 0

        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT MAX(s.score) AS best
                FROM scores s
                JOIN players p ON s.player_id = p.id
                WHERE p.username = %s
            """
            cursor.execute(query, (username,))
            row = cursor.fetchone()
            return row["best"] if row and row["best"] is not None else 0
        except Error as e:
            print(f"Error retrieving best score: {e}")
            return 0
        finally:
            self.close()