"""
app.py  —  AI Property Advisor
Complete UI rewrite: high-contrast, fully visible chat interface.
Run:  streamlit run app.py
"""

import uuid
import re
import streamlit as st

st.set_page_config(
    page_title="AI Property Advisor — Astrick",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from agent.advisor_agent import build_agent, run_agent_sync

# ═══════════════════════════════════════════════════════════════════════════════
#  MASTER CSS
# ═══════════════════════════════════════════════════════════════════════════════
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Tokens ─────────────────────────────────────────────────────────────── */
:root {
  --bg:         #0A0A0F;
  --bg2:        #111118;
  --bg3:        #18181F;
  --bg4:        #1E1E28;
  --surface:    #22222E;
  --surfaceHi:  #2A2A38;
  --gold:       #F0C060;
  --goldDim:    #C8962A;
  --goldGlow:   rgba(240,192,96,0.18);
  --white:      #FFFFFF;
  --offwhite:   #F4F0E8;
  --gray1:      #D0CCC4;
  --gray2:      #A09890;
  --gray3:      #605850;
  --border:     rgba(240,192,96,0.15);
  --borderHi:   rgba(240,192,96,0.45);
  --radius:     14px;
  --radiusSm:   8px;
  --shadow:     0 8px 40px rgba(0,0,0,0.6);
}

/* ── Base ───────────────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
section.main { background: var(--bg) !important; }

[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stSidebar"],
#MainMenu, footer { display: none !important; }

.block-container {
  padding: 0 !important;
  max-width: 100% !important;
}

/* ── Typography globals ─────────────────────────────────────────────────── */
body, p, li, span, label, div {
  font-family: 'Inter', sans-serif !important;
  color: var(--offwhite);
}

/* ══════════════════════════════════════════════════════════════════════════
   LANDING PAGE
═══════════════════════════════════════════════════════════════════════════ */

/* ── Hero ───────────────────────────────────────────────────────────────── */
.hero {
  position: relative;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 5rem 2rem 4rem;
  overflow: hidden;
  background:
    radial-gradient(ellipse 70% 55% at 50% -5%,  rgba(240,192,96,0.14) 0%, transparent 65%),
    radial-gradient(ellipse 45% 35% at 85% 85%,  rgba(240,192,96,0.07) 0%, transparent 55%),
    var(--bg);
}

/* subtle grid */
.hero::before {
  content: '';
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(240,192,96,0.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(240,192,96,0.035) 1px, transparent 1px);
  background-size: 64px 64px;
  pointer-events: none;
}

/* animated gradient orb */
.hero::after {
  content: '';
  position: absolute;
  width: 600px; height: 600px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(240,192,96,0.06) 0%, transparent 70%);
  top: -150px; left: 50%; transform: translateX(-50%);
  animation: orbFloat 8s ease-in-out infinite;
  pointer-events: none;
}

@keyframes orbFloat {
  0%,100% { transform: translateX(-50%) translateY(0); }
  50%      { transform: translateX(-50%) translateY(30px); }
}

.hero-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(240,192,96,0.08);
  border: 1px solid var(--borderHi);
  color: var(--gold);
  padding: 7px 18px;
  border-radius: 100px;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  margin-bottom: 2.2rem;
  position: relative; z-index: 1;
}

.hero-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  background: var(--gold);
  animation: blink 2s ease-in-out infinite;
}

@keyframes blink {
  0%,100% { opacity: 1; box-shadow: 0 0 6px var(--gold); }
  50%      { opacity: 0.3; box-shadow: none; }
}

.hero-title {
  font-family: 'Playfair Display', serif !important;
  font-size: clamp(3.2rem, 7.5vw, 6.8rem);
  font-weight: 700;
  line-height: 1.04;
  letter-spacing: -0.025em;
  color: var(--white) !important;
  margin: 0 0 1.2rem;
  position: relative; z-index: 1;
}

