
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Night City Racing", layout="wide")

st.markdown("""
<style>
.stApp {
    background: #071522;
}
.block-container {
    padding-top: 1rem;
    max-width: 1200px;
}
h1 {
    color: #eaf5ff;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

st.title("🌃 NIGHT CITY RACING")

game_html = r"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
* { box-sizing: border-box; }
body {
    margin: 0;
    background: #071522;
    color: white;
    font-family: Arial, sans-serif;
    overflow: hidden;
}
#game {
    width: 100%;
    max-width: 1100px;
    margin: auto;
    position: relative;
}
canvas {
    width: 100%;
    display: block;
    background: #071522;
    border-radius: 12px;
}
.hud {
    position: absolute;
    inset: 0;
    pointer-events: none;
    font-weight: 900;
    text-shadow: 0 2px 8px #000;
}
.score {
    position: absolute;
    top: 18px;
    left: 22px;
    font-size: 22px;
}
.score span {
    display: block;
    color: #ffbd22;
    font-size: 42px;
}
.timer {
    position: absolute;
    top: 16px;
    left: 50%;
    transform: translateX(-50%);
    text-align: center;
    font-size: 18px;
}
.timer span {
    display: block;
    font-size: 48px;
}
.level {
    position: absolute;
    top: 22px;
    right: 22px;
    font-size: 20px;
}
.speed {
    position: absolute;
    right: 20px;
    bottom: 20px;
    border: 5px solid #ffffff55;
    border-radius: 50%;
    width: 115px;
    height: 115px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: #142d3b88;
}
.speed span {
    font-size: 34px;
}
.boost {
    position: absolute;
    bottom: 25px;
    left: 50%;
    transform: translateX(-50%);
    text-align: center;
    font-size: 20px;
}
.boostbar {
    display: flex;
    gap: 5px;
    margin-top: 8px;
}
.boostbar i {
    width: 23px;
    height: 10px;
    background: #ffffff44;
}
.boostbar i.on {
    background: #ffad18;
}
.controls {
    display: flex;
    justify-content: center;
    gap: 30px;
    padding: 12px;
}
.controls button, #restart {
    border: 1px solid #80b9d0;
    background: #16384c;
    color: white;
    font-size: 25px;
    font-weight: bold;
    border-radius: 15px;
    padding: 12px 35px;
    touch-action: none;
}
.controls button:active, #restart:active {
    background: #ffad18;
    color: #111;
}
#message {
    position: absolute;
    top: 43%;
    width: 100%;
    text-align: center;
    font-size: 42px;
    font-weight: 900;
    text-shadow: 0 3px 12px black;
    display: none;
}
</style>
</head>

<body>
<div id="game">
    <canvas id="canvas" width="1000" height="620"></canvas>

    <div class="hud">
        <div class="score">SCORE <span id="score">0</span></div>
        <div class="timer">TIME LEFT <span id="timer">60.0</span></div>
        <div class="level">LEVEL <span id="level">1</span></div>

        <div class="speed">
            SPEED
            <span id="speed">120</span>
            KM/H
        </div>

        <div class="boost">
            BOOST
            <div class="boostbar" id="boostbar">
                <i class="on"></i><i class="on"></i><i class="on"></i>
                <i class="on"></i><i class="on"></i><i></i><i></i><i></i>
            </div>
        </div>
    </div>

    <div id="message">LEVEL UP!</div>
</div>

<div class="controls">
    <button id="left">◀</button>
    <button id="right">▶</button>
</div>

<div style="text-align:center;padding-bottom:12px">
    <button id="restart" onclick="restartGame()">重新開始</button>
</div>

<script>
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

const W = canvas.width;
const H = canvas.height;

let score = 0;
let level = 1;
let timeLeft = 60;
let speed = 120;
let boost = 5;
let playerX = 0;
let roadScroll = 0;
let frame = 0;
let enemies = [];
let gameOver = false;
let paused = false;
let lastTime = 0;
let messageTimer = 0;

const keys = {left:false, right:false};

function roadCenter(y) {
    const t = y / H;
    return W/2 + Math.sin(t * 3.2 + roadScroll * 0.0007) * 115 * t;
}

function roadWidth(y) {
    return 100 + (y/H) * 780;
}

function drawBackground() {
    const sky = ctx.createLinearGradient(0,0,0,H);
    sky.addColorStop(0,"#03101c");
    sky.addColorStop(0.55,"#09283a");
    sky.addColorStop(1,"#273d43");
    ctx.fillStyle = sky;
    ctx.fillRect(0,0,W,H);

    // 遠方城市光暈
    const glow = ctx.createRadialGradient(500,280,10,500,280,400);
    glow.addColorStop(0,"#e7a66b33");
    glow.addColorStop(1,"#07152200");
    ctx.fillStyle = glow;
    ctx.fillRect(0,0,W,H);

    // 左右兩側高樓
    for(let side of [-1,1]) {
        for(let i=0;i<10;i++) {
            let depth = i/10;
            let bh = 180 + ((i*73)%220);
            let bw = 45 + ((i*19)%45);
            let x = side < 0
                ? i*58 - 15
                : W - i*58 - bw + 15;

            let y = 90 + (i%3)*22;
            let shade = 8 + i%4*4;

            ctx.fillStyle = `rgb(${shade},${25+shade},${35+shade})`;
            ctx.fillRect(x,y,bw,bh);

            // 大樓窗戶
            for(let wy=y+12;wy<y+bh-8;wy+=20) {
                for(let wx=x+8;wx<x+bw-5;wx+=16) {
                    if(Math.random() > 0.25) {
                        ctx.fillStyle =
                            Math.random() > 0.5 ? "#d9e6a877" : "#8bc4d655";
                        ctx.fillRect(wx,wy,7,9);
                    }
                }
            }
        }
    }

    // 遠方路燈
    for(let i=0;i<7;i++) {
        let y = 180 + i*38;
        let x1 = 250 - i*22;
        let x2 = 750 + i*22;

        for(let x of [x1,x2]) {
            ctx.strokeStyle="#627b7d";
            ctx.lineWidth=2+i*0.3;
            ctx.beginPath();
            ctx.moveTo(x,y);
            ctx.lineTo(x,y-35-i*4);
            ctx.stroke();

            ctx.fillStyle="#ffe6a0";
            ctx.shadowColor="#ffd879";
            ctx.shadowBlur=18;
            ctx.fillRect(x-5,y-38-i*4,10,4);
            ctx.shadowBlur=0;
        }
    }
}

function drawRoad() {
    let leftTop = roadCenter(0)-roadWidth(0)/2;
    let rightTop = roadCenter(0)+roadWidth(0)/2;
    let leftBottom = roadCenter(H)-roadWidth(H)/2;
    let rightBottom = roadCenter(H)+roadWidth(H)/2;

    // 道路外側地面
    ctx.fillStyle="#263b3c";
    ctx.fillRect(0,300,W,H-300);

    // 道路主體
    let road = ctx.createLinearGradient(0,250,0,H);
    road.addColorStop(0,"#555b57");
    road.addColorStop(1,"#77766b");

    ctx.fillStyle=road;
    ctx.beginPath();
    ctx.moveTo(leftTop,0);
    ctx.lineTo(rightTop,0);
    ctx.lineTo(rightBottom,H);
    ctx.lineTo(leftBottom,H);
    ctx.closePath();
    ctx.fill();

    // 路邊白線
    ctx.strokeStyle="#e8e8c9";
    ctx.lineWidth=4;
    ctx.beginPath();
    ctx.moveTo(leftTop,0);
    ctx.lineTo(leftBottom,H);
    ctx.moveTo(rightTop,0);
    ctx.lineTo(rightBottom,H);
    ctx.stroke();

    // 車道虛線
    for(let lane=1;lane<=2;lane++) {
        for(let i=0;i<14;i++) {
            let p = (i/14 + (roadScroll*0.001)%1)%1;
            let y = p*H;
            let x = roadCenter(y) - roadWidth(y)/2 + roadWidth(y)*lane/3;
            let lineH = 3 + p*24;
            let lineW = 1 + p*5;

            ctx.fillStyle="#f2edcf";
            ctx.fillRect(x-lineW/2,y,lineW,lineH);
        }
    }

    // 路邊護欄
    for(let side of [-1,1]) {
        ctx.strokeStyle="#a9b6aa";
        ctx.lineWidth=3;
        ctx.beginPath();
        for(let y=230;y<H;y+=8) {
            let x=roadCenter(y)+side*(roadWidth(y)/2+12);
            if(y===230) ctx.moveTo(x,y);
            else ctx.lineTo(x,y);
        }
        ctx.stroke();

        for(let i=0;i<12;i++) {
            let y=250+i*35;
            let x=roadCenter(y)+side*(roadWidth(y)/2+12);
            ctx.fillStyle="#778984";
            ctx.fillRect(x-2,y,5,18);
        }
    }

    // 道路表面光影
    let light = ctx.createLinearGradient(300,250,700,H);
    light.addColorStop(0,"#fff3c000");
    light.addColorStop(0.5,"#fff3c022");
    light.addColorStop(1,"#fff3c000");
    ctx.fillStyle=light;
    ctx.fillRect(0,250,W,H-250);
}

function drawCar(x,y,w,h,color,isPlayer=false) {
    ctx.save();
    ctx.translate(x,y);

    // 車底陰影
    ctx.fillStyle="#0009";
    ctx.beginPath();
    ctx.ellipse(0,h*0.48,w*0.62,h*0.12,0,0,Math.PI*2);
    ctx.fill();

    // 車燈光暈
    if(isPlayer) {
        ctx.shadowColor="#ff4b32";
        ctx.shadowBlur=24;
        ctx.fillStyle="#ff4b3233";
        ctx.fillRect(-w*0.42,h*0.22,w*0.84,h*0.3);
        ctx.shadowBlur=0;
    }

    // 輪胎
    ctx.fillStyle="#090d12";
    ctx.fillRect(-w*0.52,-h*0.05,w*0.15,h*0.38);
    ctx.fillRect(w*0.37,-h*0.05,w*0.15,h*0.38);

    // 車身立體漸層
    let body = ctx.createLinearGradient(-w/2,0,w/2,0);
    body.addColorStop(0,"#56646a");
    body.addColorStop(0.18,color);
    body.addColorStop(0.5,"#f5f0ce");
    body.addColorStop(0.82,color);
    body.addColorStop(1,"#3b464c");

    ctx.fillStyle=body;
    ctx.beginPath();
    ctx.moveTo(-w*0.43,h*0.42);
    ctx.lineTo(-w*0.48,h*0.02);
    ctx.lineTo(-w*0.31,-h*0.30);
    ctx.lineTo(-w*0.19,-h*0.43);
    ctx.lineTo(w*0.19,-h*0.43);
    ctx.lineTo(w*0.31,-h*0.30);
    ctx.lineTo(w*0.48,h*0.02);
    ctx.lineTo(w*0.43,h*0.42);
    ctx.closePath();
    ctx.fill();

    // 後車窗
    let glass=ctx.createLinearGradient(0,-h*0.4,0,h*0.05);
    glass.addColorStop(0,"#172c39");
    glass.addColorStop(1,"#07131d");
    ctx.fillStyle=glass;
    ctx.beginPath();
    ctx.moveTo(-w*0.29,-h*0.29);
    ctx.lineTo(-w*0.17,-h*0.39);
    ctx.lineTo(w*0.17,-h*0.39);
    ctx.lineTo(w*0.29,-h*0.29);
    ctx.lineTo(w*0.34,-h*0.04);
    ctx.lineTo(-w*0.34,-h*0.04);
    ctx.closePath();
    ctx.fill();

    // 後車廂
    ctx.fillStyle="#202c32";
    ctx.fillRect(-w*0.38,h*0.06,w*0.76,h*0.12);

    // 尾燈
    ctx.shadowColor="#ff2929";
    ctx.shadowBlur=isPlayer?22:12;
    ctx.fillStyle="#ff3b38";
    ctx.fillRect(-w*0.40,h*0.19,w*0.25,h*0.09);
    ctx.fillRect(w*0.15,h*0.19,w*0.25,h*0.09);
    ctx.shadowBlur=0;

    // 車牌
    ctx.fillStyle="#c9c8b4";
    ctx.fillRect(-w*0.12,h*0.22,w*0.24,h*0.07);
    ctx.fillStyle="#26343a";
    ctx.fillRect(-w*0.09,h*0.235,w*0.18,h*0.035);

    // 保險桿
    ctx.fillStyle="#313c40";
    ctx.fillRect(-w*0.42,h*0.34,w*0.84,h*0.07);

    // 車身反光
    ctx.strokeStyle="#fff5c988";
    ctx.lineWidth=2;
    ctx.beginPath();
    ctx.moveTo(-w*0.43,h*0.04);
    ctx.lineTo(-w*0.36,h*0.27);
    ctx.moveTo(w*0.43,h*0.04);
    ctx.lineTo(w*0.36,h*0.27);
    ctx.stroke();

    ctx.restore();
}

function spawnEnemy() {
    const lanes=[-0.65,0,0.65];
    let lane=lanes[Math.floor(Math.random()*lanes.length)];
    enemies.push({
        lane:lane,
        z:0.05,
        color:["#b7c6c5","#b94d42","#343f50","#d0c5a1"][Math.floor(Math.random()*4)]
    });
}

function drawEnemies() {
    for(let e of enemies) {
        let y=120+e.z*470;
        let center=roadCenter(y);
        let x=center+e.lane*(roadWidth(y)*0.38);
        let scale=0.18+e.z*0.82;
        let w=55*scale;
        let h=90*scale;
        drawCar(x,y,w,h,e.color,false);
    }
}

function updateEnemies() {
    for(let e of enemies) {
        e.z += 0.0035 + level*0.00045;
    }

    enemies=enemies.filter(e=>{
        if(e.z>1.1) {
            score+=10;
            return false;
        }
        return true;
    });

    if(frame%Math.max(35,100-level*8)===0) spawnEnemy();
}

function drawPlayer() {
    let y=H-115;
    let x=W/2+playerX*270;
    drawCar(x,y,190,245,"#e9e9d0",true);
}

function checkCollision() {
    for(let e of enemies) {
        if(e.z>0.78) {
            let enemyX=roadCenter(520)+e.lane*roadWidth(520)*0.38;
            let playerScreenX=W/2+playerX*270;
            if(Math.abs(enemyX-playerScreenX)<75) {
                gameOver=true;
                document.getElementById("message").innerText="撞到車輛！ GAME OVER";
                document.getElementById("message").style.display="block";
            }
        }
    }
}

function updateHUD() {
    document.getElementById("score").innerText=score;
    document.getElementById("level").innerText=level;
    document.getElementById("timer").innerText=Math.max(0,timeLeft).toFixed(1);
    document.getElementById("speed").innerText=speed;

    let bars=document.querySelectorAll(".boostbar i");
    bars.forEach((b,i)=>b.classList.toggle("on",i<boost));
}

function update(dt) {
    if(gameOver || paused) return;

    frame++;
    roadScroll+=speed;
    timeLeft-=dt/1000;

    if(keys.left) playerX-=0.035;
    if(keys.right) playerX+=0.035;
    playerX=Math.max(-1,Math.min(1,playerX));

    speed=120+(level-1)*12;
    updateEnemies();
    checkCollision();

    let newLevel=Math.floor(score/100)+1;
    if(newLevel>level) {
        level=newLevel;
        messageTimer=100;
        document.getElementById("message").innerText="LEVEL "+level+"!";
        document.getElementById("message").style.display="block";
    }

    if(messageTimer>0) {
        messageTimer--;
        if(messageTimer===0)
            document.getElementById("message").style.display="none";
    }

    if(timeLeft<=0) {
        gameOver=true;
        document.getElementById("message").innerText="時間到！ GAME OVER";
        document.getElementById("message").style.display="block";
    }

    updateHUD();
}

function draw() {
    drawBackground();
    drawRoad();
    drawEnemies();
    drawPlayer();
}

function loop(timestamp) {
    let dt=timestamp-lastTime;
    lastTime=timestamp;
    update(dt);
    draw();
    requestAnimationFrame(loop);
}

function restartGame() {
    score=0;
    level=1;
    timeLeft=60;
    speed=120;
    playerX=0;
    roadScroll=0;
    frame=0;
    enemies=[];
    gameOver=false;
    paused=false;
    boost=5;
    document.getElementById("message").style.display="none";
    updateHUD();
}

document.addEventListener("keydown",e=>{
    if(e.key==="ArrowLeft" || e.key==="a") keys.left=true;
    if(e.key==="ArrowRight" || e.key==="d") keys.right=true;
});
document.addEventListener("keyup",e=>{
    if(e.key==="ArrowLeft" || e.key==="a") keys.left=false;
    if(e.key==="ArrowRight" || e.key==="d") keys.right=false;
});

function holdButton(id,direction) {
    const btn=document.getElementById(id);
    btn.addEventListener("pointerdown",e=>{
        e.preventDefault();
        keys[direction]=true;
    });
    ["pointerup","pointerleave","pointercancel"].forEach(event=>{
        btn.addEventListener(event,()=>keys[direction]=false);
    });
}
holdButton("left","left");
holdButton("right","right");

updateHUD();
requestAnimationFrame(loop);
</script>
</body>
</html>
"""

components.html(game_html, height=790, scrolling=False)

