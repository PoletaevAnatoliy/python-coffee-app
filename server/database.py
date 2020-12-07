import sqlite3


# noinspection SqlNoDataSourceInspection
class BreakagesDatabase:

    def __init__(self, database: str = "breakages.sqlite"):
        self._db = database
        with sqlite3.connect(self._db) as connection:
            cursor = connection.cursor()
            cursor.execute("""CREATE TABLE IF NOT EXISTS breakages (
                              id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                              place TEXT NOT NULL,
                              time INTEGER NOT NULL,
                              description TEXT NOT NULL,
                              engineer_id INTEGER,
                              is_active BOOLEAN NOT NULL);""")
            connection.commit()

    def get_free_breakages(self) -> list:
        with sqlite3.connect(self._db) as connection:
            cursor = connection.cursor()
            result = cursor.execute("""SELECT id, place, time, description
                                       FROM breakages WHERE engineer_id IS NULL;""").fetchall()
        return result

    def add_new_breakage(self, place, time, description) -> bool:
        with sqlite3.connect(self._db) as connection:
            cursor = connection.cursor()
            cursor.execute("""INSERT INTO breakages (place, time, description, engineer_id, is_active)
                              VALUES (?, ?, ?, NULL, FALSE)""", (place, time, description))
            connection.commit()

    def take_breakage(self, breakage_id, engineer_id) -> bool:
        if self._breakage_is_free(breakage_id):
            self._set_breakage_engineer(breakage_id, engineer_id)
            return True
        return False

    def report_breakage_fixed(self, breakage_id):
        with sqlite3.connect(self._db) as connection:
            cursor = connection.cursor()
            cursor.execute("""UPDATE breakages SET is_active=TRUE WHERE id=?""", (breakage_id,))
            connection.commit()

    def _breakage_is_free(self, breakage_id):
        with sqlite3.connect(self._db) as connection:
            cursor = connection.cursor()
            engineer_id = cursor.execute("""SELECT engineer_id FROM breakages WHERE id = ?""",
                                      (breakage_id,)).fetchone()[0]
        return True if engineer_id is None else False

    def _set_breakage_engineer(self, breakage_id, engineer_id):
        with sqlite3.connect(self._db) as connection:
            cursor = connection.cursor()
            cursor.execute("""UPDATE breakages SET engineer_id=? WHERE id=?""", (engineer_id, breakage_id))
            connection.commit()
