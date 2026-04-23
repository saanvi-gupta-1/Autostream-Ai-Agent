import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from agent_logic import build_graph, get_initial_state
from intent import INTENT_DISPLAY_LABELS, get_score_label
from styles import PREMIUM_CSS

# ─── Avatar paths ───
ASSETS = Path(__file__).parent / "assets"
AGENT_AVATAR = str(ASSETS / "agent_avatar.png")
USER_AVATAR = str(ASSETS / "user_avatar.png")

st.set_page_config(
    page_title="AutoStream AI | Aria",
    page_icon="▶",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ─── Inject premium styles ───
st.markdown(PREMIUM_CSS, unsafe_allow_html=True)


# ─── helpers ───
def _badge(intent_value: str) -> str:
    label = INTENT_DISPLAY_LABELS.get(intent_value, "New")
    css = {
        "greeting": "badge-greeting",
        "product_inquiry": "badge-inquiry",
        "high_intent_lead": "badge-high",
        "lead_info_response": "badge-lead",
    }.get(intent_value, "badge-new")
    return f'<span class="badge {css}">{label}</span>'


def _level(score: int) -> str:
    return "low" if score < 40 else ("med" if score < 75 else "high")


def _val(v, placeholder="Waiting..."):
    return (
        f'<span class="s-val">{v}</span>'
        if v
        else f'<span class="s-wait">{placeholder}</span>'
    )


# ─── session ───
def init_session():
    if "state" not in st.session_state:
        st.session_state.state = get_initial_state()
        st.session_state.graph = build_graph()
        st.session_state.msgs = []
        st.session_state.captured = False


# ─── sidebar ───
def render_sidebar():
    with st.sidebar:
        # Brand — clean, no emoji
        st.markdown(
            """<div class="brand-container">
            <p class="brand-text">AutoStream AI</p>
            <p class="brand-role">Sales Intelligence Agent</p>
        </div>""",
            unsafe_allow_html=True,
        )

        s = st.session_state.state
        intent_val = s.get("intent", "unknown")
        score = s.get("lead_score", 0)
        lvl = _level(score)
        platform = s.get("user_platform")
        is_captured = s.get("lead_captured", False)
        dot = "dot-done" if is_captured else "dot-active"
        status = "Captured" if is_captured else "Active"

        # ── Card 1: Lead Intelligence ──
        st.markdown(
            f"""<div class="s-card s-card-1">
            <p class="s-title"><span class="s-title-icon">&#9670;</span> Lead Intelligence</p>
            <div class="s-row"><span class="s-lbl">Intent</span>{_badge(intent_val)}</div>
            <div class="s-row"><span class="s-lbl">Platform</span>{_val(platform)}</div>
            <div class="score-container">
                <div class="s-row"><span class="s-lbl">Lead Score</span></div>
                <p class="score-lbl score-{lvl}">
                    <span class="score-value">{score}%</span> · {get_score_label(score)}
                </p>
                <div class="bar-bg"><div class="bar-fill bar-{lvl}" style="width:{score}%"></div></div>
            </div>
        </div>""",
            unsafe_allow_html=True,
        )

        # ── Card 2: Lead Details ──
        name = s.get("lead_name")
        email = s.get("lead_email")
        lp = s.get("lead_platform")

        st.markdown(
            f"""<div class="s-card s-card-2">
            <p class="s-title"><span class="s-title-icon">&#9679;</span> Lead Details</p>
            <div class="s-row"><span class="s-lbl">Name</span>{_val(name)}</div>
            <div class="s-row"><span class="s-lbl">Email</span>{_val(email)}</div>
            <div class="s-row"><span class="s-lbl">Platform</span>{_val(lp)}</div>
            <div class="s-row"><span class="s-lbl">Status</span><span class="s-val"><span class="{dot}"></span>{status}</span></div>
        </div>""",
            unsafe_allow_html=True,
        )

        # ── Card 3: Session ──
        turns = len([m for m in s.get("messages", []) if m.get("role") == "user"])
        mem = len(s.get("messages", []))
        topic = s.get("last_topic") or "—"

        st.markdown(
            f"""<div class="s-card s-card-3">
            <p class="s-title"><span class="s-title-icon">&#9889;</span> Session</p>
            <div class="s-row"><span class="s-lbl">Turns</span><span class="s-val">{turns}</span></div>
            <div class="s-row"><span class="s-lbl">Memory</span><span class="s-val">{mem} msgs</span></div>
            <div class="s-row"><span class="s-lbl">Topic</span><span class="s-val">{topic}</span></div>
        </div>""",
            unsafe_allow_html=True,
        )

        # ── Card 4: Integrations ──
        whatsapp_icon = '<img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" style="width:14px;height:14px;margin-right:6px;vertical-align:-2px;">'
        st.markdown(
            f"""<div class="s-card s-card-4" style="animation-delay: 0.6s;">
            <p class="s-title"><span class="s-title-icon">&#9842;</span> Integrations</p>
            <div class="s-row"><span class="s-lbl">Webhook</span><span class="s-val">Port 8000</span></div>
            <div class="s-row"><span class="s-lbl">{whatsapp_icon}WhatsApp</span><span class="s-val"><span class="status-dot green"></span>Active</span></div>
        </div>""",
            unsafe_allow_html=True,
        )


# ─── chat ───
def render_chat():
    # Hero header — clean, no emoji
    st.markdown(
        """<div class="hero-header">
        <p class="hero-title">Aria</p>
        <p class="hero-sub">AutoStream AI Sales Assistant — Ask about plans, pricing, or get started</p>
    </div>
    <div class="hero-divider"></div>""",
        unsafe_allow_html=True,
    )

    # Quick-action pills — clean text, no emoji
    st.markdown(
        """<div class="pill-row">
        <span class="pill">Pricing & Plans</span>
        <span class="pill">Features</span>
        <span class="pill">Get Started</span>
        <span class="pill">Compare Plans</span>
    </div>""",
        unsafe_allow_html=True,
    )

    # Welcome message — clean, minimal
    if not st.session_state.msgs:
        st.session_state.msgs.append(
            {
                "role": "assistant",
                "content": (
                    "Hey there — I'm **Aria**, your AutoStream assistant.\n\n"
                    "I can help you with:\n"
                    "- Plan details & pricing\n"
                    "- Feature comparisons\n"
                    "- Getting started with a free trial\n\n"
                    "What would you like to know?"
                ),
            }
        )

    # Render messages with image avatars
    for msg in st.session_state.msgs:
        avatar = AGENT_AVATAR if msg["role"] == "assistant" else USER_AVATAR
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

            if msg.get("lead_result"):
                r = msg["lead_result"]
                st.markdown(
                    f"""<div class="lead-captured-card">
                    <h3>Lead Captured Successfully</h3>
                    <p><strong>Name:</strong> {r['name']}</p>
                    <p><strong>Email:</strong> {r['email']}</p>
                    <p><strong>Platform:</strong> {r['platform']}</p>
                    <p><strong>Lead ID:</strong> {r['lead_id']}</p>
                </div>""",
                    unsafe_allow_html=True,
                )


# ─── process (phase 2 — runs after user message is already displayed) ───
def process_pending():
    """Process a pending user input. Called AFTER the user message is already visible."""
    user_input = st.session_state.pop("pending_input", None)
    if not user_input:
        return

    s = st.session_state.state
    s["messages"].append({"role": "user", "content": user_input})

    try:
        result = st.session_state.graph.invoke(s)
        st.session_state.state = result
        reply = result["messages"][-1]["content"]

        entry = {"role": "assistant", "content": reply}

        if result.get("lead_captured") and not st.session_state.captured:
            entry["lead_result"] = {
                "name": result.get("lead_name", ""),
                "email": result.get("lead_email", ""),
                "platform": result.get("lead_platform", ""),
                "lead_id": f"LEAD-{abs(hash(result.get('lead_email', ''))) % 100000:05d}",
            }
            st.session_state.captured = True

        st.session_state.msgs.append(entry)

    except Exception as e:
        st.session_state.msgs.append(
            {
                "role": "assistant",
                "content": f"I'm having a temporary issue. Please try again.\n\n`{str(e)[:200]}`",
            }
        )


# ─── main ───
def main():
    init_session()

    # Floating WhatsApp Button (Official Green Circular with Pulse)
    st.markdown("""
        <a href="https://wa.me/910000000000?text=Hi!%20I'm%20interested%20in%20AutoStream.%20Can%20you%20help%20me%20get%20started%3F" target="_blank" class="floating-wa">
            <svg viewBox="0 0 24 24"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51a12.8 12.8 0 0 0-.57-.01c-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413z"/></svg>
        </a>
    """, unsafe_allow_html=True)

    render_sidebar()
    render_chat()

    # Phase 2: if there's a pending input, process it (user msg is already shown)
    if "pending_input" in st.session_state:
        with st.chat_message("assistant", avatar=AGENT_AVATAR):
            with st.spinner("Thinking..."):
                process_pending()
        st.rerun()

    # Phase 1: user submits → save msg, store pending, rerun immediately
    if prompt := st.chat_input("Ask about pricing, features, or plans..."):
        st.session_state.msgs.append({"role": "user", "content": prompt})
        st.session_state.pending_input = prompt
        st.rerun()


if __name__ == "__main__":
    main()
