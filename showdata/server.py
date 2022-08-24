from flask import Flask, request, Response, redirect
import mimetypes
import os
from showdata import generate_html_table
from urllib.parse import quote
from flask_cors import CORS
import time


allow_modify = False
show_delete_button = False
show_upload_button = False
index_hide = True
password = "1234"
app = Flask(__name__)
CORS(app)


def get_head_div(full_path):
    sub_path = os.path.relpath(full_path, os.getcwd())
    sub_paths = sub_path.split('/')

    head_div = '<div style="margin:10px">'
    head_div += f"<a href='/'>{os.getcwd().strip('/')}<a>"

    cur_path = ''
    for path in sub_paths:
        cur_path = f"{cur_path}/{path}"
        head_div += f'/<a href="{cur_path}">{path}</a>'
    head_div += "</div>"
    return head_div

def all_images(files):
    exts = ['.jpg', '.png', '.JPEG']
    for file in files:
        if not os.path.splitext(file)[1] in exts:
            return False
    return True
            

def grid_image(files, full_path, head_div):
    cols = 6
    table = []
    row = {"row\col": 0}
    for i, img_path in enumerate(files):
        row[i % cols] = {'src': str(img_path), 'text': str(img_path)+' '}
        if len(row)-1 == cols:
            table.append(row)
            row = {"row\col": i // cols+1}

    if len(row) > 0:
        table.append(row)

    return generate_html_table(table,
                               image_width=256,
                               save=False,
                               rel_path=False,
                               title=full_path,
                               max_str_len=-1,
                               page_size=50,
                               head_div=head_div)


def parse_folder(full_path):
    files = sorted(os.listdir(full_path))
    # 过滤掉python文件
    for ext in [".py", ".cpp", ".ipynb", ".c", ".md"]:
        files = [file for file in files if not file.endswith(ext)]
    head_div = get_head_div(full_path)

    if len(files) > 10000: 
        head_div += f"<div>Total {len(files)} files, only show top 10000 files for speed.</div>"
        files = files[:10000]

    if len(files) > 20 and all_images(files):
        return grid_image(files, full_path, head_div)

    table = []

    row = {}
    print(full_path)
    # row["filename"] = f'<a href="/{os.path.split(full_path[:-1])[0]}"> .. </a>'
    # row["type"] = f"parent folder"
    # row["size"] = f""
    # row["time"] = ''
    # row["content"] = ".."

    # if allow_modify and show_delete_button:
    #     row["delete"] = f''
    # table.append(row)

    row = {}
    if allow_modify and show_upload_button:
        row["filename"] = "upload file"
        row["type"] = f"""
        """
        row["size"] = f""
        row["content"] = f"""
        <div>
        <input id="upload-file" type="file" class="form-control form-control-file" style="display: inline-block; width: 100px;"/>
        <button class="btn btn-sm btn-primary" style="margin-left: 4px"
        onclick="
            let file = document.getElementById('upload-file').files[0];
            let formData = new FormData();
            formData.append('file', file);
            fetch('/{full_path}', {{method: 'POST', body: formData}})
            .then(function(response){{location.reload()}});
        "
        >Confirm Upload</button>
        </div>
        """
        if show_delete_button:
            row["delete"] = f''
        table.append(row)

    for i, file in enumerate(files):
        row = {}
        if os.path.isdir(full_path + '/' + file):
            file = file + '/'
        row["filename"] = f'<a href="{quote(file)}"> {file} </a>'
        row['time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(full_path + '/' + file)))
        row["size"] = f"{os.path.getsize(full_path + '/' + file) / 1024 / 1024:.2f}M"
        row["type"] = f"{os.path.splitext(file)[-1]}"
        row["content"] = file
        if allow_modify and show_delete_button:
            # 不允许删除文件夹
            if os.path.isdir(full_path + '/' + file):
                row["delete"] = ""
            else:
                row["delete"] = f"""<button class="btn btn-danger" onclick="
                fetch('{quote(file)}?action=delete&password={password}', {{method: 'GET'}})
                .then(function(response){{location.reload()}});
                ">Delete</button>"""
        table.append(row)

    table = sorted(table, key=lambda x: x['time'])[::-1]
    return generate_html_table(table,
                               image_width=256,
                               save=False,
                               rel_path=False,
                               title=full_path,
                               max_str_len=-1,
                               page_size=50,
                               head_div=head_div)


@app.route('/', defaults={"subpath": "./"})
@app.route('/<path:subpath>', methods=['GET', 'POST'])
def server(subpath):
    if ".." in subpath or '..' in os.path.relpath(subpath, '.'):
        return 'File Not Found.', 404
    full_path = f'{subpath.strip()}'
    print(full_path)
    if request.method == 'GET':
        action = request.args.get('action', default='download', type=str)
        # 下载文件
        if action == 'download':
            if os.path.exists(full_path):
                if os.path.isdir(full_path):
                    if full_path[-1] != '/':
                        return redirect('/' + full_path + '/')
                    if index_hide and os.path.exists(full_path + 'index.html'):
                        return redirect('/' + full_path + 'index.html')
                    return parse_folder(full_path)
                else:
                    data = open(full_path, 'rb').read()
                    return Response(data, mimetype=mimetypes.guess_type(subpath)[0])
            else:
                return 'File not Found', 404

        # 删除文件
        elif action == 'delete':
            user_password = request.args.get(
                'password', default='1234', type=str)
            if allow_modify and password == user_password:
                if os.path.exists(full_path):
                    os.system('rm -f "%s"' % full_path)
                    return f'Delete {full_path}', 200
                else:
                    return f'{full_path} does not exists', 200
            else:
                return f"Don't allow delete files.", 405

        else:
            return 'Invalid Action', 404

    elif request.method == 'POST':
        # 上传文件
        if 'file' in request.files:
            if not allow_modify:
                return "Don't allow upload files.", 405
            file = request.files['file']
            filename = file.filename

            if not os.path.exists(full_path):
                os.makedirs(full_path, exist_ok=True)

            file.save(os.path.join(full_path, filename))
            return 'Success uploaded!', 200
        else:
            return 'Need file', 404