.hero-title-em {
  font-style: italic;
  background: linear-gradient(135deg, var(--gold) 0%, #FFE08A 50%, var(--goldDim) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-sub {
  font-size: clamp(1rem, 1.8vw, 1.2rem);
  font-weight: 400;
  color: var(--gray1) !important;
  max-width: 540px;
  line-height: 1.75;
  margin: 0 auto 3.2rem;
  position: relative; z-index: 1;
}

/* Stats row */
.hero-stats {
  display: flex;
  gap: 0;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 3.5rem;
  position: relative; z-index: 1;
  background: rgba(240,192,96,0.04);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  max-width: 520px;
  margin-left: auto;
  margin-right: auto;
}

.stat-item {
  flex: 1;
  min-width: 100px;
  padding: 1.4rem 1rem;
  text-align: center;
  border-right: 1px solid var(--border);
}
.stat-item:last-child { border-right: none; }

.stat-num {
  font-family: 'Playfair Display', serif !important;
  font-size: 2rem;
  font-weight: 700;
  color: var(--gold) !important;
  display: block;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 0.68rem;
  color: var(--gray2) !important;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-weight: 500;
}

/* ── CTA button ─────────────────────────────────────────────────────────── */
.stButton > button {
  background: linear-gradient(135deg, var(--gold), #FFE08A, var(--goldDim)) !important;
  background-size: 200% 200% !important;
  color: #0A0A0F !important;
  border: none !important;
  padding: 0.95rem 2.6rem !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 0.92rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.04em !important;
  border-radius: 100px !important;
  cursor: pointer !important;
  transition: all 0.3s ease !important;
  box-shadow: 0 6px 30px rgba(240,192,96,0.35) !important;
  animation: shimmer 3s ease infinite !important;
}

@keyframes shimmer {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.stButton > button:hover {
  transform: translateY(-3px) scale(1.02) !important;
  box-shadow: 0 12px 45px rgba(240,192,96,0.55) !important;
}

/* ── Feature section ────────────────────────────────────────────────────── */
.features-wrap {
  background: var(--bg2);
  padding: 5.5rem 3rem;
  border-top: 1px solid var(--border);
}

.features-inner {
  max-width: 700px;
  margin: 0 auto;
  text-align: center;
}

.section-eyebrow {
  text-align: center;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--gold) !important;
  margin-bottom: 0.75rem;
}

.section-title {
  font-family: 'Playfair Display', serif !important;
  font-size: clamp(1.9rem, 3.5vw, 2.8rem);
  font-weight: 700;
  color: var(--white) !important;
  text-align: center;
  margin-bottom: 0.5rem;
  line-height: 1.2;
}

.section-sub {
  text-align: center;
  color: var(--gray2) !important;
  font-size: 1rem;
  margin-bottom: 3.5rem;
  max-width: 500px;
  margin-left: auto;
  margin-right: auto;
}

.feat-card {
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 2rem 1.6rem;
  height: 100%;
  transition: all 0.35s ease;
  position: relative;
  overflow: hidden;
}

.feat-card::after {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, transparent, var(--gold), transparent);
  opacity: 0;
  transition: opacity 0.35s;
}

.feat-card:hover { transform: translateY(-5px); border-color: var(--borderHi); }
.feat-card:hover::after { opacity: 1; }

.feat-icon {
  font-size: 2rem;
  margin-bottom: 1.1rem;
  display: block;
}

.feat-card h3 {
  font-family: 'Playfair Display', serif !important;
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--white) !important;
  margin: 0 0 0.6rem;
}

.feat-card p {
  color: var(--gray1) !important;
  font-size: 0.88rem;
  line-height: 1.65;
  margin: 0;
}

/* ══════════════════════════════════════════════════════════════════════════
   CHAT PAGE — COMPLETE OVERRIDE
═══════════════════════════════════════════════════════════════════════════ */

/* Full page wrapper */
.chat-page {
  min-height: 100vh;
  background: var(--bg);
  display: flex;
  flex-direction: column;
}

/* Top bar */
.topbar {
  background: var(--bg2);
  border-bottom: 1px solid var(--border);
  padding: 0.9rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 100;
}

.topbar-brand {
  font-family: 'Playfair Display', serif !important;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--white) !important;
  display: flex;
  align-items: center;
  gap: 10px;
}

