    <script>
document.addEventListener("DOMContentLoaded", async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const videoUrl = urlParams.get("video_url");
    const videoId = urlParams.get("video_id");

    if (!videoUrl || !videoId) return;

    const storedData = sessionStorage.getItem("videoData");
    if (!storedData) return;

    let videoData = JSON.parse(storedData);

    const videoElement = document.getElementById("onlineVideo");
    const videoSource = document.getElementById("videoSource");

    const firstPlayable = videoData.formats.find(f => f.vcodec !== "none" && f.acodec !== "none");

    if (firstPlayable) {
        videoSource.src = firstPlayable.url;
        videoElement.load();
    }

    const getLabel = (format) => {
        if (format.vcodec !== "none" && format.acodec === "none") {
            return `${format.height || format.resolution || format.format_note || "Video"} - ${format.ext}`;
        } else if (format.vcodec === "none" && format.acodec !== "none") {
            return `Audio - ${format.ext}`;
        } else if (format.vcodec !== "none" && format.acodec !== "none") {
            return `${format.height || format.resolution || format.format_note || "Video"} - ${format.ext}`;
        } else {
            return `${format.format_id || "Unknown"} - ${format.ext}`;
        }
    };

    const setDownloadedStyle = (button) => {
        button.style.backgroundColor = "green";
        button.style.color = "white";
    };

    const forceDownload = async (url, filename = "download") => {
    try {
        // Open the URL in a new tab
        const newTab = window.open(url, "_blank");

        if (!newTab) {
            alert("Popup blocked. Please allow popups and try again.");
            return;
        }

        alert("If the download doesn't start automatically, click the 3-dot menu and choose 'Download'.");
    } catch (err) {
        console.error("Download failed:", err);
        alert("Download failed. Click and hold the link or open it in a new tab to download manually.");
    }
};

    const buttonContainer = document.getElementById("download-buttons");
    buttonContainer.innerHTML = "";

    videoData.formats.forEach((format) => {
        if (!format.url) return;

        const label = getLabel(format);
        const btn = document.createElement("button");
        btn.innerHTML = `<i class="fas fa-download"></i> Download (${label})`;
        btn.className = "download-btn";

        btn.onclick = () => {
    // Apply green color immediately
    btn.style.backgroundColor = "#4CAF50";
    btn.style.color = "white";
    btn.disabled = true;

    // Let the browser render the style changes before downloading
    setTimeout(() => {
        const filename = `${videoId || 'video'}_${label.replace(/\s+/g, "_")}.${format.ext}`;
        forceDownload(format.url, filename);
    }, 50); // slight delay to ensure style update renders first
};

        buttonContainer.appendChild(btn);
    });

    // YouTube merge logic
    const mergeContainer = document.getElementById("merged-download-buttons");
mergeContainer.innerHTML = "";

const isYouTube = (videoData.platform || "").toLowerCase().includes("youtube");
if (isYouTube) {
    const resolutions = ["720p", "1080p", "1440p", "2160p"];
    resolutions.forEach((res) => {
        const mergeBtn = document.createElement("button");
        mergeBtn.textContent = `Download ${res}`;
        mergeBtn.className = "download-btn";

        mergeBtn.onclick = async () => {
            mergeBtn.disabled = true;
            let percent = 0;

            const updateButton = (p) => {
                mergeBtn.innerHTML = `
                    <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Preparing ${res} (${p}%)`;
            };

            updateButton(percent);

            const progressInterval = setInterval(() => {
                if (percent < 90) {
                    percent += 5;
                    updateButton(percent);
                }
            }, 300);

            try {
                const mergeRes = await fetch("/merge_video", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        video_url: videoUrl,
                        resolution: res,
                        formats: videoData.formats
                    })
                });

                const result = await mergeRes.json();
                clearInterval(progressInterval);

                if (result.url) {
                    updateButton(100);
                    const filename = result.url.split("/").pop();
                    await forceDownload(`/merged/${filename}`, filename, mergeBtn);

                    setTimeout(() => {
                        mergeBtn.innerHTML = `<i class="fas fa-check-circle"></i> Downloaded ${res}`;
                        mergeBtn.disabled = false;
                    }, 500);
                } else {
                    mergeBtn.innerHTML = "Error";
                    mergeBtn.disabled = false;
                }
            } catch (err) {
                clearInterval(progressInterval);
                mergeBtn.innerHTML = "Error";
                mergeBtn.disabled = false;
            }
        };

        mergeContainer.appendChild(mergeBtn);
    });
}

    // External players
    document.querySelectorAll(".player-options button").forEach((btn) => {
        btn.addEventListener("click", () => {
            if (!firstPlayable || !firstPlayable.url) return;

            const videoLink = firstPlayable.url;
            const player = btn.getAttribute("data-player");

            const schemes = {
                online: () => {
                    videoSource.src = videoLink;
                    videoElement.load();
                    videoElement.play();
                },
                mx: () => window.location.href = `intent:${videoLink}#Intent;package=com.mxtech.videoplayer.ad;end`,
                vlc: () => window.location.href = `vlc://${videoLink}`,
                xplayer: () => window.location.href = `intent:${videoLink}#Intent;package=video.player.videoplayer;end`,
                splayer: () => window.location.href = `intent:${videoLink}#Intent;package=com.smedia.video.player;end`,
                kmplayer: () => window.location.href = `intent:${videoLink}#Intent;package=com.kmplayer;end`,
                playit: () => window.location.href = `intent:${videoLink}#Intent;package=com.playit.videoplayer;end`
            };

            schemes[player]?.();
        });
    });

    // Show the video title
    const videoTitle = document.getElementById("videoTitle");
    if (videoData.title) {
        videoTitle.textContent = videoData.title;
    }
});
</script>