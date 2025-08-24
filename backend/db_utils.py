import sqlite3


class DB_Helper:
    def __init__(self, path: str):
        self._path = path
        self.setup_db()


    def change_path(self, path: str):
        self._path = path


    def check_table(self, cursor: sqlite3.Cursor, name: str) -> list:
        cursor.execute(f"PRAGMA table_info({name})")
        columns = cursor.fetchall()
        return columns


    def setup_db(self):
        conn = sqlite3.connect(self._path)
        cursor = conn.cursor()

        self.create_metadatas(cursor)
        self.create_highlights(cursor)

        conn.commit()
        conn.close()


    def create_metadatas(self, cursor: sqlite3.Cursor):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metadatas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT UNIQUE NOT NULL,
                type TEXT NOT NULL DEFAULT "mp4",
                volume INTEGER NOT NULL DEFAULT 50 CHECK(volume >= 0 AND volume <= 100),
                start_t INTEGER NOT NULL DEFAULT 0 CHECK(start_t >= 0),
                rotation INTEGER NOT NULL DEFAULT 0 CHECK(rotation >= 0 AND rotation <= 359),
                create_t DATETIME NOT NULL DEFAULT 0 CHECK(create_t >= 0),
                scale INTEGER NOT NULL DEFAULT 100 CHECK(scale >= 10 AND scale <= 300),
                zoom INTEGER NOT NULL DEFAULT 0,
                reflection_x INTEGER NOT NULL DEFAULT 1 CHECK(reflection_x == 1 OR reflection_x == -1),
                reflection_y INTEGER NOT NULL DEFAULT 1 CHECK(reflection_y == 1 OR reflection_y == -1)
            )
        ''')


    def create_tags(self, cursor: sqlite3.Cursor):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE
            )
        ''')


    def create_video_tags(self, cursor: sqlite3.Cursor):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_tags (
                vid_id INTEGER,
                tag_id INTEGER,
                FOREIGN KEY (vid_id) REFERENCES metadatas(id),
                FOREIGN KEY (tag_id) REFERENCES tags(id),
                PRIMARY KEY (vid_id, tag_id)
            )
        ''')


    def create_highlights(self, cursor: sqlite3.Cursor):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS highlights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vid_id INTEGER NOT NULL,
                timestamp INTEGER NOT NULL,
                FOREIGN KEY (vid_id) REFERENCES metadatas(id),
                UNIQUE (vid_id, timestamp) ON CONFLICT FAIL
            )
        ''')


    def query_metadatas(self) -> list:
        conn = sqlite3.connect(self._path)
        rows = conn.cursor().execute('''
            SELECT *
            FROM metadatas
            ORDER BY create_t DESC
        ''').fetchall()
        conn.close()

        results = []
        datas = ['id', 'title', 'type', 'volume', 'start_t', 'rotation', 'create_t',
                 'scale', 'zoom', 'reflection_x', 'reflection_y']
        for row in rows:
            results.append({datas[i]: row[i] for i in range(len(datas))})
        return results


    def query_highlights(self, vid: int) -> list:
        conn = sqlite3.connect(self._path)
        rows = conn.cursor().execute(f'''
            SELECT * 
            FROM highlights 
            WHERE vid_id = {vid}
            ORDER BY timestamp ASC
        ''').fetchall()
        conn.close()
        return [row[2] for row in rows]


    def update_db(self, vids: list):
        conn = sqlite3.connect(self._path)
        titles = []
        for title, create_t in vids:
            titles.append(title)
            conn.cursor().execute('''
                        INSERT OR IGNORE INTO metadatas (title, create_t)
                        VALUES (?, ?)
                    ''', (title, create_t))

        placeholders = ",".join("?" * len(titles))
        conn.cursor().execute(f'''
                DELETE FROM metadatas
                WHERE title NOT IN ({placeholders})
            ''', titles)

        conn.cursor().execute('''
            DELETE FROM highlights 
            WHERE vid_id NOT IN (select id FROM metadatas)
        ''')
        conn.commit()
        conn.close()


    def update_metadatas(self, setting: str, cmd):
        idx = int(cmd.get('id'))
        val = int(cmd.get('value'))
        conn = sqlite3.connect(self._path)
        conn.cursor().execute(f'''
            UPDATE metadatas
            SET {setting} = ?
            WHERE id = ?
        ''', (val, idx))
        conn.commit()
        conn.close()


    def update_highlights(self, vid: int, timestamp: str):
        conn = sqlite3.connect(self._path)
        conn.cursor().execute(
            "SELECT 1 FROM highlights WHERE vid_id = ? AND timestamp = ? LIMIT 1",
            (vid, timestamp)
        )
        exists = conn.cursor().fetchone()
        if not exists:
            conn.cursor().execute(
                "INSERT INTO highlights (vid_id, timestamp) VALUES (?, ?)",
                (vid, timestamp)
            )
        conn.commit()


    def run_sql_cmd(self, cmd: str) -> list:
        conn = sqlite3.connect(self._path)
        res = conn.cursor().execute(cmd).fetchall()
        conn.commit()
        conn.close()
        return res
