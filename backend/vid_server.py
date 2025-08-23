from flask import Flask, request, send_from_directory, Response, abort, jsonify, make_response
import os
from db_utils import *
from config.config_utils import *


app = Flask(__name__)
be_conf = Config("config/backend_conf.yaml")
fe_conf = Config("config/frontend_conf.yaml")


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
    to_remove = set()

    # app.run(host="0.0.0.0", port=PORT, threaded=True)
    # app.run(host="127.0.0.1", port=PORT, threaded=True)