.topbar-dot {
  width: 9px; height: 9px;
  border-radius: 50%;
  background: #4ADE80;
  box-shadow: 0 0 8px rgba(74,222,128,0.7);
  animation: blink 2s infinite;
}

.topbar-status {
  font-size: 0.78rem;
  color: #4ADE80 !important;
  font-weight: 500;
  letter-spacing: 0.05em;
}

/* Memory bar */
.memory-bar {
  background: linear-gradient(90deg, rgba(240,192,96,0.07), rgba(240,192,96,0.03));
  border-bottom: 1px solid var(--border);
  padding: 0.6rem 2rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.memory-label {
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--gold) !important;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-right: 4px;
}

.mem-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: rgba(240,192,96,0.12);
  border: 1px solid rgba(240,192,96,0.3);
  color: var(--offwhite) !important;
  padding: 3px 10px;
  border-radius: 100px;
  font-size: 0.76rem;
  font-weight: 500;
}

/* ── Streamlit native chat messages — FULL OVERRIDE ── */

/* Container that wraps each message row */
[data-testid="stChatMessage"] {
  background: transparent !important;
  padding: 0.4rem 0 !important;
  margin: 0 !important;
  gap: 12px !important;
}

/* USER bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stMarkdownContainer"],
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown {
  background: linear-gradient(135deg, #2A5298, #1E3A7A) !important;
  color: #FFFFFF !important;
  border-radius: 18px 4px 18px 18px !important;
  padding: 0.85rem 1.2rem !important;
  font-size: 0.96rem !important;
  line-height: 1.65 !important;
  border: 1px solid rgba(100,150,255,0.3) !important;
  box-shadow: 0 4px 20px rgba(42,82,152,0.4) !important;
  max-width: 75% !important;
  margin-left: auto !important;
}

/* ASSISTANT bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stMarkdownContainer"],
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown {
  background: var(--bg3) !important;
  color: var(--offwhite) !important;
  border-radius: 4px 18px 18px 18px !important;
  padding: 0.85rem 1.2rem !important;
  font-size: 0.96rem !important;
  line-height: 1.7 !important;
  border: 1px solid var(--border) !important;
  box-shadow: 0 4px 20px rgba(0,0,0,0.4) !important;
  max-width: 85% !important;
}

/* All text inside bubbles must be readable */
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span {
  color: inherit !important;
  font-size: 0.96rem !important;
  line-height: 1.7 !important;
}

/* Bold text in assistant */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) strong {
  color: var(--gold) !important;
  font-weight: 700 !important;
}

/* Bold text in user */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) strong {
  color: #FFE08A !important;
  font-weight: 700 !important;
}

/* Bullet points */
[data-testid="stChatMessage"] ul,
[data-testid="stChatMessage"] ol {
  padding-left: 1.4rem;
  margin: 0.5rem 0;
}

[data-testid="stChatMessage"] li {
  margin-bottom: 0.3rem;
}

/* Avatar icons */
[data-testid="chatAvatarIcon-user"],
[data-testid="chatAvatarIcon-assistant"] {
  background: var(--surface) !important;
  border: 2px solid var(--border) !important;
  border-radius: 50% !important;
  font-size: 1.1rem !important;
  width: 40px !important;
  height: 40px !important;
  flex-shrink: 0 !important;
}

/* ── Chat input box — CRITICAL VISIBILITY FIX ── */
[data-testid="stChatInput"] {
  background: var(--bg3) !important;
  border: 2px solid var(--borderHi) !important;
  border-radius: 14px !important;
  padding: 0.2rem 0.5rem !important;
  box-shadow: 0 0 0 4px rgba(240,192,96,0.06), var(--shadow) !important;
  transition: border-color 0.2s, box-shadow 0.2s !important;
}

[data-testid="stChatInput"]:focus-within {
  border-color: var(--gold) !important;
  box-shadow: 0 0 0 4px rgba(240,192,96,0.15), var(--shadow) !important;
}

