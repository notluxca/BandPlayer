document.addEventListener("DOMContentLoaded", () => {
    console.log("Page loaded");

    // quando uma música for tocada
    function setSong(songName) {
        window.pywebview.api.set_current_song(songName).then(response => {
            console.log(response);
        });
    }

    const playButton = document.getElementById("play");
    if (!playButton) return;

    playButton.addEventListener("click", () => {
        window.pywebview.api.test();
    });

    playButton.addEventListener("click", () => {
        const songName = "Assets/songs/LavaRushOst.wav";
        window.pywebview.api.set_current_song(songName).then(response => {
            document.getElementById("song-name-text").innerText = response;
            // console.log("[JS] Resposta do Python:", response);
        });
    });
});

