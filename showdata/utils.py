from flask import Flask, request, Response, redirect

def generate_chunks(file_path, chunk_size=32*1024):
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk

def get_mp4(video_path):
    return Response(generate_chunks(video_path), mimetype="video/mp4", headers={
        'Accept-Ranges': 'bytes'  # 告知浏览器支持范围请求
    })