[data-testid="stChatInput"] textarea {
  background: transparent !important;
  color: var(--black) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 1rem !important;
  font-weight: 400 !important;
  line-height: 1.6 !important;
  caret-color: var(--gold) !important;
}

[data-testid="stChatInput"] textarea::placeholder {
  color: var(--gray2) !important;
  font-size: 0.95rem !important;
}

/* Send button inside chat input */
[data-testid="stChatInput"] button {
  background: var(--gold) !important;
  border-radius: 8px !important;
  color: #0A0A0F !important;
}

[data-testid="stChatInput"] button:hover {
  background: #FFE08A !important;
}

/* ── Suggestion chips (quick-start buttons) ── */
.sug-btn .stButton > button {
  background: var(--bg3) !important;
  color: var(--gray1) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radiusSm) !important;
  font-size: 0.82rem !important;
  font-weight: 500 !important;
  padding: 0.6rem 0.9rem !important;
  box-shadow: none !important;
  text-align: left !important;
  transition: all 0.2s ease !important;
  letter-spacing: 0 !important;
}

.sug-btn .stButton > button:hover {
  background: var(--surface) !important;
  border-color: var(--gold) !important;
  color: var(--gold) !important;
  transform: none !important;
  box-shadow: 0 2px 12px rgba(240,192,96,0.15) !important;
}

/* ── Home / Reset buttons ── */
.nav-btn .stButton > button {
  background: var(--bg3) !important;
  color: var(--gray1) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radiusSm) !important;
  font-size: 0.82rem !important;
  font-weight: 600 !important;
  padding: 0.5rem 1rem !important;
  box-shadow: none !important;
  letter-spacing: 0.02em !important;
}

.nav-btn .stButton > button:hover {
  background: var(--surface) !important;
  border-color: var(--borderHi) !important;
  color: var(--white) !important;
  transform: none !important;
  box-shadow: none !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] p,
.stSpinner p {
  color: var(--gray1) !important;
  font-size: 0.9rem !important;
}

/* ── Welcome empty state ── */
.welcome-state {
  text-align: center;
  padding: 4rem 2rem;
  color: var(--gray2) !important;
}

.welcome-state .wi {
  font-size: 3.5rem;
  margin-bottom: 1rem;
}

.welcome-state h3 {
  font-family: 'Playfair Display', serif !important;
  font-size: 1.5rem;
  color: var(--gray1) !important;
  margin-bottom: 0.5rem;
}

.welcome-state p {
  font-size: 0.92rem;
  color: var(--gray2) !important;
  max-width: 360px;
  margin: 0 auto;
  line-height: 1.6;
}

/* ── Footer ── */
.footer {
  background: var(--bg2);
  border-top: 1px solid var(--border);
  text-align: center;
  padding: 1.5rem 2rem;
  font-size: 0.78rem;
  color: var(--gray3) !important;
}

.footer a {
  color: var(--gold) !important;
  text-decoration: none;
}

.footer strong {
  color: var(--gray2) !important;
}

/* ── Divider helper ── */
.gap { margin: 1rem 0; }
.gap-sm { margin: 0.5rem 0; }

/* Streamlit columns gap fix */
[data-testid="column"] { padding: 0.3rem !important; }

