<script>
console.log("JS loaded successfully!");

const mobileBtn = document.getElementById('mobileMenuBtn');
    const mobileOverlay = document.getElementById('mobileMenuOverlay');
    const closeBtn = document.getElementById('closeMobileMenu');

    mobileBtn.addEventListener('click', () => {
        mobileOverlay.classList.add('active');
    });

    closeBtn.addEventListener('click', () => {
        mobileOverlay.classList.remove('active');
    });

window.onload = function () {
    const form = document.getElementById("videoForm");
    if (!form) return;

    form.addEventListener("submit", async function (e) {
        e.preventDefault();

        const urlInput = document.getElementById("videoUrl");
        const videoURL = urlInput.value.trim();

        const errorBox = createOrGetBox("error-box");
        const countdownBox = createOrGetBox("countdown-box");

        errorBox.innerHTML = "";
        countdownBox.innerHTML = "";

        if (!videoURL) {
            errorBox.innerHTML = "Please enter a video URL.";
            return;
        }

        try {
            countdownBox.innerHTML = `<strong>Analyzing video info...</strong>`;

            const response = await fetch("/get_video_info", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ video_url: videoURL })
            });

            const result = await response.json();

            if (!response.ok || !result.formats || !result.platform || !result.video_id) {
                throw new Error(result.error || "Could not process the video. Try a different link.");
            }

            // Store the video data in sessionStorage
            sessionStorage.setItem("videoData", JSON.stringify(result));

            errorBox.innerHTML = `<span style="color:green">Detected platform: <strong>${result.platform}</strong>. Preparing stream page...</span>`;

            startCountdown(5, countdownBox, () => {
                window.location.href = `/stream?video_id=${result.video_id}&video_url=${encodeURIComponent(videoURL)}`;
            });

        } catch (error) {
            errorBox.innerHTML = `<span style="color:red">${error.message}</span>`;
            countdownBox.innerHTML = "";
        }
    });

    function startCountdown(seconds, box, callback) {
        let counter = seconds;
        box.innerHTML = `<strong>Redirecting in ${counter} seconds...</strong>`;
        const interval = setInterval(() => {
            counter--;
            if (counter > 0) {
                box.innerHTML = `<strong>Redirecting in ${counter} seconds...</strong>`;
            } else {
                clearInterval(interval);
                callback();
            }
        }, 1000);
    }

    function createOrGetBox(id) {
        let box = document.getElementById(id);
        if (!box) {
            box = document.createElement("div");
            box.id = id;
            box.style.marginTop = "10px";
            form.after(box);
        } else {
            box.innerHTML = "";
        }
        return box;
    }
};
</script>