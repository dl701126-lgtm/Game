import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Car Racing Game",
    page_icon="🏎️",
    layout="centered"
)

st.title("🏎️ Car Racing Game")
st.write("Avoid the enemy cars and get the highest score!")

# HTML, CSS and JavaScript
game_html = """
<!DOCTYPE html>
<html>
<head>

<style>

body {
    margin: 0;
    background: #111;
    font-family: Arial;
    text-align: center;
    color: white;
}

h2 {
    color: #00ff99;
}

canvas {
    background: #333;
    border: 4px solid white;
    border-radius: 10px;
}

button {
    background: #00cc66;
    color: white;
    border: none;
    padding: 12px 25px;
    margin: 10px;
    border-radius: 8px;
    font-size: 16px;
    cursor: pointer;
}

button:hover {
    background: #009944;
}

</style>
</head>

<body>

<h2>🏁 SUPER CAR RACING 🏁</h2>

<p>Use LEFT and RIGHT arrow keys to drive.</p>

<canvas id="gameCanvas"
        width="400"
        height="500">
</canvas>

<br>

<button onclick="restartGame()">🔄 Restart Game</button>

<h3>Score: <span id="score">0</span></h3>

<h3 id="message"></h3>

<script>

const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

let player = {
    x: 175,
    y: 400,
    width: 50,
    height: 80,
    speed: 6
};

let enemies = [];
let score = 0;
let gameOver = false;
let keys = {};

document.addEventListener("keydown", function(e) {
    keys[e.key] = true;
});

document.addEventListener("keyup", function(e) {
    keys[e.key] = false;
});

function drawPlayer() {

    ctx.fillStyle = "#00ccff";

    ctx.fillRect(
        player.x,
        player.y,
        player.width,
        player.height
    );

    ctx.fillStyle = "white";

    ctx.fillRect(player.x + 7, player.y + 10, 36, 15);

    ctx.fillStyle = "black";

    ctx.fillRect(player.x - 5, player.y + 12, 7, 18);
    ctx.fillRect(player.x + 48, player.y + 12, 7, 18);
    ctx.fillRect(player.x - 5, player.y + 55, 7, 18);
    ctx.fillRect(player.x + 48, player.y + 55, 7, 18);
}

function drawEnemy(enemy) {

    ctx.fillStyle = "red";

    ctx.fillRect(
        enemy.x,
        enemy.y,
        50,
        80
    );

    ctx.fillStyle = "white";

    ctx.fillRect(enemy.x + 7, enemy.y + 10, 36, 15);

    ctx.fillStyle = "black";

    ctx.fillRect(enemy.x - 5, enemy.y + 12, 7, 18);
    ctx.fillRect(enemy.x + 48, enemy.y + 12, 7, 18);
}

function drawRoad() {

    ctx.fillStyle = "#555";

    ctx.fillRect(0, 0, 400, 500);

    ctx.strokeStyle = "white";
    ctx.lineWidth = 4;
    ctx.setLineDash([30, 25]);

    ctx.beginPath();
    ctx.moveTo(200, 0);
    ctx.lineTo(200, 500);
    ctx.stroke();

    ctx.setLineDash([]);
}

function createEnemy() {

    let x = Math.random() * 340;

    enemies.push({
        x: x,
        y: -100,
        width: 50,
        height: 80,
        speed: 4
    });
}

function collision(a, b) {

    return (
        a.x < b.x + b.width &&
        a.x + a.width > b.x &&
        a.y < b.y + b.height &&
        a.y + a.height > b.y
    );
}

function update() {

    if (gameOver) return;

    if (keys["ArrowLeft"] || keys["a"]) {
        player.x -= player.speed;
    }

    if (keys["ArrowRight"] || keys["d"]) {
        player.x += player.speed;
    }

    player.x = Math.max(
        5,
        Math.min(345, player.x)
    );

    enemies.forEach(enemy => {

        enemy.y += enemy.speed;

        if (collision(player, enemy)) {
            gameOver = true;
        }

    });

    enemies = enemies.filter(enemy => {

        if (enemy.y > 500) {
            score += 10;
            document.getElementById("score").innerText = score;
            return false;
        }

        return true;
    });

    if (Math.random() < 0.025) {
        createEnemy();
    }
}

function draw() {

    ctx.clearRect(0, 0, 400, 500);

    drawRoad();

    drawPlayer();

    enemies.forEach(drawEnemy);

    if (gameOver) {

        ctx.fillStyle = "rgba(0,0,0,0.8)";
        ctx.fillRect(0, 0, 400, 500);

        ctx.fillStyle = "red";
        ctx.font = "bold 35px Arial";
        ctx.fillText("GAME OVER", 85, 230);

        ctx.fillStyle = "white";
        ctx.font = "20px Arial";
        ctx.fillText("Score: " + score, 150, 270);

        document.getElementById("message").innerText =
            "You crashed! Press Restart to play again.";
    }
}

function gameLoop() {

    update();
    draw();

    requestAnimationFrame(gameLoop);
}

function restartGame() {

    player.x = 175;

    enemies = [];

    score = 0;

    gameOver = false;

    document.getElementById("score").innerText = 0;

    document.getElementById("message").innerText = "";

}

gameLoop();

</script>

</body>
</html>
"""

# Display HTML game inside Streamlit
components.html(
    game_html,
    height=650,
    scrolling=False
)

st.markdown("---")

st.markdown(
    """
    ### 🎮 Game Instructions

    - ⬅️ **Left Arrow:** Move left
    - ➡️ **Right Arrow:** Move right
    - 🚗 Avoid red cars.
    - ⭐ Earn 10 points for every car avoided.
    - 🔄 Restart when the game ends.
    """
)