/* Remove ugly default streamlit borders from chat area */
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
  gap: 0 !important;
}
</style>
"""


# ═══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════════
def init_session():
    defaults = {
        "session_id":   str(uuid.uuid4())[:8],
        "messages":     [],
        "agent":        None,
        "show_chat":    False,
        "user_profile": {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def get_agent():
    if st.session_state.agent is None:
        with st.spinner("⚙️ Initialising Astrick..."):
            st.session_state.agent = build_agent()
    return st.session_state.agent


# ═══════════════════════════════════════════════════════════════════════════════
#  LANDING PAGE
# ═══════════════════════════════════════════════════════════════════════════════
def render_hero():
    st.markdown("""
    <div class="hero">
      <div class="hero-eyebrow">
        <span class="hero-dot"></span>
        AI-Powered Real Estate Intelligence
      </div>
      <h1 class="hero-title">
        Find Your<br>
        <span class="hero-title-em">Perfect Property</span>
      </h1>
      <p class="hero-sub">
        Meet <strong>Astrick</strong> — your personal AI real estate consultant.
        He asks the right questions, analyses the market, and guides you to
        the smartest property decision.
      </p>
      <div class="hero-stats">
        <div class="stat-item">
          <span class="stat-num">6+</span>
          <span class="stat-label">Cities</span>
        </div>
        <div class="stat-item">
          <span class="stat-num">50+</span>
          <span class="stat-label">Listings</span>
        </div>
        <div class="stat-item">
          <span class="stat-num">AI</span>
          <span class="stat-label">Powered</span>
        </div>
        <div class="stat-item">
          <span class="stat-num">24/7</span>
          <span class="stat-label">Available</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    _, c, _ = st.columns([1.5, 2, 1.5])
    with c:
        if st.button("🏠  Start Consulting — It's Free", use_container_width=True):
            st.session_state.show_chat = True
            st.rerun()


