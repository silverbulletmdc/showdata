from flask import Flask, request, Response
import mimetypes
import os
from showdata import generate_html_table
from flask_cors import CORS
app = Flask(__name__)
CORS(app)


def parse_folder(full_path):
    files = sorted(os.listdir(full_path))
    table = []
    for i, file in enumerate(files):
        row = {}
        if os.path.isdir(full_path + '/' + file):
            file = file + '/'
        row["filename"] = f'<a href="{file}"> {file} </a>'
        row["type"] = f"{os.path.splitext(file)[-1]}"
        row["size"] = f"{os.path.getsize(full_path + '/' + file) / 1024:.2f}K"
        row["content"] = file
        table.append(row)

    return generate_html_table(table, image_width=400, save=False, rel_path=False, title=full_path, max_str_len=-1)


@app.route('/', defaults={"subpath": "."})
@app.route('/<path:subpath>')
def server(subpath):
    full_path = f'{subpath.strip()}'
    if os.path.exists(full_path):
        if os.path.isdir(full_path):
            return parse_folder(full_path)
        else:
            data = open(full_path, 'rb').read()
            resp = Response(data, mimetype=mimetypes.guess_type(subpath)[0])
    else:
        resp = 'File not Found', 404
    return resp
