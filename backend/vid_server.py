import os
from db_utils import *
from vid_utils import *
from config.config_utils import *
from flask import Flask, request, send_from_directory, Response, abort, jsonify, make_response

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
to_remove = set()
be_conf = load_config("config/backend_conf.yaml")
db = DB_Helper(be_conf.paths.DB_PATH)


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
            path = be_conf.paths.VIDS_PATH
            if os.path.isfile(path + title):
                os.remove(path + title)
        to_remove = set()
        vids = preprocess_vids(be_conf.paths.VIDS_PATH, be_conf.preprocess.MODIFY,
                               be_conf.preprocess.PLATFORM, be_conf.preprocess.HIDE)
        db.update_db(vids)
    except Exception as e:
        print(e)
        return make_cors_response(jsonify(status=0, response='Database Update Failed'))
    return make_cors_response(jsonify(status=1, response='Database updated successfully'))


@app.route("/player/metadatas")
def metadatas():
    return make_cors_response(jsonify(db.query_metadatas()))


def update_table(func, args: list):
    try:
        func(*args)
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
    return update_table(db.update_highlights, [vid, timestamp])
    # return update_highlights(vid, timestamp)


@app.route("/player/remove_highlight")
def remove_highlight():
    vid = request.args.get('vid_id')
    timestamp = int(float(request.args.get('timestamp')))
    try:
        res = db.run_sql_cmd(f'''
                                SELECT * FROM highlights
                                WHERE vid_id = {vid} AND timestamp = {timestamp}
                            ''')
        if not res:
            raise
        db.run_sql_cmd(f'''
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
    return make_cors_response(jsonify(db.query_highlights(vid)))


@app.route("/frontend/<filename>")
def page(filename):
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../frontend/")
    print(file_path)
    return send_from_directory(file_path, filename)


@app.route("/vids/<filename>")
def video(filename):
    file_path = os.path.join(be_conf.paths.VIDS_PATH, filename)
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
    app.run(host=be_conf.server.HOST, port=be_conf.server.PORT, threaded=True)