def render_features():
    st.markdown("""
    <div class="features-wrap">
    <div class="features-inner">
        <p class="section-eyebrow">What Astrick Can Do</p>
        <h2 class="section-title">Everything You Need to<br>Decide Confidently</h2>
        <p class="section-sub">
        Our AI agent doesn't just answer — it guides, compares, and remembers.
        </p>
    </div>
    </div>
    """, unsafe_allow_html=True)

    cards = [
        ("🏘️", "Smart Property Match",
         "Tell us your budget and city — Astrick ranks properties by ROI, amenities, and lifestyle fit."),
        ("📊", "City Comparison Engine",
         "Torn between Bangalore and Hyderabad? Get a data-driven comparison in seconds."),
        ("📈", "Investment Strategy",
         "First-time buyer or seasoned investor — get a tailored strategy with projected returns."),
        ("🧠", "Session Memory",
         "Astrick remembers your preferences throughout the conversation. No repeating yourself."),
        ("🔍", "Market Intelligence",
         "Rental yields, 5-year appreciation, livability scores, and infrastructure ratings."),
        ("💬", "Consultant, Not Salesperson",
         "Honest trade-offs. Astrick only recommends what genuinely fits YOUR goals."),
    ]

    for row in [cards[:3], cards[3:]]:
        cols = st.columns(3, gap="medium")
        for col, (icon, title, desc) in zip(cols, row):
            with col:
                st.markdown(f"""
                <div class="feat-card">
                  <span class="feat-icon">{icon}</span>
                  <h3>{title}</h3>
                  <p>{desc}</p>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("<div class='gap-sm'></div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  CHAT PAGE
# ═══════════════════════════════════════════════════════════════════════════════
def render_topbar():
    """Sticky top bar with brand + status."""
    st.markdown("""
    <div class="topbar">
      <div class="topbar-brand">
        🏛️ &nbsp;AI Property Advisor
      </div>
      <div style="display:flex;align-items:center;gap:8px;">
        <span class="topbar-dot"></span>
        <span class="topbar-status">Astrick is Online</span>
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_memory_bar():
    profile = st.session_state.user_profile
    if not profile:
        return

    mapping = {
        "budget_lakh":   ("💰", "₹{}L"),
        "preferred_city":("📍", "{}"),
        "property_type": ("🏠", "{}"),
        "purpose":       ("🎯", "{}"),
    }
    chips = ""
    for key, (icon, fmt) in mapping.items():
        if key in profile:
            val = fmt.format(str(profile[key]).title())
            chips += f'<span class="mem-chip">{icon} {val}</span>'

    if chips:
        st.markdown(f"""
        <div class="memory-bar">
          <span class="memory-label">🧠 Remembered:</span>
          {chips}
        </div>
        """, unsafe_allow_html=True)


def render_messages():
    if not st.session_state.messages:
        st.markdown("""
        <div class="welcome-state">
          <div class="wi">🏛️</div>
          <h3>Hello! I'm Astrick Your personal Advisor</h3>
          <p>Your AI-powered real estate consultant. Ask me anything about properties,
             cities, or investment strategies.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant", avatar="🏛️"):
                st.markdown(msg["content"])


def render_suggestions():
    suggestions = [
        "🏙️  2BHK apartment in Bangalore under ₹1.2 Cr",
        "📊  Compare Mumbai vs Hyderabad",
        "💰  Best strategy for ₹50L investment, 5 years",
    ]
    st.markdown("<div style='margin: 0.8rem 0 0.4rem;'><span style='font-size:0.78rem;color:#A09890;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;'>Try asking:</span></div>", unsafe_allow_html=True)
    cols = st.columns(3, gap="small")
    for col, sug in zip(cols, suggestions):
        with col:
            st.markdown('<div class="sug-btn">', unsafe_allow_html=True)
            if st.button(sug, use_container_width=True, key=f"sug_{sug[:15]}"):
                handle_input(sug.split("  ", 1)[-1].strip())
            st.markdown('</div>', unsafe_allow_html=True)


def render_chat_page():
    render_topbar()
    render_memory_bar()

    # Nav row: Home + Reset
    c1, _, c2 = st.columns([1, 7, 1])
    with c1:
        st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
        if st.button("← Home", key="home_btn", use_container_width=True):
            st.session_state.show_chat = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
        if st.button("🔄 Reset", key="reset_btn", use_container_width=True):
            st.session_state.messages = []
            st.session_state.user_profile = {}
            st.session_state.agent = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Centre column for chat
    _, mid, _ = st.columns([0.5, 8, 0.5])
    with mid:
        render_messages()

        if not st.session_state.messages:
            render_suggestions()

        st.markdown("<div class='gap-sm'></div>", unsafe_allow_html=True)

        user_input = st.chat_input(
            "Ask Astrick about properties, cities, or investment strategies...",
        )
        if user_input:
            handle_input(user_input)


# ═══════════════════════════════════════════════════════════════════════════════
#  LOGIC
# ═══════════════════════════════════════════════════════════════════════════════
def handle_input(text: str):
    st.session_state.messages.append({"role": "user", "content": text})
    agent = get_agent()
    with st.spinner("✦ Astrick is thinking..."):
        reply = run_agent_sync(
            agent=agent,
            user_message=text,
            session_id=st.session_state.session_id,
            history=st.session_state.messages[:-1],
        )
    st.session_state.messages.append({"role": "assistant", "content": reply})
    _sniff_profile(reply, text)
    st.rerun()


def _sniff_profile(reply: str, user_msg: str):
    combined = (reply + " " + user_msg).lower()
    p = st.session_state.user_profile

    m = re.search(r"₹?\s*(\d+\.?\d*)\s*(l\b|lakh|lac|cr\b|crore)", combined)
    if m and "budget_lakh" not in p:
        num = float(m.group(1))
        if "cr" in m.group(2):
            num *= 100
        p["budget_lakh"] = num

    for city in ["mumbai","bangalore","delhi","hyderabad","pune","chennai"]:
        if city in combined and "preferred_city" not in p:
            p["preferred_city"] = city

    for pt in ["apartment","villa","plot","flat","house"]:
        if pt in combined and "property_type" not in p:
            p["property_type"] = "apartment" if pt == "flat" else pt

    for pur in ["investment","self use","rental","renting"]:
        if pur in combined and "purpose" not in p:
            p["purpose"] = pur.replace(" ", "_")

    st.session_state.user_profile = p


# ═══════════════════════════════════════════════════════════════════════════════
#  FOOTER
# ═══════════════════════════════════════════════════════════════════════════════
def render_footer():
    st.markdown("""
    <div class="footer">
      🏛️ <strong>AI Property Advisor</strong> &nbsp;—&nbsp;
      Built with AutoGen 0.7.5 · Groq LLaMA 3.3 · Streamlit &nbsp;|&nbsp;
      Not a registered financial advisor. Projections are indicative only.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    init_session()
    st.markdown(CSS, unsafe_allow_html=True)

    if st.session_state.show_chat:
        render_chat_page()
    else:
        render_hero()
        render_features()

    render_footer()


if __name__ == "__main__":
    main()