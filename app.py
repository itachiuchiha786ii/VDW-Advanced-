from flask import Flask, request, render_template, redirect, url_for, jsonify, send_from_directory
import yt_dlp
import os
import uuid
import hashlib
import subprocess
import sqlite3
from urllib.parse import urlparse
from datetime import datetime, timedelta, timezone
import time
from collections import Counter

app = Flask(__name__)

MERGED_DIR = "merged"
DB_FILE = "download.db"
os.makedirs(MERGED_DIR, exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS merged_videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_url TEXT,
            resolution TEXT,
            merged_path TEXT,
            created_at TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS visitor_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS platform_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT,
            video_url TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

def log_visitor_ip():
    ip_address = request.remote_addr
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM visitor_logs WHERE ip_address = ? AND timestamp >= datetime('now', '-10 minutes')", (ip_address,))
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO visitor_logs (ip_address) VALUES (?)", (ip_address,))
        conn.commit()
    conn.close()

def detect_platform(video_url):
    domain = urlparse(video_url).netloc.replace("www.", "")
    return domain.split('.')[0].capitalize()

def log_platform_usage(video_url):
    platform = detect_platform(video_url)
    conn = sqlite3.connect(DB_FILE)
    conn.execute("INSERT INTO platform_logs (platform, video_url) VALUES (?, ?)", (platform, video_url))
    conn.commit()
    conn.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/stream")
def stream():
    log_visitor_ip()
    return render_template("stream.html")

@app.route('/get_video_info', methods=['POST'])
def get_video_info():
    data = request.get_json()
    video_url = data.get("video_url")
    if not video_url:
        return jsonify({"error": "Missing video_url"}), 400

    cookies_file = None
    if "facebook.com" in video_url:
        cookies_file = "cookies/www.facebook.com.txt"
    elif "x.com" in video_url or "twitter.com" in video_url:
        cookies_file = "cookies/x.com.txt"
    elif "instagram.com" in video_url:
        cookies_file = "cookies/www.instagram.com.txt"

    try:
        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "forcejson": True,
        }

        if cookies_file:
            ydl_opts["cookiefile"] = cookies_file

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)

        video_id = hashlib.md5(info["title"].encode()).hexdigest()

        formats = []
        for f in info.get("formats", []):
            f["is_video_only"] = (f.get("vcodec") != "none" and f.get("acodec") == "none")
            f["is_audio_only"] = (f.get("acodec") != "none" and f.get("vcodec") == "none")
            f["quality"] = f.get("format_note") or f.get("height") or f.get("format_id")

            formats.append(f)

        return jsonify({
            "video_id": video_id,
            "title": info.get("title"),
            "description": info.get("description"),
            "platform": info.get("extractor"),
            "formats": formats,
            "video_url": video_url
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/merge_video", methods=["POST"])
def merge_video():
    data = request.get_json()
    video_url = data.get("video_url")
    resolution = data.get("resolution")
    formats = data.get("formats")

    if not video_url or not resolution or not formats:
        return jsonify({"error": "Missing data"}), 400

    log_platform_usage(video_url)

    conn = sqlite3.connect(DB_FILE)
    threshold = (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat()
    conn.execute("DELETE FROM merged_videos WHERE created_at <= ?", (threshold,))
    conn.commit()

    row = conn.execute("""
        SELECT merged_path FROM merged_videos
        WHERE video_url = ? AND resolution = ?
    """, (video_url, resolution)).fetchone()

    if row:
        filename = os.path.basename(row[0])
        conn.close()
        return jsonify({"url": f"/merged/{filename}"})

    try:
        temp_id = uuid.uuid4().hex
        video_file = f"temp_{temp_id}_video.mp4"
        audio_file = f"temp_{temp_id}_audio.m4a"
        output_file = os.path.join(MERGED_DIR, f"{temp_id}_{resolution}.mp4")

        # Safely match resolution (exact height or note like '720p')
        video_format = next(
            (f for f in formats if f.get("is_video_only") and (
                str(resolution) in str(f.get("height")) or
                str(resolution) in str(f.get("format_note", "")).lower()
            )),
            None
        )
        audio_format = next((f for f in formats if f.get("is_audio_only")), None)

        if not video_format or not audio_format:
            return jsonify({"error": "Requested format is not available"}), 500

        video_format_id = video_format["format_id"]
        audio_format_id = audio_format["format_id"]

        # Debug log
        print(f"Selected video format: {video_format_id}, audio format: {audio_format_id}")

        with yt_dlp.YoutubeDL({
            "quiet": True,
            "outtmpl": video_file,
            "format": video_format_id,
        }) as ydl:
            ydl.download([video_url])

        with yt_dlp.YoutubeDL({
            "quiet": True,
            "outtmpl": audio_file,
            "format": audio_format_id,
        }) as ydl:
            ydl.download([video_url])

        if not os.path.exists(video_file) or not os.path.exists(audio_file):
            raise Exception("Failed to download video or audio")

        command = [
            "ffmpeg", "-y", "-i", video_file, "-i", audio_file,
            "-c:v", "copy", "-c:a", "aac", output_file
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode != 0:
            raise Exception(f"FFmpeg error: {result.stderr.decode()}")

        if os.path.exists(output_file):
            conn.execute("""
                INSERT INTO merged_videos (video_url, resolution, merged_path, created_at)
                VALUES (?, ?, ?, ?)
            """, (video_url, resolution, output_file, datetime.now(timezone.utc).isoformat()))
            conn.commit()

        os.remove(video_file) if os.path.exists(video_file) else None
        os.remove(audio_file) if os.path.exists(audio_file) else None

        filename = os.path.basename(output_file)
        return jsonify({"url": f"/merged/{filename}"})

    except Exception as e:
        print(f"Error merging video: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route("/merged/<filename>")
def serve_merged(filename):
    return send_from_directory(MERGED_DIR, filename)

def get_total_visitors():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(DISTINCT ip_address) FROM visitor_logs")
    result = cursor.fetchone()[0]
    conn.close()
    return result

def get_videos_by_platform():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT platform FROM platform_logs")
    rows = cursor.fetchall()
    conn.close()
    counter = Counter([row[0] for row in rows])
    return dict(counter)

def get_videos_by_resolution():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT resolution FROM merged_videos")
    rows = cursor.fetchall()
    conn.close()
    counter = Counter([row[0] for row in rows])
    return dict(counter)

@app.route("/dashboard")
def dashboard():
    total_visitors = get_total_visitors()
    videos_by_platform = get_videos_by_platform()
    videos_by_resolution = get_videos_by_resolution()

    if videos_by_platform:
        import matplotlib.pyplot as plt
        labels = list(videos_by_platform.keys())
        sizes = list(videos_by_platform.values())
        colors = plt.cm.Paired.colors[:len(labels)]

        plt.figure(figsize=(4, 4))
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%')
        plt.title('Platform Usage')

        pie_chart_path = os.path.join("static", "platform_pie.png")
        plt.savefig(pie_chart_path, bbox_inches='tight')
        plt.close()

    chart_version = int(time.time())

    return render_template("dashboard.html",
                           total_visitors=total_visitors,
                           videos_by_platform=videos_by_platform,
                           videos_by_resolution=videos_by_resolution,
                           chart_version=chart_version)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)