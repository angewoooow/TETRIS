import mysql.connector
from mysql.connector import Error


class DatabaseManager:
    """
    MySQL storage manager for BlockMaster.

    Designed for:
        XAMPP
        MySQL / MariaDB
        Database: blockmaster
        Table: game_scores

    Expected table columns:

        id
        player_name
        score
        level
        line_count
        played_at
    """

    HOST = "localhost"
    PORT = 3306
    USER = "root"
    PASSWORD = ""
    DATABASE = "blockmaster"

    def __init__(self):
        self.connection = None

    # ============================================================
    # CONNECTION
    # ============================================================

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.HOST,
                port=self.PORT,
                user=self.USER,
                password=self.PASSWORD,
                database=self.DATABASE
            )

            if self.connection.is_connected():
                print("[DATABASE] Connected successfully!")
                return True

            return False

        except Error as e:
            print(f"[DATABASE] Connection failed: {e}")
            self.connection = None
            return False

    def ensure_connection(self):
        try:
            if self.connection and self.connection.is_connected():
                return True
        except Error:
            pass

        return self.connect()

    # ============================================================
    # SAVE GAME
    # ============================================================

    def save_game(self, player_name, score, level, lines):
        """
        Save one completed game.

        Every game is inserted as a NEW record.
        Existing scores are never overwritten.
        """

        if not self.ensure_connection():
            print("[DATABASE] Cannot save game - database unavailable.")
            return False

        sql = """
            INSERT INTO game_scores
            (
                player_name,
                score,
                level,
                line_count
            )
            VALUES (%s, %s, %s, %s)
        """

        cursor = None

        try:
            cursor = self.connection.cursor()

            cursor.execute(
                sql,
                (
                    str(player_name)[:50],
                    int(score),
                    int(level),
                    int(lines)
                )
            )

            self.connection.commit()

            print(
                f"[DATABASE] Game saved successfully! "
                f"Player={player_name}, Score={score}"
            )

            return True

        except Error as e:
            print(f"[DATABASE] Save failed: {e}")

            try:
                self.connection.rollback()
            except Error:
                pass

            return False

        finally:
            if cursor:
                try:
                    cursor.close()
                except Error:
                    pass

    # ============================================================
    # HIGH SCORE VALUE
    # ============================================================

    def get_high_score(self):
        """
        Return the highest score ever recorded.
        """

        if not self.ensure_connection():
            return 0

        cursor = None

        try:
            cursor = self.connection.cursor()

            cursor.execute("""
                SELECT COALESCE(MAX(score), 0)
                FROM game_scores
            """)

            result = cursor.fetchone()

            if result and result[0] is not None:
                return int(result[0])

            return 0

        except Error as e:
            print(f"[DATABASE] High score read failed: {e}")
            return 0

        finally:
            if cursor:
                try:
                    cursor.close()
                except Error:
                    pass

    # ============================================================
    # HIGHEST SCORE RECORD
    # ============================================================

    def get_high_score_record(self):
        """
        Return the complete record belonging to the highest score.

        Example:

        {
            "id": 5,
            "player_name": "ANGELO",
            "score": 2500,
            "level": 6,
            "line_count": 42,
            "played_at": ...
        }
        """

        if not self.ensure_connection():
            return None

        cursor = None

        try:
            cursor = self.connection.cursor(dictionary=True)

            cursor.execute("""
                SELECT
                    id,
                    player_name,
                    score,
                    level,
                    line_count,
                    played_at
                FROM game_scores
                ORDER BY
                    score DESC,
                    played_at ASC,
                    id ASC
                LIMIT 1
            """)

            result = cursor.fetchone()

            return result

        except Error as e:
            print(f"[DATABASE] High score record read failed: {e}")
            return None

        finally:
            if cursor:
                try:
                    cursor.close()
                except Error:
                    pass

    # ============================================================
    # TOP SCORES
    # ============================================================

    def get_top_scores(self, limit=100):
        """
        Get the highest scores.

        Used for the main leaderboard.
        """

        if not self.ensure_connection():
            return []

        try:
            limit = int(limit)
        except (ValueError, TypeError):
            limit = 100

        limit = max(1, min(limit, 5000))

        sql = f"""
            SELECT
                id,
                player_name,
                score,
                level,
                line_count,
                played_at
            FROM game_scores
            ORDER BY
                score DESC,
                played_at ASC,
                id ASC
            LIMIT {limit}
        """

        cursor = None

        try:
            cursor = self.connection.cursor(dictionary=True)

            cursor.execute(sql)

            rows = cursor.fetchall()

            return rows

        except Error as e:
            print(f"[DATABASE] Leaderboard read failed: {e}")
            return []

        finally:
            if cursor:
                try:
                    cursor.close()
                except Error:
                    pass

    # ============================================================
    # ALL SCORES
    # ============================================================

    def get_all_scores(self):
        """
        Get ALL saved games from the database.

        Sorted from highest score to lowest.

        This is used when the user wants to see the
        complete leaderboard history.
        """

        if not self.ensure_connection():
            return []

        cursor = None

        try:
            cursor = self.connection.cursor(dictionary=True)

            cursor.execute("""
                SELECT
                    id,
                    player_name,
                    score,
                    level,
                    line_count,
                    played_at
                FROM game_scores
                ORDER BY
                    score DESC,
                    played_at ASC,
                    id ASC
            """)

            rows = cursor.fetchall()

            return rows

        except Error as e:
            print(f"[DATABASE] All scores read failed: {e}")
            return []

        finally:
            if cursor:
                try:
                    cursor.close()
                except Error:
                    pass

    # ============================================================
    # RECENT SCORES
    # ============================================================

    def get_recent_scores(self, limit=10):
        """
        Get the most recently completed games.
        """

        if not self.ensure_connection():
            return []

        try:
            limit = int(limit)
        except (ValueError, TypeError):
            limit = 10

        limit = max(1, min(limit, 5000))

        sql = f"""
            SELECT
                id,
                player_name,
                score,
                level,
                line_count,
                played_at
            FROM game_scores
            ORDER BY
                played_at DESC,
                id DESC
            LIMIT {limit}
        """

        cursor = None

        try:
            cursor = self.connection.cursor(dictionary=True)

            cursor.execute(sql)

            rows = cursor.fetchall()

            return rows

        except Error as e:
            print(f"[DATABASE] Recent scores read failed: {e}")
            return []

        finally:
            if cursor:
                try:
                    cursor.close()
                except Error:
                    pass

    # ============================================================
    # CLOSE DATABASE
    # ============================================================

    def close(self):
        if self.connection:

            try:
                if self.connection.is_connected():
                    self.connection.close()
                    print("[DATABASE] Connection closed.")

            except Error:
                pass

            self.connection = None