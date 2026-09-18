from flask import Flask, request, render_template_string, send_file, url_for
import yt_dlp
import os
import time

app = Flask(__name__)

DOWNLOAD_FOLDER = "/storage/emulated/0/Movies"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# ---------------- HTML MAIN ----------------
HTML = """
<!doctype html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ទាញយកវីដេអូ</title>
    <style>
        * { box-sizing:border-box; }
        html, body { width:100%; min-height:100%; }
        body { margin:0; font-family:Arial,sans-serif; color:#fff; text-align:center; background:#000; padding:clamp(10px,3vw,30px); }
        h2 { color:#1FD91F; font-size:20px; text-shadow:2px 2px 5px #000; }
        h100 { color: #00fff1; font-size: 18px; text-shadow: 2px 2px 5px #000; display:block; margin-top:15px; }       
        form { width:min(100%,520px); margin:15px auto 0; padding:clamp(14px,4vw,22px); background:rgba(255,255,255,0.1); border-radius:15px; }
        input[type="text"], select { padding:12px; border-radius:10px; width:100%; max-width:100%; border:none; font-size:16px; }
        input[type="submit"] { margin:15px auto 0; padding:10px 20px; width:min(100%,360px); min-height:48px; border:none; background:#1565c0; color:white; font-size:20px; border-radius:10px; cursor:pointer; display:flex; align-items:center; justify-content:center; }
        input[type="submit"]:hover { background:#0d47a1; }
        a.folder-link { display:flex; align-items:center; justify-content:center; margin:20px auto 0; padding:8px 15px; width:min(100%,360px); min-height:48px; background:#43a047; color:white; border-radius:10px; text-decoration:none; }
        a.folder-link:hover { background:#2e7d32; }
        .video-preview { width:100%; max-width:680px; height:auto; margin-top:20px; border:4px solid #fff; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.7); }
        .video-container { display:flex; flex-direction:column; align-items:center; justify-content:center; gap:15px; width:100%; margin-top:20px; }
        .download-btn { display:flex; align-items:center; justify-content:center; width:min(100%,360px); min-height:48px; padding:10px 20px; background:#4caf50; color:white; border-radius:8px; text-decoration:none; font-size:18px; }
        .download-btn:hover { background:#2e7d32; }
        .error-msg { color:red; margin-top:20px; font-size:16px; }
        .info { color:#ffd700; margin-top:10px; font-size:16px; }
        button.reload-btn { width:min(100%,360px); min-height:48px; padding:10px 25px; font-size:18px; display:block; margin:20px auto 0; border:none; background:#4caf50; color:white; border-radius:8px; cursor:pointer; margin-top:20px; }
        button.reload-btn:hover { background:#388e3c; }
    </style>
</head>
<body>
<h2>🌐 ទាញយកវីដេអូ </h2>

<form method="post">
    🔗 URL: <input type="text" name="url" required><br><br>
    📂 Resolution:
    <select name="resolution">
        <option value="144">144p</option>
        <option value="240">240p</option>
        <option value="360">360p</option>
        <option value="480">480p</option>
        <option value="720" selected>720p</option>
        <option value="1080">1080p</option>
    </select><br><br>
    <input type="submit" value="⚡ Download">
</form>

<a href="{{ url_for('list_downloads') }}" class="folder-link">📂 មើលឯកសារ Downloads</a>

{% if error %}
    <div class="error-msg">❌ Error: {{ error }}</div>
{% endif %}

{% if file %}
    <h3>✅ Download Completed:</h3>
    <div class="info">⏳ Time: {{ time_taken }} seconds</div>
    <div class="info">📦 Size: {{ file_size }} MB</div>
    <div class="info">⚡ Speed: {{ speed }} KB/s</div>

    <div class="video-container">
        <video class="video-preview" controls>
            <source src="{{ file }}" type="video/mp4">
        </video>
        <a href="{{ file }}" download class="download-btn">⬇️ Download {{ filename }}</a>
    </div>

    <button class="reload-btn" onclick="window.location.href='/'">🔄 Download New Video</button>
{% endif %}
</body>
</html>
"""

# ---------------- FOLDER VIEW ----------------
FOLDER_HTML = """
<!doctype html>
<html>
<head>
    <title>📂 Downloads Folder</title>
    <style>
        body { background:#000; color:#fff; font-family:Arial; text-align:center; padding:20px; }
        h2 { color:#ffd700; }
        .file-item { display:flex; justify-content:space-between; align-items:center; background:#333; padding:10px 15px; margin:10px auto; width:90%; max-width:800px; border-radius:8px; }
        .file-name { overflow:hidden; white-space:nowrap; text-overflow:ellipsis; max-width:60%; }
        .file-actions a { margin-left:5px; padding:8px 15px; border-radius:5px; text-decoration:none; color:white; }
        .btn-preview { background:#4caf50; }
        .btn-download { background:#2196f3; }
        .btn-preview:hover { background:#2e7d32; }
        .btn-download:hover { background:#0b79d0; }
        a.back { display:block; margin-top:20px; padding:10px 20px; background:#2196f3; color:#fff; border-radius:8px; text-decoration:none; width:100px; margin-left:auto; margin-right:auto; }
        a.back:hover { background:#0b79d0; }
    </style>
</head>
<body>
    <h2>📂 File Downloads</h2>
    {% if files %}
        {% for f in files %}
            <div class="file-item">
                <div class="file-name">{{ f }}</div>
                <div class="file-actions">
                    <a href="{{ url_for('preview_video', filename=f) }}" class="btn-preview">▶️ មើលមុន</a>
                    <a href="{{ url_for('download_file', filename=f) }}" class="btn-download">⬇️ Download</a>
                </div>
            </div>
        {% endfor %}
    {% else %}
        <p>❌ មិនទាន់មានឯកសារទេ</p>
    {% endif %}
    <a href="/" class="back">⬅️ Back</a>
</body>
</html>
"""

