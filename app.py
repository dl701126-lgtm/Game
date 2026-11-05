
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Night City Racing",
    page_icon="🏎️",
    layout="wide"
)

st.markdown("""
<style>
    .stApp {
        background: #080d18;
    }
    h1 {
        color: #ffffff;
        text-align: center;
    }
    iframe {
        border: none;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏎️ NIGHT CITY RACING")

game_html = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
* {
    box-sizing: border-box;
    user-select: none;
    -webkit-user-select: none;
}

body {
    margin: 0;
    background: #080d18;
    color: white;
    font-family: Arial, sans-serif;
    overflow: hidden;
}

#game {
    display: block;
    width: 100%;
    max-width: 1000px;
    margin: auto;
    background: #080d18;
    touch-action: none;
}

#panel {
    max-width: 1000px;
    margin: 8px auto;
    display: flex;
    justify-content: space-around;
    flex-wrap: wrap;
    gap: 8px;
}

.info {
    background: #111d30;
    border: 1px solid #29415f;
    border-radius: 8px;
    padding: 8px 14px;
    min-width: 90px;
    text-align: center;
    font-size: 14px;
}

.info span {
    display: block;
    color: #4deaff;
    font-size: 20px;
    font-weight: bold;
    margin-top: 3px;
}

#controls {
    max-width: 1000px;
    margin: 12px auto;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
}

button {
    border: none;
    border-radius: 12px;
    padding: 14px 20px;
    color: white;
    font-size: 17px;
    font-weight: bold;
    background: #174a80;
    min-width: 72px;
    touch-action: none;
}

button:active {
    background: #268bdc;
    transform: scale(0.96);
}

#gas {
    background: #087b4a;
}

#brake {
    background: #a52b32;
}

#restart {
    background: #7544a5;
}

#message {
    text-align: center;
    color: #ffe66d;
    font-size: 18px;
    font-weight: bold;
    min-height: 24px;
}
</style>
</head>

<body>

<div id="panel">
    <div class="info">SCORE<span id="score">0</span></div>
    <div class="info">TIME<span id="time">60</span></div>
    <div class="info">LEVEL<span id="level">1</span></div>
    <div class="info">SPEED<span id="speed">0 km/h</span></div>
</div>

<canvas id="game" width="1000" height="620"></canvas>

<div id="message">按住油門開始遊戲！</div>

<div id="controls">
    <button id="left">⬅ 左</button>
    <button id="brake">煞車</button>
    <button id="gas">油門</button>
    <button id="right">右 ➡</button>
    <button id="restart">重新開始</button>
</div>

<script>
const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

const W = canvas.width;
const H = canvas.height;

let score = 0;
let timeLeft = 60;
let level = 1;

let speed = 0;
let maxSpeed = 220;
let acceleration = 38;
let brakePower = 100;
let friction = 7;

let playerX = W / 2;
let roadScroll = 0;

let enemies = [];
let frame = 0;
let gameOver = false;
let started = false;

let lastTime = 0;
let spawnTimer = 0;
let messageTimer = 0;

const keys = {
    left: false,
    right: false,
    gas: false,
    brake: false
};

const enemyColors = [
    "#e53935",
    "#2979ff",
    "#43a047",
    "#ffca28",
    "#8e24aa",
    "#eeeeee"
];

function roadCenter(y) {
    return W / 2;
}

function roadWidth(y) {
    return 100 + (y / H) * 780;
}

function updateHUD() {
    document.getElementById("score").textContent = score;
    document.getElementById("time").textContent =
        Math.max(0, Math.ceil(timeLeft));
    document.getElementById("level").textContent = level;
    document.getElementById("speed").textContent =
        Math.round(speed) + " km/h";
}

function drawBackground() {
    const sky = ctx.createLinearGradient(0, 0, 0, H);
    sky.addColorStop(0, "#050a18");
    sky.addColorStop(1, "#18233a");

    ctx.fillStyle = sky;
    ctx.fillRect(0, 0, W, H);

    // 城市建築
    for (let side = 0; side < 2; side++) {
        for (let i = 0; i < 12; i++) {
            let bw = 35 + (i % 3) * 18;
            let bh = 160 + ((i * 47) % 190);
            let x = side === 0
                ? i * 48
                : W - (i + 1) * 48;

            let y = H - bh;

            ctx.fillStyle = i % 2 === 0
                ? "#101c32"
                : "#17243b";

            ctx.fillRect(x, y, bw, bh);

            // 建築物窗戶
            for (let wy = y + 15; wy < H - 10; wy += 25) {
                for (let wx = x + 8; wx < x + bw - 5; wx += 17) {
                    if ((Math.floor(wx + wy) % 4) !== 0) {
                        ctx.fillStyle =
                            (Math.floor(wx + wy) % 3 === 0)
                            ? "#ffd76a"
                            : "#58a9d8";

                        ctx.fillRect(wx, wy, 6, 9);
                    }
                }
            }
        }
    }

    // 路燈
    for (let i = 0; i < 7; i++) {
        let y = (i * 105 + roadScroll * 0.7) % H;
        let scale = 0.35 + y / H * 0.65;

        for (let side of [-1, 1]) {
            let x = W / 2 + side * (roadWidth(y) / 2 + 35 * scale);

            ctx.strokeStyle = "#667b9d";
            ctx.lineWidth = 4 * scale;

            ctx.beginPath();
            ctx.moveTo(x, y);
            ctx.lineTo(x, y - 70 * scale);
            ctx.lineTo(x + side * 25 * scale, y - 70 * scale);
            ctx.stroke();

            ctx.fillStyle = "#ffe9a0";
            ctx.beginPath();
            ctx.arc(
                x + side * 25 * scale,
                y - 70 * scale,
                5 * scale,
                0,
                Math.PI * 2
            );
            ctx.fill();
        }
    }
}

function drawRoad() {
    const topWidth = roadWidth(0);
    const bottomWidth = roadWidth(H);

    ctx.fillStyle = "#252b36";

    ctx.beginPath();
    ctx.moveTo(W / 2 - topWidth / 2, 0);
    ctx.lineTo(W / 2 + topWidth / 2, 0);
    ctx.lineTo(W / 2 + bottomWidth / 2, H);
    ctx.lineTo(W / 2 - bottomWidth / 2, H);
    ctx.closePath();
    ctx.fill();

    // 道路兩側邊線
    ctx.strokeStyle = "#e8e8e8";
    ctx.lineWidth = 8;

    ctx.beginPath();
    ctx.moveTo(W / 2 - topWidth / 2, 0);
    ctx.lineTo(W / 2 - bottomWidth / 2, H);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(W / 2 + topWidth / 2, 0);
    ctx.lineTo(W / 2 + bottomWidth / 2, H);
    ctx.stroke();

    // 車道虛線
    for (let lane = -1; lane <= 1; lane++) {
        if (lane === 0) continue;

        for (let i = 0; i < 12; i++) {
            let y = (i * 75 + roadScroll) % H;
            let width = roadWidth(y);
            let x = W / 2 + lane * width / 3;

            ctx.fillStyle = "#f6f0ce";
            ctx.fillRect(x - 4, y, 8, 35 + y / H * 25);
        }
    }
}

function drawCar(x, y, w, h, color, isPlayer = false) {
    ctx.save();
    ctx.translate(x, y);

    // 車底陰影
    ctx.fillStyle = "rgba(0,0,0,0.5)";
    ctx.beginPath();
    ctx.ellipse(0, h * 0.43, w * 0.58, h * 0.12, 0, 0, Math.PI * 2);
    ctx.fill();

    // 輪胎
    ctx.fillStyle = "#080808";
    ctx.fillRect(-w * 0.53, -h * 0.25, w * 0.19, h * 0.42);
    ctx.fillRect(w * 0.34, -h * 0.25, w * 0.19, h * 0.42);
    ctx.fillRect(-w * 0.53, h * 0.25, w * 0.19, h * 0.25);
    ctx.fillRect(w * 0.34, h * 0.25, w * 0.19, h * 0.25);

    // 車身漸層
    let body = ctx.createLinearGradient(-w / 2, 0, w / 2, 0);
    body.addColorStop(0, "#222");
    body.addColorStop(0.18, color);
    body.addColorStop(0.5, color);
    body.addColorStop(0.82, color);
    body.addColorStop(1, "#222");

    ctx.fillStyle = body;

    ctx.beginPath();
    ctx.moveTo(-w * 0.42, -h * 0.48);
    ctx.lineTo(w * 0.42, -h * 0.48);
    ctx.lineTo(w * 0.5, -h * 0.2);
    ctx.lineTo(w * 0.48, h * 0.4);
    ctx.lineTo(w * 0.35, h * 0.5);
    ctx.lineTo(-w * 0.35, h * 0.5);
    ctx.lineTo(-w * 0.48, h * 0.4);
    ctx.lineTo(-w * 0.5, -h * 0.2);
    ctx.closePath();
    ctx.fill();

    // 車頂玻璃
    ctx.fillStyle = "#101d2c";
    ctx.beginPath();
    ctx.moveTo(-w * 0.3, -h * 0.28);
    ctx.lineTo(w * 0.3, -h * 0.28);
    ctx.lineTo(w * 0.34, h * 0.08);
    ctx.lineTo(-w * 0.34, h * 0.08);
    ctx.closePath();
    ctx.fill();

    // 後擋風玻璃反光
    ctx.fillStyle = "rgba(100,190,230,0.35)";
    ctx.fillRect(-w * 0.25, -h * 0.24, w * 0.5, h * 0.12);

    // 車尾燈
    ctx.fillStyle = "#ff172e";
    ctx.fillRect(-w * 0.39, h * 0.29, w * 0.2, h * 0.08);
    ctx.fillRect(w * 0.19, h * 0.29, w * 0.2, h * 0.08);

    // 車牌
    ctx.fillStyle = "#dce7ed";
    ctx.fillRect(-w * 0.14, h * 0.37, w * 0.28, h * 0.07);

    if (isPlayer) {
        ctx.shadowColor = "#ff263d";
        ctx.shadowBlur = 15;
        ctx.fillStyle = "rgba(255,40,60,0.25)";
        ctx.fillRect(-w * 0.4, h * 0.31, w * 0.8, h * 0.05);
    }

    ctx.restore();
}

function drawPlayer() {
    drawCar(playerX, H - 145, 190, 245, "#e51d35", true);
}

function spawnEnemy() {
    const lanes = [-0.65, 0, 0.65];
    const lane = lanes[Math.floor(Math.random() * lanes.length)];

    enemies.push({
        lane: lane,
        z: 0.03,
        color: enemyColors[
            Math.floor(Math.random() * enemyColors.length)
        ]
    });
}

function drawEnemies() {
    for (let e of enemies) {
        let y = e.z * H;
        let width = roadWidth(y);
        let x = W / 2 + e.lane * width / 2.7;

        let scale = 0.25 + e.z * 0.65;

        let carW = 135 * scale;
        let carH = 175 * scale;

        drawCar(x, y, carW, carH, e.color, false);
    }
}

function updateEnemies(dt) {
    spawnTimer += dt;

    let spawnInterval = Math.max(650, 1500 - level * 55);

    if (spawnTimer > spawnInterval) {
        spawnEnemy();
        spawnTimer = 0;
    }

    let movement = 0.2 + speed / 120;

    for (let e of enemies) {
        e.z += (
            0.00018 +
            level * 0.000025
        ) * movement * dt;
    }

    for (let i = enemies.length - 1; i >= 0; i--) {
        let e = enemies[i];

        if (e.z > 1.05) {
            enemies.splice(i, 1);
            score += 10;

            let newLevel = Math.floor(score / 100) + 1;

            if (newLevel > level) {
                level = newLevel;
                document.getElementById("message").textContent =
                    "LEVEL UP! 第 " + level + " 關！";

                messageTimer = 120;
            }
        }
    }
}

function checkCollision() {
    for (let e of enemies) {
        if (e.z > 0.72 && e.z < 1.02) {
            let y = e.z * H;
            let x = W / 2 + e.lane * roadWidth(y) / 2.7;

            if (
                Math.abs(x - playerX) < 120 &&
                Math.abs(y - (H - 145)) < 100
            ) {
                gameOver = true;
                document.getElementById("message").textContent =
                    "💥 GAME OVER！按重新開始再玩一次";
                return;
            }
        }
    }
}

function updatePlayer(dt) {
    const seconds = dt / 1000;

    if (keys.gas) {
        speed += acceleration * seconds;
        started = true;
    } else if (keys.brake) {
        speed -= brakePower * seconds;
    } else {
        speed -= friction * seconds;
    }

    speed = Math.max(0, Math.min(maxSpeed + (level - 1) * 10, speed));

    if (keys.left) {
        playerX -= 420 * seconds;
    }

    if (keys.right) {
        playerX += 420 * seconds;
    }

    playerX = Math.max(120, Math.min(W - 120, playerX));

    roadScroll += speed * seconds * 1.5;
}

function endGame() {
    gameOver = true;
    document.getElementById("message").textContent =
        "⏰ 時間到！最終分數：" + score;
}

function update(dt) {
    if (gameOver) return;

    if (started) {
        timeLeft -= dt / 1000;

        if (timeLeft <= 0) {
            timeLeft = 0;
            endGame();
            return;
        }
    }

    updatePlayer(dt);
    updateEnemies(dt);
    checkCollision();

    if (messageTimer > 0) {
        messageTimer--;
    } else if (gameOver === false) {
        document.getElementById("message").textContent =
            started ? "小心其他車輛！" : "按住油門開始遊戲！";
    }

    updateHUD();
}

function draw() {
    drawBackground();
    drawRoad();
    drawEnemies();
    drawPlayer();

    if (gameOver) {
        ctx.fillStyle = "rgba(0,0,0,0.65)";
        ctx.fillRect(0, 0, W, H);

        ctx.fillStyle = "#ffdf65";
        ctx.font = "bold 54px Arial";
        ctx.textAlign = "center";
        ctx.fillText("GAME OVER", W / 2, H / 2);

        ctx.font = "bold 28px Arial";
        ctx.fillText("SCORE: " + score, W / 2, H / 2 + 55);
    }
}

function gameLoop(timestamp) {
    let dt = lastTime ? timestamp - lastTime : 16.67;
    lastTime = timestamp;

    dt = Math.min(dt, 50);

    update(dt);
    draw();

    requestAnimationFrame(gameLoop);
}

function resetGame() {
    score = 0;
    timeLeft = 60;
    level = 1;

    speed = 0;
    playerX = W / 2;
    roadScroll = 0;

    enemies = [];
    frame = 0;
    spawnTimer = 0;
    messageTimer = 0;

    gameOver = false;
    started = false;

    keys.left = false;
    keys.right = false;
    keys.gas = false;
    keys.brake = false;

    document.getElementById("message").textContent =
        "按住油門開始遊戲！";

    updateHUD();
}

// 按鈕控制
function bindButton(id, key) {
    const button = document.getElementById(id);

    button.addEventListener("pointerdown", function(e) {
        e.preventDefault();
        keys[key] = true;
        button.setPointerCapture(e.pointerId);
    });

    button.addEventListener("pointerup", function(e) {
        e.preventDefault();
        keys[key] = false;
    });

    button.addEventListener("pointercancel", function() {
        keys[key] = false;
    });

    button.addEventListener("lostpointercapture", function() {
        keys[key] = false;
    });
}

bindButton("left", "left");
bindButton("right", "right");
bindButton("gas", "gas");
bindButton("brake", "brake");

document.getElementById("restart").addEventListener(
    "click",
    resetGame
);

// 鍵盤控制
document.addEventListener("keydown", function(e) {
    if (
        ["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", " "]
        .includes(e.key)
    ) {
        e.preventDefault();
    }

    if (e.key === "ArrowLeft" || e.key.toLowerCase() === "a") {
        keys.left = true;
    }

    if (e.key === "ArrowRight" || e.key.toLowerCase() === "d") {
        keys.right = true;
    }

    if (
        e.key === "ArrowUp" ||
        e.key.toLowerCase() === "w" ||
        e.key === " "
    ) {
        keys.gas = true;
    }

    if (
        e.key === "ArrowDown" ||
        e.key.toLowerCase() === "s"
    ) {
        keys.brake = true;
    }
});

document.addEventListener("keyup", function(e) {
    if (e.key === "ArrowLeft" || e.key.toLowerCase() === "a") {
        keys.left = false;
    }

    if (e.key === "ArrowRight" || e.key.toLowerCase() === "d") {
        keys.right = false;
    }

    if (
        e.key === "ArrowUp" ||
        e.key.toLowerCase() === "w" ||
        e.key === " "
    ) {
        keys.gas = false;
    }

    if (
        e.key === "ArrowDown" ||
        e.key.toLowerCase() === "s"
    ) {
        keys.brake = false;
    }
});

updateHUD();
requestAnimationFrame(gameLoop);

</script>
</body>
</html>
"""

# 這裡是 Streamlit 顯示遊戲的地方
components.html(
    game_html,
    height=850,
    scrolling=False
)





