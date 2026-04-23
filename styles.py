"""
AutoStream AI — Premium UI Styles
Dark glass theme · Polished chat · Refined micro-interactions
"""

PREMIUM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --bg-primary: #09090f;
        --bg-card: rgba(18, 18, 35, 0.7);
        --glass-border: rgba(100, 120, 230, 0.12);
        --accent-1: #667eea;
        --accent-2: #764ba2;
        --text-primary: #e8eaed;
        --text-secondary: #9ca3af;
        --text-muted: #5b6178;
        --green: #34d399;
        --amber: #fbbf24;
        --purple: #a78bfa;
        --radius: 16px;
        --ease: cubic-bezier(0.4, 0, 0.2, 1);
    }

    * { font-family: 'Inter', -apple-system, sans-serif !important; }

    .main .block-container {
        padding-top: 0.5rem; padding-bottom: 4rem;
        max-width: 820px;
    }

    /* ══════ AMBIENT GLOW ══════ */
    .main {
        background:
            radial-gradient(ellipse 600px 400px at 25% 5%, rgba(102,126,234,0.06) 0%, transparent 70%),
            radial-gradient(ellipse 500px 350px at 75% 85%, rgba(118,75,162,0.04) 0%, transparent 70%) !important;
    }

    /* ══════ HERO HEADER ══════ */
    .hero-header {
        padding: 0.3rem 0 0.2rem 0;
        animation: fadeUp 0.5s var(--ease) both;
    }
    .hero-title {
        background: linear-gradient(135deg, #667eea 0%, #a78bfa 40%, #c084fc 70%, #667eea 100%);
        background-size: 200% 200%;
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 1.6rem; font-weight: 800;
        letter-spacing: -0.5px; margin: 0; line-height: 1.2;
        animation: shimmer 4s ease-in-out infinite;
    }
    .hero-sub {
        color: var(--text-muted); font-size: 0.76rem; margin-top: 0.15rem;
        font-weight: 400; letter-spacing: 0.3px;
        animation: fadeUp 0.5s var(--ease) 0.1s both;
    }
    .hero-divider {
        height: 1px; margin: 0.5rem 0 0.3rem 0;
        background: linear-gradient(90deg, transparent, rgba(102,126,234,0.2), transparent);
        animation: fadeUp 0.5s var(--ease) 0.2s both;
    }
    @keyframes shimmer {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* ══════ QUICK-ACTION PILLS ══════ */
    .pill-row {
        display: flex; gap: 0.4rem; flex-wrap: wrap;
        margin: 0.3rem 0 0.6rem 0;
        animation: fadeUp 0.5s var(--ease) 0.25s both;
    }
    .pill {
        background: rgba(30, 30, 55, 0.5);
        border: 1px solid rgba(102,126,234,0.1);
        border-radius: 20px; padding: 0.28rem 0.7rem;
        font-size: 0.68rem; color: var(--text-muted);
        cursor: pointer; transition: all 0.25s var(--ease);
        letter-spacing: 0.2px;
    }
    .pill:hover {
        border-color: var(--accent-1); color: var(--accent-1);
        background: rgba(102,126,234,0.08);
        box-shadow: 0 0 16px rgba(102,126,234,0.1);
        transform: translateY(-1px);
    }

    /* ══════ CHAT BUBBLES ══════ */
    [data-testid="stChatMessage"] {
        border-radius: 16px !important;
        padding: 0.75rem 1rem !important;
        margin-bottom: 0.5rem !important;
        font-size: 0.84rem !important;
        line-height: 1.65 !important;
        animation: msgSlide 0.4s var(--ease) both;
        transition: all 0.25s var(--ease);
        background: rgba(20, 20, 38, 0.6) !important;
        border: 1px solid rgba(102,126,234,0.06) !important;
    }
    [data-testid="stChatMessage"]:hover {
        transform: translateY(-1px);
        border-color: rgba(102,126,234,0.12) !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }

    /* Avatar — rounded square with accent border */
    [data-testid="stChatMessage"] [data-testid="stAvatar"] img,
    [data-testid="stChatMessage"] img[style] {
        border-radius: 10px !important;
        border: 1.5px solid rgba(102,126,234,0.2) !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }

    @keyframes msgSlide {
        from { opacity: 0; transform: translateY(10px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* ══════ CHAT INPUT ══════ */
    .stChatInput > div {
        border: 1px solid rgba(102,126,234,0.12) !important;
        border-radius: 16px !important;
        background: rgba(15,15,28,0.7) !important;
        box-shadow: 0 2px 16px rgba(0,0,0,0.15) !important;
        transition: all 0.3s var(--ease);
    }
    .stChatInput > div:focus-within {
        border-color: var(--accent-1) !important;
        box-shadow:
            0 0 16px rgba(102,126,234,0.15),
            0 0 40px rgba(102,126,234,0.05) !important;
    }
    .stChatInput textarea {
        font-size: 0.84rem !important;
        color: var(--text-primary) !important;
    }
    .stChatInput textarea::placeholder { color: var(--text-muted) !important; }

    /* ══════ LEAD CAPTURED CARD ══════ */
    @keyframes celebrateBounce {
        0%   { opacity: 0; transform: scale(0.6) translateY(30px); }
        50%  { opacity: 1; transform: scale(1.03) translateY(-4px); }
        100% { transform: scale(1) translateY(0); }
    }
    .lead-captured-card {
        background: linear-gradient(135deg, #059669 0%, #10b981 50%, #34d399 100%);
        padding: 1.2rem 1.4rem; border-radius: 14px; color: white;
        text-align: center; margin: 0.6rem 0;
        box-shadow: 0 8px 30px rgba(16,185,129,0.3);
        animation: celebrateBounce 0.6s var(--ease);
        position: relative; overflow: hidden;
    }
    .lead-captured-card::before {
        content: ''; position: absolute; top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: conic-gradient(from 0deg, transparent 0%, rgba(255,255,255,0.1) 10%, transparent 20%);
        animation: sparkle 3s linear infinite;
    }
    @keyframes sparkle { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    .lead-captured-card h3 {
        margin: 0 0 0.4rem 0; font-weight: 700; font-size: 0.95rem;
        position: relative; z-index: 1;
    }
    .lead-captured-card p {
        margin: 0.1rem 0; font-size: 0.76rem; opacity: 0.93;
        position: relative; z-index: 1;
    }

    /* ══════ SIDEBAR ══════ */
    div[data-testid="stSidebarContent"] {
        background: linear-gradient(180deg, #0a0a14 0%, #0d0d1a 50%, #10102a 100%) !important;
    }
    .brand-container {
        padding: 0.4rem 0 0.6rem 0;
        border-bottom: 1px solid rgba(102,126,234,0.08);
        margin-bottom: 0.6rem;
        animation: fadeUp 0.4s var(--ease) both;
    }
    .brand-text {
        background: linear-gradient(135deg, #667eea 0%, #a78bfa 50%, #c084fc 100%);
        background-size: 200% 200%;
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 1.05rem; font-weight: 800; letter-spacing: -0.3px;
        animation: shimmer 4s ease-in-out infinite;
    }
    .brand-role {
        color: var(--text-muted); font-size: 0.65rem; margin-top: 0.1rem;
        letter-spacing: 0.8px; text-transform: uppercase; font-weight: 600;
    }

    /* ══════ SIDEBAR CARDS ══════ */
    .s-card {
        background: rgba(16, 16, 32, 0.6);
        border: 1px solid rgba(102,126,234,0.08);
        border-radius: 14px;
        padding: 0.75rem 0.85rem;
        margin-bottom: 0.5rem;
        transition: all 0.25s var(--ease);
        position: relative;
    }
    .s-card:hover {
        border-color: rgba(102,126,234,0.18);
        box-shadow: 0 4px 20px rgba(102,126,234,0.06);
    }
    .s-card-1 { animation: fadeUp 0.4s var(--ease) 0.05s both; }
    .s-card-2 { animation: fadeUp 0.4s var(--ease) 0.12s both; }
    .s-card-3 { animation: fadeUp 0.4s var(--ease) 0.19s both; }

    .s-title {
        color: var(--purple); margin: 0 0 0.4rem 0; font-size: 0.6rem;
        text-transform: uppercase; letter-spacing: 1.5px; font-weight: 700;
        display: flex; align-items: center; gap: 0.35rem;
    }
    .s-title-icon {
        display: inline-flex; align-items: center; justify-content: center;
        width: 16px; height: 16px; border-radius: 5px;
        background: rgba(167,139,250,0.1); font-size: 0.5rem;
        color: var(--purple);
    }
    .s-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 0.2rem 0; font-size: 0.73rem;
        border-bottom: 1px solid rgba(255,255,255,0.025);
        transition: all 0.2s var(--ease);
    }
    .s-row:last-child { border-bottom: none; }
    .s-row:hover { background: rgba(255,255,255,0.015); border-radius: 4px; padding: 0.2rem 0.3rem; }
    .s-lbl { color: var(--text-secondary); font-weight: 500; }
    .s-val { color: var(--text-primary); font-weight: 600; font-variant-numeric: tabular-nums; }
    .s-wait { color: var(--text-muted); font-style: italic; font-size: 0.68rem; }

    /* ══════ BADGES ══════ */
    .badge {
        display: inline-flex; align-items: center;
        padding: 0.15rem 0.55rem; border-radius: 16px;
        font-size: 0.58rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.4px;
        animation: badgePop 0.3s var(--ease);
    }
    @keyframes badgePop {
        from { transform: scale(0.7); opacity: 0; }
        to   { transform: scale(1); opacity: 1; }
    }
    .badge-greeting  { background: rgba(55,65,81,0.5); color: #9ca3af; }
    .badge-inquiry   { background: rgba(146,64,14,0.3); color: #fbbf24; box-shadow: 0 0 8px rgba(251,191,36,0.08); }
    .badge-high      { background: rgba(6,95,70,0.3); color: #34d399; box-shadow: 0 0 8px rgba(52,211,153,0.1); }
    .badge-lead      { background: rgba(88,28,135,0.3); color: #c084fc; box-shadow: 0 0 8px rgba(192,132,252,0.1); }
    .badge-new       { background: rgba(31,41,55,0.5); color: #6b7280; }

    /* ══════ SCORE BAR ══════ */
    .score-container { margin: 0.2rem 0 0; }
    .score-lbl {
        font-size: 0.7rem; font-weight: 700; margin-bottom: 0.15rem;
        display: flex; align-items: center; gap: 0.3rem;
    }
    .score-value { font-family: 'JetBrains Mono', monospace !important; }
    .score-low  { color: #9ca3af; }
    .score-med  { color: #fbbf24; }
    .score-high { color: #34d399; }
    .bar-bg {
        height: 4px; border-radius: 3px;
        background: rgba(31,41,55,0.7);
        overflow: hidden; margin-top: 0.15rem;
    }
    .bar-fill {
        height: 100%; border-radius: 3px;
        animation: barGrow 0.8s var(--ease);
    }
    @keyframes barGrow { from { width: 0 !important; } }
    .bar-low  { background: linear-gradient(90deg,#4b5563,#9ca3af); }
    .bar-med  { background: linear-gradient(90deg,#d97706,#fbbf24); box-shadow: 0 0 6px rgba(251,191,36,0.2); }
    .bar-high { background: linear-gradient(90deg,#059669,#34d399); box-shadow: 0 0 8px rgba(52,211,153,0.25); }

    /* ══════ STATUS DOT ══════ */
    .dot-active {
        display: inline-block; width: 6px; height: 6px; border-radius: 50%;
        background: var(--green); margin-right: 4px;
        box-shadow: 0 0 6px rgba(52,211,153,0.4);
        animation: dotPulse 2s ease-in-out infinite;
    }
    @keyframes dotPulse {
        0%, 100% { opacity: 1; }
        50%      { opacity: 0.4; }
    }
    .dot-done {
        display: inline-block; width: 6px; height: 6px; border-radius: 50%;
        background: var(--purple); margin-right: 4px;
        box-shadow: 0 0 6px rgba(167,139,250,0.4);
    }

    /* ══════ TECH FOOTER ══════ */
    .tech-footer {
        background: rgba(16,16,32,0.4);
        border: 1px solid rgba(102,126,234,0.06);
        border-radius: 10px; padding: 0.6rem 0.8rem;
        animation: fadeUp 0.4s var(--ease) 0.3s both;
    }
    .tech-tag {
        display: inline-block; padding: 0.12rem 0.45rem;
        background: rgba(102,126,234,0.06);
        border: 1px solid rgba(102,126,234,0.08);
        border-radius: 6px; font-size: 0.58rem; color: var(--text-muted);
        margin: 0.12rem 0.06rem; transition: all 0.2s var(--ease); font-weight: 500;
    }
    .tech-tag:hover {
        background: rgba(102,126,234,0.12);
        color: var(--accent-1);
    }

    /* ══════ SCROLLBAR ══════ */
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(102,126,234,0.15); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(102,126,234,0.3); }

    /* ══════ HIDE STREAMLIT DEFAULTS ══════ */
    #MainMenu { visibility: hidden; }
    header { visibility: hidden; }
    footer { visibility: hidden; }
    .stDeployButton { display: none; }
    .stHtml { height: 0 !important; overflow: hidden !important; margin: 0 !important; padding: 0 !important; }

    /* ══════ FLOATING WHATSAPP BUTTON ══════ */
    @keyframes pulse-wa {
        0% { box-shadow: 0 0 0 0 rgba(37, 211, 102, 0.7); }
        70% { box-shadow: 0 0 0 15px rgba(37, 211, 102, 0); }
        100% { box-shadow: 0 0 0 0 rgba(37, 211, 102, 0); }
    }
    .floating-wa {
        position: fixed;
        bottom: 30px;
        right: 30px;
        background-color: #25D366;
        color: white;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-decoration: none;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 999999;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        animation: pulse-wa 2s infinite;
    }
    .floating-wa:hover {
        transform: translateY(-4px) scale(1.05);
        box-shadow: 0 6px 16px rgba(0,0,0,0.4), 0 0 0 2px rgba(37, 211, 102, 0.5);
    }
    .floating-wa svg {
        width: 32px;
        height: 32px;
        fill: white;
    }
</style>
"""

PARTICLE_HTML = """
<html>
<head><style>
    body { margin: 0; overflow: hidden; background: transparent; }
    canvas { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; }
</style></head>
<body>
<canvas id="p"></canvas>
<script>
const c = document.getElementById('p');
const ctx = c.getContext('2d');
let W, H;
function resize() { W = c.width = window.innerWidth; H = c.height = window.innerHeight; }
resize();
window.addEventListener('resize', resize);
const pts = [];
for (let i = 0; i < 35; i++) {
    pts.push({ x: Math.random()*W, y: Math.random()*H,
        vx: (Math.random()-0.5)*0.25, vy: (Math.random()-0.5)*0.25,
        r: Math.random()*1.5+0.5, a: Math.random()*0.25+0.08 });
}
function draw() {
    ctx.clearRect(0,0,W,H);
    pts.forEach(p => {
        p.x += p.vx; p.y += p.vy;
        if (p.x<0||p.x>W) p.vx*=-1;
        if (p.y<0||p.y>H) p.vy*=-1;
        ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
        ctx.fillStyle='rgba(102,126,234,'+p.a+')'; ctx.fill();
    });
    for (let i=0;i<pts.length;i++) {
        for (let j=i+1;j<pts.length;j++) {
            const dx=pts[i].x-pts[j].x, dy=pts[i].y-pts[j].y;
            const d=Math.sqrt(dx*dx+dy*dy);
            if (d<140) {
                ctx.beginPath(); ctx.moveTo(pts[i].x,pts[i].y); ctx.lineTo(pts[j].x,pts[j].y);
                ctx.strokeStyle='rgba(102,126,234,'+(0.05*(1-d/140))+')';
                ctx.lineWidth=0.5; ctx.stroke();
            }
        }
    }
    requestAnimationFrame(draw);
}
draw();
</script>
</body>
</html>
"""