# ---------------- PREVIEW PAGE (បន្ថែម FILE SIZE) ----------------
PREVIEW_HTML = """
<!doctype html>
<html>
<head>
    <title>🎬 Preview {{ filename }}</title>
    <style>
        body {
            background:#000;
            color:#fff;
            text-align:center;
            font-family:Arial;
            padding:30px;
        }
        h2 {
            font-size:22px;
            color:#ffd700;
            margin-bottom:10px;
        }
        .video-container {
            display:flex;
            flex-direction:column;
            align-items:center;
            justify-content:center;
            margin-top:10px;
        }
        video {
            width:90%;
            max-width:900px;
            height:auto;
            border-radius:12px;
            box-shadow:0 4px 20px rgba(0,0,0,0.7);
        }
        .download-btn {
            margin-top:20px;
            padding:12px 30px;
            background:#4caf50;
            color:white;
            border-radius:8px;
            text-decoration:none;
            font-size:20px;
            font-weight:bold;
            box-shadow:0 4px 10px rgba(0,0,0,0.5);
            transition:all 0.2s ease;
        }
        .download-btn:hover {
            background:#2e7d32;
            transform:scale(1.05);
        }
        a.back {
            display:inline-block;
            margin-top:25px;
            padding:10px 25px;
            background:#2196f3;
            color:#fff;
            border-radius:8px;
            text-decoration:none;
            font-size:18px;
        }
        a.back:hover {
            background:#0b79d0;
        }
    </style>
</head>
<body>
    <h2>🎬 Preview: {{ filename }}</h2>
    <p style="color:#1FD91F; font-size:18px;">📦 File Size: {{ file_size }} MB</p>
    <div class="video-container">
        <video src="{{ url_for('download_file', filename=filename) }}" controls autoplay loop></video>
        <a href="{{ url_for('download_file', filename=filename) }}" class="download-btn">⬇️ Download Video</a>
    </div>
    <a href="{{ url_for('list_downloads') }}" class="back">⬅️ Back</a>
</body>
</html>
"""

# ---------------- MAIN FUNCTIONS ----------------
def download_hook(d):
    pass

@app.route('/', methods=['GET', 'POST'])
def index():
    file_path = None
    filename = None
    error = None
    time_taken = None
    file_size = None
    speed = None

    if request.method == 'POST':
        url = request.form.get('url')
        resolution = request.form.get('resolution', '480')
        start_time = time.time()

        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
            title = info.get('title', 'downloaded')
        except Exception as e:
            error = f"Failed to fetch video info: {e}"
            title = 'downloaded'

        safe_title = "".join(
            c if c.isalnum() or c in " ._-" or '\u1780' <= c <= '\u17FF' else "_"
            for c in title
        )
        filename = f"{safe_title}.mp4"
        full_path = os.path.join(DOWNLOAD_FOLDER, filename)

        if not os.path.exists(full_path):
            ydl_opts = {
    'format': f"bestvideo[height<={resolution}][ext=mp4]+bestaudio[ext=m4a]/mp4",

    # = -S "vcodec:h264,lang,quality,res,fps,hdr:12,acodec:aac"
    'format_sort': [
        'vcodec:h264',
        'lang',
        'quality',
        'res',
        'fps',
        'hdr:12',
        'acodec:aac'
    ],

    # = --merge-output-format mp4
    'merge_output_format': 'mp4',

    # = --remux-video mp4
    'remuxvideo': 'mp4',

    'outtmpl': full_path,
    'progress_hooks': [download_hook],
    'noplaylist': True,
    'quiet': True
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
            except Exception as e:
                error = f"Failed to download video: {e}"
                filename = None

        end_time = time.time()
        if os.path.exists(full_path):
            file_path = f"/downloads/{filename}"
            time_taken = round(end_time - start_time, 2)
            size_bytes = os.path.getsize(full_path)
            file_size = round(size_bytes / (1024*1024), 2)
            avg_speed_bytes = size_bytes / max(time_taken, 1)
            speed = round(avg_speed_bytes / 1024, 2)

    return render_template_string(HTML, file=file_path, filename=filename, error=error,
                                  time_taken=time_taken, file_size=file_size, speed=speed)

@app.route('/downloads')
def list_downloads():
    files = os.listdir(DOWNLOAD_FOLDER)
    return render_template_string(FOLDER_HTML, files=files)

@app.route('/downloads/<path:filename>')
def download_file(filename):
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found", 404

@app.route('/preview/<path:filename>')
def preview_video(filename):
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return "File not found", 404
    size_bytes = os.path.getsize(file_path)
    file_size = round(size_bytes / (1024 * 1024), 2)
    return render_template_string(PREVIEW_HTML, filename=filename, file_size=file_size)

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
