"""
支持二级media目录的可视化.
可以读取一个配置文件，确定需要展示的字段.
每个二级目录下的文件名需要相同.
"""

import click
from .utils import get_mp4
from urllib.parse import unquote, quote
from easydict import EasyDict
from showdata import generate_html_table
from flask import Flask, request, Response, redirect
import os
import mimetypes


@click.command()
@click.option("--root-path", default=".")
@click.option("--files", default="")
@click.option("--host", default="0.0.0.0")
@click.option("--port", default=8000)
@click.option("--media-width", default=384)
def main(root_path, files, host, port, media_width):
    files = files.split(',')

    app = Flask(__name__)

    @app.route("/", methods=["GET"])
    def index():
        folders = sorted(os.listdir(root_path))[::-1]

        table = []
        for folder in folders:
            # 跳过文件
            if not os.path.isdir(os.path.join(root_path, folder)):
                continue

            row = {
                "name": folder,
            }
            for file in files:
                quote_path = quote(f"{folder}/{file}")
                if quote_path.endswith('.mp4'):
                    row[file + " "] = f"<video src='/media?path={quote_path}' preload='none' width={media_width} controls>"
                elif quote_path.endswith(".png") or quote_path.endswith(".jpg"):
                    row[file + " "] = f"<image src='/media?path={quote_path}' width={media_width}>"
                elif quote_path.endswith(".mp3") or quote_path.endswith(".wav"):
                    row[file + " "] = f"<audio src='/media?path={quote_path}'>"
            table.append(row)

        table = generate_html_table(table, rel_path=False, max_str_len=200000, page_size=10)

        return table

    @app.route("/media", methods=["GET"])
    def get_media():
        media_path: str = request.args.get("path")
        if '..' in media_path:
            return "Forbidden"
        media_path = os.path.join(root_path, media_path)
        if not os.path.exists(media_path):
            return "Not found."
        if media_path.endswith(".mp4"):
            print(media_path)
            return get_mp4(media_path)
        else:
            with open(media_path, 'rb') as f:
                data = f.read()
            return Response(data, mimetype=mimetypes.guess_type(media_path)[0])

    app.run(host=host, port=port)



if __name__ == '__main__':
    main()
