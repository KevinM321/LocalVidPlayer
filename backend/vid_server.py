from flask import Flask, request, send_from_directory, Response, abort, jsonify, make_response
import os
import sqlite3


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


app = Flask(__name__)

to_remove = set()
setup_db()


def make_cors_response(content):
    response = make_response(content)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


@app.route("/player/remove", methods=['POST', 'OPTIONS'])
def remove():
    if request.method == 'OPTIONS':
        response = make_cors_response('')
        return response

    global to_remove
    try:
        to_remove.add(request.json.get('value'))
    except:
        return make_cors_response(jsonify({"status": 0, "response": "Command Failed"}))
    return make_cors_response(jsonify({"status": 1, "response": "Command Successful"}))


@app.route("/player/reload")
def reload():
    global to_remove
    try:
        for title in to_remove:
            path = config.resource_path + 'vids/'
            if os.path.isfile(path + title):
                os.remove(path + title)
        to_remove = set()
        update_db()
    except Exception as e:
        return make_cors_response(jsonify(status=0, response='Database Update Failed'))
    return make_cors_response(jsonify(status=1, response='Database updated successfully'))


@app.route("/player/metadatas")
def metadatas():
    return make_cors_response(jsonify(query_metadatas()))


def update_metadatas(setting, cmd):
    try:
        idx = int(cmd.get('id'))
        val = int(cmd.get('value'))
        conn = sqlite3.connect(DB_PATH)
        conn.cursor().execute(f'''
            UPDATE metadatas
            SET {setting} = ?
            WHERE id = ?
        ''', (val, idx))
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)
        return make_cors_response(jsonify({"status": 0, "response": "Command Failed"}))
    return make_cors_response(jsonify({"status": 1, "response": "Command Successful"}))


def update_highlights(vid, timestamp):
    try:
        conn = sqlite3.connect(DB_PATH)
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
    except Exception as e:
        print(e)
        return make_cors_response(jsonify({"status": 0, "response": "Command Failed"}))
    return make_cors_response(jsonify({"status": 1, "response": "Command Successful"}))


@app.route("/player/volume", methods=['POST', 'OPTIONS'])
def volume():
    if request.method == 'OPTIONS':
        response = make_cors_response('')
        return response
    return update_metadatas('volume', request.json)


@app.route("/player/start_t", methods=['POST', 'OPTIONS'])
def start_t():
    if request.method == 'OPTIONS':
        response = make_cors_response('')
        return response
    return update_metadatas('start_t', request.json)


@app.route("/player/rotation", methods=['POST', 'OPTIONS'])
def rotation():
    if request.method == 'OPTIONS':
        response = make_cors_response('')
        return response
    return update_metadatas('rotation', request.json)


@app.route("/player/reflection_x", methods=['POST', 'OPTIONS'])
def reflection_x():
    if request.method == 'OPTIONS':
        response = make_cors_response('')
        return response
    return update_metadatas('reflection_x', request.json)


@app.route("/player/reflection_y", methods=['POST', 'OPTIONS'])
def reflection_y():
    if request.method == 'OPTIONS':
        response = make_cors_response('')
        return response
    return update_metadatas('reflection_y', request.json)


@app.route("/player/scale", methods=['POST', 'OPTIONS'])
def scale():
    if request.method == 'OPTIONS':
        response = make_cors_response('')
        return response
    return update_metadatas('scale', request.json)


@app.route("/player/zoom", methods=['POST', 'OPTIONS'])
def zoom():
    if request.method == 'OPTIONS':
        response = make_cors_response('')
        return response
    return update_metadatas('zoom', request.json)


@app.route("/player/add_highlight", methods=['GET', 'POST', 'OPTIONS'])
def add_highlight():
    if request.method == 'OPTIONS':
        response = make_cors_response('')
        return response
    if request.method == 'GET':
        vid = request.args.get('vid_id')
        timestamp = int(float(request.args.get('timestamp')))
    else:
        cmd = request.json
        vid = cmd['id']
        timestamp = int(float(cmd['value']))
    return update_highlights(vid, timestamp)


@app.route("/player/remove_highlight")
def remove_highlight():
    vid = request.args.get('vid_id')
    timestamp = int(float(request.args.get('timestamp')))
    try:
        res = run_sql_cmd(f'''
            SELECT * FROM highlights
            WHERE vid_id = {vid} AND timestamp = {timestamp}
        ''')
        if not res:
            raise
        run_sql_cmd(f'''
            DELETE FROM highlights
            WHERE vid_id = {vid} AND timestamp = {timestamp}
        ''')
    except Exception as e:
        print(e)
        return make_cors_response(jsonify({"status": 0, "response": "Command Failed"}))
    return make_cors_response(jsonify({"status": 1, "response": "Command Successful"}))


@app.route("/player/get_highlight")
def get_highlight():
    vid = request.args.get('vid_id')
    return make_cors_response(jsonify(query_highlights(vid)))


@app.route("/code/<filename>")
def page(filename):
    file_path = os.path.join(CODE_DIR, filename)
    if not os.path.isfile(file_path):
        abort(404)
    return send_from_directory(CODE_DIR, filename)


@app.route("/vids/<filename>")
def video(filename):
    file_path = os.path.join(VIDEO_DIR, filename)
    if not os.path.isfile(file_path):
        abort(404)

    range_header = request.headers.get('Range', None)
    file_size = os.path.getsize(file_path)
    start = 0
    end = file_size - 1

    if range_header:
        try:
            bytes_range = range_header.strip().split("=")[-1]
            start_str, end_str = bytes_range.split("-")
            if start_str:
                start = int(start_str)
            if end_str:
                end = int(end_str)
        except ValueError:
            abort(400)

    length = end - start + 1

    def generate():
        with open(file_path, 'rb') as f:
            f.seek(start)
            while True:
                data = f.read(8192)
                if not data:
                    break
                yield data

    resp = Response(generate(), status=206 if range_header else 200, mimetype="video/mp4")
    resp.headers.add("Content-Range", f"bytes {start}-{end}/{file_size}")
    resp.headers.add("Accept-Ranges", "bytes")
    resp.headers.add("Content-Length", str(length))
    return resp


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, threaded=True)
    # app.run(host="127.0.0.1", port=PORT, threaded=True)
