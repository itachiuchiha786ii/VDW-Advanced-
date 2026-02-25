VDW-Advanced – Multi-Platform Video Downloader

VDW-Advanced is a privacy-focused video downloader web application built using Flask.
It supports downloading videos from multiple platforms, merging YouTube audio and video streams, cookie-based authenticated downloads, and includes a statistics dashboard for usage monitoring.

---

OVERVIEW

This project provides a lightweight and efficient backend system for downloading and processing online video content.
It follows a stateless backend architecture focused on performance, simplicity, and scalability.

---

FEATURES

Multi-platform video download support: 
• YouTube
• Facebook
• Instagram
• X (Twitter)
• Other supported platforms

Automatic platform detection from URL
FFmpeg-based merging for YouTube video-only and audio-only streams
Cookie-based authentication for restricted/private content
Usage statistics dashboard
Resolution analytics
Platform usage distribution
Visitor tracking by IP address
Android intent support (MX Player, VLC, KM Player)
Stateless backend design

---

PROJECT STRUCTURE

VDW-Advanced/ │ 
├── app.py
├── requirements.txt
├── readme.txt
├── cookies/
├── static/
├── templates/
└── database files

---

INSTALLATION

1. Clone the repository:
git clone https://github.com/itachiuchiha786ii/VDW-Advanced.git
cd VDW-Advanced

2. Create a virtual environment (recommended):
python3 -m venv venv
source venv/bin/activate
(On Windows: venv\Scripts\activate)

3. Install dependencies:
pip install -r requirements.txt

4. Install FFmpeg (required):
Linux: sudo apt install ffmpeg
Windows: Download FFmpeg from https://ffmpeg.org/download.html
Add FFmpeg to your system PATH.

---

RUNNING THE APPLICATION

Run the application using:
python app.py

Access the application in your browser:
http://localhost:5000

---

DOCKER DEPLOYMENT

You can also run the application using Docker.

1. Build Docker image:
docker build -t vdw-advanced .

2. Run container:
docker run -d -p 5000:5000 --name vdw-app vdw-advanced

3. Access application:
http://localhost:5000

If using Docker Compose:
docker-compose up -d

---

COOKIE CONFIGURATION

To enable authenticated downloads:
Place cookie files in:
cookies/<platform>.cookies.json
Or:
cookies/<platform>.txt

---

YOUTUBE STREAM MERGING

The application uses FFmpeg to merge separate audio and video streams.
Merged files are temporarily stored in SQLite
Files automatically expire after 8 hours

---

DASHBOARD

The dashboard provides:
Video resolution distribution
Platform usage analytics
Visitor tracking by IP

Access:
/dashboard

---

TECHNOLOGY STACK

Backend: Flask (Python)
Frontend: HTML, Tailwind CSS, JavaScript
Database: SQLite
Media Processing: FFmpeg
Charts: Chart.js

---

VPS DEPLOYMENT

1. Deploy on Ubuntu VPS
2. Use tmux or screen to keep the app running
3. Configure Nginx + Gunicorn for production
4. Point your domain or subdomain to VPS IP

---

FUTURE ENHANCEMENTS

Telegram bot integration
Automatic cookie synchronization tool
Android application frontend
Advanced error analytics

---

LICENSE

This project is licensed under the MIT License.
See the LICENSE file for details.
