
# ðŸŽ¥ AI-Powered Video Downloader Website

This is a fully functional, privacy-focused video downloader platform built using **Flask**, enhanced with **AI-powered platform detection**, **YouTube video-audio merging**, **cookie support**, and a **statistics dashboard** to monitor usage trends.

## ðŸš€ Features

- âœ… Download videos from multiple platforms: YouTube, Facebook, Instagram, X (Twitter), and more.
- ðŸ” AI-based platform detection for pasted URLs.
- ðŸ”„ Backend **FFmpeg merging** for YouTube audio+video.
- ðŸ“Š Dashboard with resolution/platform stats and visitor tracking.
- ðŸª Custom cookie injection for authenticated downloads (e.g., private videos).
- ðŸŽ¬ One-click playback on MX Player / VLC / KM Player (Android intent links).
- ðŸŒ Stateless, sessionless backend for better performance and simplicity.

## ðŸ› ï¸ Installation

### 1. Clone the Repo
```bash
git clone https://github.com/itachiuchiha786ii/VDW-Advanced.git
cd VDW-Advanced
```

### 2. Create a Virtual Environment (optional but recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install FFmpeg (Required)
- **Linux**: `sudo apt install ffmpeg`
- **Windows**: [Download FFmpeg](https://ffmpeg.org/download.html), and add to PATH

## â–¶ï¸ Running the App

```bash
python app.py
```

Visit `http://localhost:5000` or your server IP.

## ðŸ” Cookie Setup

For platforms like Facebook, Instagram, or X, place your cookies in:
```
/cookies/<platform>.cookies.json
```

Or use `.txt` cookie formats if needed:
```
/cookies/<platform>.txt
```

## ðŸŽžï¸ YouTube Audio + Video Merge

The app uses FFmpeg to merge **video-only** and **audio-only** streams for YouTube. The merged files are stored in a SQLite DB and expire after 8 hours automatically.

## ðŸ“Š Dashboard Features

- Merged video resolution breakdown
- Platform usage pie chart
- Visitor tracking (by IP)

Visit: `/dashboard` on your deployment

## ðŸ§  AI Features

- Auto-detects supported platforms from any URL
- Friendly, readable error messages when something goes wrong

## ðŸ’» Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **Database**: SQLite
- **Media Processing**: FFmpeg
- **Charts**: Chart.js

## ðŸ“¡ VPS Deployment

1. Deploy on any Ubuntu VPS.
2. Use `tmux` or `screen` to keep it running in background.
3. Set up Nginx + Gunicorn (optional) for production.
4. Point domain or subdomain to VPS IP.

## ðŸ§ª Future Plans

- Telegram bot integration
- Auto cookie sync tool
- Android app frontend
- Error analytics

## ðŸ“„ License

This project is licensed under the **MIT License**.
See the [LICENSE](LICENSE) file for details.
