import sqlite3


def test():
    return "hi"

def setup_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # cursor.execute('''
    #     CREATE TABLE IF NOT EXISTS metadatas (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         title TEXT UNIQUE NOT NULL,
    #         volume INTEGER NOT NULL DEFAULT 50 CHECK(volume >= 0 AND volume <= 100),
    #         start_t INTEGER NOT NULL DEFAULT 0 CHECK(start_t >= 0),
    #         rotation INTEGER NOT NULL DEFAULT 0 CHECK(rotation >= 0 AND rotation <= 359),
    #         create_t DATETIME NOT NULL DEFAULT 0 CHECK(create_t >= 0),
    #         scale INTEGER NOT NULL DEFAULT 100 CHECK(scale >= 10 AND scale <= 300),
    #         zoom INTEGER NOT NULL DEFAULT 0,
    #         reflection_x INTEGER NOT NULL DEFAULT 1 CHECK(reflection_x == 1 OR reflection_x == -1),
    #         reflection_y INTEGER NOT NULL DEFAULT 1 CHECK(reflection_y == 1 OR reflection_y == -1)
    #     )
    # ''')

    # cursor.execute('''
    #     CREATE TABLE IF NOT EXISTS tags (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         name TEXT UNIQUE
    #     )
    # ''')
    #
    # cursor.execute('''
    #     CREATE TABLE IF NOT EXISTS video_tags (
    #         vid_id INTEGER,
    #         tag_id INTEGER,
    #         FOREIGN KEY (vid_id) REFERENCES metadatas(id),
    #         FOREIGN KEY (tag_id) REFERENCES tags(id),
    #         PRIMARY KEY (vid_id, tag_id)
    #     )
    # ''')

    # cursor.execute('''
    #     DROP TABLE IF EXISTS highlights
    # ''')
    # cursor.execute('''
    #     CREATE TABLE IF NOT EXISTS highlights (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         vid_id INTEGER NOT NULL,
    #         timestamp INTEGER NOT NULL,
    #         FOREIGN KEY (vid_id) REFERENCES metadatas(id),
    #         UNIQUE (vid_id, timestamp) ON CONFLICT FAIL
    #     )
    # ''')

    # cursor.execute("PRAGMA table_info(metadatas)")
    # columns = cursor.fetchall()
    # for i, col in enumerate(columns):
    #     print(f"Column {i} name: {col[1]}, Type: {col[2]}")

    # cursor.execute("PRAGMA table_info(video_tags)")
    # columns = cursor.fetchall()
    # for i, col in enumerate(columns):
    #     print(f"Column {i} name: {col[1]}, Type: {col[2]}")
    #
    cursor.execute("PRAGMA table_info(highlights)")
    columns = cursor.fetchall()
    for i, col in enumerate(columns):
        print(f"Column {i} name: {col[1]}, Type: {col[2]}")

    conn.commit()
    conn.close()




def query_metadatas():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.cursor().execute('''
        SELECT *
        FROM metadatas
        ORDER BY create_t DESC
    ''').fetchall()
    conn.close()

    results = []
    datas = ['id', 'title', 'volume', 'start_t', 'rotation', 'create_t',
             'scale', 'zoom', 'reflection_x', 'reflection_y']
    for row in rows:
        results.append({datas[i]: row[i] for i in range(len(datas))})
    return results


def update_db():
    conn = sqlite3.connect(DB_PATH)

    vids = generator.get_vids()
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


def query_highlights(vid):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.cursor().execute(f'''
        SELECT * 
        FROM highlights 
        WHERE vid_id = {vid}
        ORDER BY timestamp ASC
    ''').fetchall()
    conn.close()
    return [row[2] for row in rows]


def run_sql_cmd(cmd):
    conn = sqlite3.connect(DB_PATH)
    res = conn.cursor().execute(cmd).fetchall()
    conn.commit()
    conn.close()
    return res
