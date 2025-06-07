import sqlite3

DB_PATH = "merged_videos.db"  # Or your actual DB path

def get_user_count():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(DISTINCT user_id) FROM merged_videos;")
    result = cursor.fetchone()[0]
    conn.close()
    return result