import streamlit as st
import html
from pathlib import Path
import base64
import chromadb
from chromadb.utils import embedding_functions
from concurrent.futures import ThreadPoolExecutor
import re
import functools
import os
from google import genai  # Modern 2026 SDK

st.set_page_config(page_title="faithspace", page_icon="🔮", layout="centered")

# ─────────────────────────────────────────────
# GEMINI 3 MODEL CONFIGURATION (2026)
# ─────────────────────────────────────────────
API_KEY = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("🔮 Welcome to FaithSpace! Please set your GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

# Initialize the modern Client
client = genai.Client(api_key=API_KEY)
MODEL_ID = "gemini-3-flash-preview"

# ─────────────────────────────────────────────
# home link behavior
# ─────────────────────────────────────────────
if st.query_params.get("home") == "1":
    st.session_state.entered  = False
    st.session_state.religion = None
    st.session_state.messages = []
    st.query_params.clear()
    st.rerun()

# ─────────────────────────────────────────────
# local font
# ─────────────────────────────────────────────
def load_local_font(font_path):
    path = Path(font_path)
    if path.exists():
        data = base64.b64encode(path.read_bytes()).decode()
        return (
            "@font-face {"
            "  font-family: 'The Augusta';"
            f" src: url(data:font/otf;base64,{data}) format('opentype');"
            "  font-weight: normal; font-style: normal;"
            "}"
        )
    return ""

augusta_font = load_local_font("The Augusta.otf")

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');
{augusta_font}

html,body,#root,.stApp,.stAppViewContainer,.main,.block-container{{
    background:
        radial-gradient(circle at 20% 12%,rgba(255,139,212,.30),transparent 28%),
        radial-gradient(circle at 85% 18%,rgba(192,132,252,.34),transparent 34%),
        radial-gradient(circle at 50% 90%,rgba(76,29,149,.45),transparent 42%),
        linear-gradient(135deg,#16051f 0%,#2b123b 45%,#08000d 100%) !important;
    color:#fff7ff !important;
}}
html,body,div,p,span,button,textarea{{font-family:'Poppins',sans-serif !important;}}
header,footer,#MainMenu,[data-testid="stToolbar"],section[data-testid="stSidebar"]{{display:none !important;}}
.block-container{{max-width:1120px;padding-top:1rem;padding-bottom:9rem;}}

.corner-logo{{
    position:fixed;top:18px;left:24px;z-index:9999;
    font-family:'The Augusta','Poppins',sans-serif !important;
    font-size:1.9rem;line-height:1.35;padding:6px 12px 2px;white-space:nowrap;
    text-decoration:none !important;
    background:linear-gradient(90deg,#ff9bdb,#f5d0fe,#c084fc,#ff9bdb);
    background-size:280% auto;-webkit-background-clip:text;-webkit-text-fill-color:transparent;
    animation:shimmer 5s linear infinite;
    filter:drop-shadow(0 0 14px rgba(255,155,219,.45));
}}
.home-spacer{{height:15vh;}}.path-spacer{{height:13vh;}}

.glow-title{{
    font-family:'The Augusta','Poppins',sans-serif !important;
    text-align:center;font-size:clamp(4.4rem,11vw,8.7rem);line-height:1.35;
    padding-top:.45em;padding-bottom:.18em;margin-bottom:.4rem;
    white-space:nowrap;overflow:visible;
    background:linear-gradient(90deg,#ff9bdb,#f5d0fe,#c084fc,#ff9bdb);
    background-size:280% auto;-webkit-background-clip:text;-webkit-text-fill-color:transparent;
    animation:shimmer 5s linear infinite;text-shadow:0 0 50px rgba(255,155,219,.35);
}}
.choose-title{{
    text-align:center;font-family:'Poppins',sans-serif !important;
    font-size:clamp(1.65rem,4.2vw,3.45rem);font-weight:800;line-height:1.2;
    margin-bottom:2.7rem;color:#fff7ff;white-space:nowrap;
}}
.choose-glow{{
    background:linear-gradient(90deg,#ff9bdb,#f5d0fe,#c084fc,#ff9bdb);
    background-size:280% auto;-webkit-background-clip:text;-webkit-text-fill-color:transparent;
    animation:shimmer 5s linear infinite;filter:drop-shadow(0 0 18px rgba(255,155,219,.42));
}}
@keyframes shimmer{{from{{background-position:0% center;}}to{{background-position:280% center;}}}}

.subtitle{{text-align:center;color:#f3e8ff;font-size:1.18rem;opacity:.92;margin-bottom:3rem;}}
.religion-title{{text-align:center;color:#f5d0fe;font-size:1.85rem;font-weight:800;margin:1.8rem 0 1.4rem;}}

.daily-card{{
    background:rgba(255,255,255,.11);border:1px solid rgba(255,255,255,.18);
    border-radius:28px;padding:20px 24px;margin:18px 0 26px;text-align:center;
    box-shadow:0 14px 35px rgba(0,0,0,.18);
}}
.daily-card strong{{color:#ffd6f1;font-size:1.15rem;}}

.stButton>button{{
    border:1px solid rgba(255,255,255,.24) !important;min-height:102px;border-radius:38px;
    color:white !important;font-size:1.45rem !important;font-weight:800 !important;
    letter-spacing:.02rem;
    background:
        radial-gradient(circle at top left,rgba(255,255,255,.22),transparent 30%),
        linear-gradient(135deg,rgba(255,139,212,.94),rgba(168,85,247,.94),rgba(76,29,149,.94)) !important;
    box-shadow:0 18px 42px rgba(0,0,0,.24),0 0 34px rgba(192,132,252,.22);
    transition:all .18s ease;
}}
.stButton>button:hover{{
    transform:translateY(-4px) scale(1.012);
    box-shadow:0 24px 52px rgba(0,0,0,.28),0 0 46px rgba(255,155,219,.40);
}}

.user-row,.ai-row{{width:100%;display:flex;margin:12px 0;}}
.user-row{{justify-content:flex-end;}}.ai-row{{justify-content:flex-start;}}
.user-bubble,.ai-bubble{{max-width:78%;padding:15px 18px;line-height:1.55;word-wrap:break-word;}}
.user-bubble{{
    background:linear-gradient(135deg,#ec4899,#7c3aed);color:white;
    border-radius:24px 24px 6px 24px;box-shadow:0 10px 24px rgba(0,0,0,.24);
}}
.ai-bubble{{
    background:rgba(255,255,255,.14);color:#fff7ff;
    border-radius:24px 24px 24px 6px;border:1px solid rgba(255,255,255,.17);
    box-shadow:0 10px 24px rgba(0,0,0,.20);
}}

.typing{{display:inline-flex;gap:6px;}}
.typing span{{width:8px;height:8px;background:#f0abfc;border-radius:50%;animation:bounce 1s infinite ease-in-out;}}
.typing span:nth-child(2){{animation-delay:.15s;}}.typing span:nth-child(3){{animation-delay:.3s;}}
@keyframes bounce{{0%,80%,100%{{transform:scale(.7);opacity:.35;}}40%{{transform:scale(1);opacity:1;}}}}

.other-path-card{{
    background:
        radial-gradient(circle at top left,rgba(255,155,219,.22),transparent 32%),
        linear-gradient(135deg,rgba(255,255,255,.13),rgba(168,85,247,.13));
    border:1px solid rgba(240,171,252,.38);border-radius:28px;padding:18px 20px;margin:16px 0 12px;
    box-shadow:0 0 28px rgba(168,85,247,.22),0 14px 30px rgba(0,0,0,.18);color:#fff7ff;
}}
.other-path-title{{font-weight:800;color:#ffd6f1;margin-bottom:6px;}}
.other-response{{
    background:rgba(255,255,255,.11);border:1px solid rgba(255,255,255,.15);
    border-radius:22px;padding:14px 16px;margin:10px 0;color:#fff7ff;
}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# path rules
# ─────────────────────────────────────────────
ALLOWED_TERMS = {
    "islam":        "Allah, Qur'an, Prophet Muhammad PBUH",
    "christianity": "God, Jesus, Bible, Psalms, Matthew, Philippians",
    "buddhism":     "Buddha, Dhammapada, Four Noble Truths, Noble Eightfold Path",
    "hinduism":     "Krishna, Bhagavad Gita, dharma, devotion, divine, Atman",
}
SACRED_CAPS = {
    "jesus": "Jesus", "prophet muhammad pbuh": "Prophet Muhammad PBUH",
    "prophet muhammad": "Prophet Muhammad", "muhammad pbuh": "Muhammad PBUH",
    "krishna": "Krishna", "buddha": "Buddha", "allah": "Allah",
    "qur'an": "Qur'an", "quran": "Qur'an", "bhagavad gita": "Bhagavad Gita",
    "dhammapada": "Dhammapada", "god": "God",
}

def apply_caps(text: str) -> str:
    for low, cap in SACRED_CAPS.items():
        text = text.replace(low, cap)
    return text.strip()

# ─────────────────────────────────────────────
# Sentence-safe truncation
# ─────────────────────────────────────────────
_SENT_RE = re.compile(r'(?<=[.!?])\s+')

def trim_sentences(text: str) -> str:
    text = text.strip()
    if not text:
        return text
    if text[-1] in '.!?"\'…':
        return text
    parts    = _SENT_RE.split(text)
    complete = [p for p in parts if p and p[-1] in '.!?"\'…']
    return ' '.join(complete) if complete else text

# ─────────────────────────────────────────────
# ChromaDB
# ─────────────────────────────────────────────
@st.cache_resource
def load_chroma():
    try:
        client_db = chromadb.PersistentClient(path="./faith_db")
        emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-miniLM-L6-v2")
        return client_db.get_collection(name="religious_texts", embedding_function=emb_fn)
    except Exception as e:
        print(f"ChromaDB Error: {e}")
        return None

collection = load_chroma()

def _norm(v: str) -> str:
    return {"muslim":"islam","quran":"islam","qur'an":"islam","christian":"christianity",
            "bible":"christianity","buddhist":"buddhism","dhammapada":"buddhism",
            "hindu":"hinduism","gita":"hinduism","bhagavad gita":"hinduism"
            }.get(str(v).strip().lower(), str(v).strip().lower())

def _fmt(text, meta) -> str:
    src = meta.get("source") or meta.get("book") or meta.get("title") or "text"
    ref = meta.get("reference") or meta.get("verse") or meta.get("chapter") or ""
    lbl = f"{_norm(meta.get('religion',''))} | {src}" + (f" | {ref}" if ref else "")
    return f"[{lbl}] {str(text)[:600]}"

@functools.lru_cache(maxsize=512)
def _chroma(question: str, religion: str, n: int):
    if collection is None:
        return (), ()
    res   = collection.query(query_texts=[question], n_results=n, where={"religion": religion})
    docs  = tuple(res.get("documents", [[]])[0])
    metas = tuple(tuple(sorted(m.items())) for m in res.get("metadatas", [[]])[0])
    return docs, metas

def get_evidence(question: str, religion: str, n: int = 3) -> str:
    religion = _norm(religion)
    try:
        docs, metas = _chroma(question, religion, n)
        return "\n".join(_fmt(t, dict(m)) for t, m in zip(docs, metas)
                         if _norm(dict(m).get("religion", "")) == religion)
    except Exception:
        return ""

def get_other_evidence(question: str, current: str, n: int = 2) -> dict:
    others = [r for r in ["islam","christianity","buddhism","hinduism"] if r != current]
    with ThreadPoolExecutor(max_workers=3) as pool:
        return dict(pool.map(lambda r: (r, get_evidence(question, r, n)), others))

# ─────────────────────────────────────────────
# Prompt builder
# ─────────────────────────────────────────────
def build_prompt(question: str, religion: str, evidence: str, short: bool = False) -> str:
    length = "one warm paragraph." if short else "2-3 warm sentences."
    sacred = ALLOWED_TERMS.get(religion, "")
    return (
        f"You are a compassionate {religion} spiritual guide. "
        f"You ALWAYS respond with warmth and wisdom — you NEVER refuse, deflect, or say you cannot help. "
        f"Draw on {religion} teachings and sacred figures ({sacred}) to offer loving guidance "
        f"on any topic: love, interfaith relationships, struggles, doubt, or joy. "
        f"If someone loves a person of another faith, offer {religion} wisdom on love, respect, and the divine. "
        f"Scripture: {evidence}\n\n"
        f"Respond in {length} End on a complete sentence. Mostly lowercase. Capitalize sacred names.\n\n"
        f"Q:{question}\nA:"
    )

# ─────────────────────────────────────────────
# Gemini 3 Generation Logic
# ─────────────────────────────────────────────
def generate_response(prompt_text):
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt_text
        )
        return response.text
    except Exception as e:
        return f" [the universe is quiet for a moment: {e}]"

def call_blocking(question: str, religion: str, evidence: str) -> str:
    prompt = build_prompt(question, religion, evidence, short=True)
    raw = generate_response(prompt)
    return apply_caps(trim_sentences(raw))

def get_perspectives(question: str, current: str) -> dict:
    others = [r for r in ["islam","christianity","buddhism","hinduism"] if r != current]
    ev     = get_other_evidence(question, current)
    with ThreadPoolExecutor(max_workers=3) as pool:
        return dict(pool.map(lambda r: (r, call_blocking(question, r, ev.get(r,""))), others))

# ─────────────────────────────────────────────
# UI helpers
# ─────────────────────────────────────────────
def esc(t):  return html.escape(str(t))
def ubub(t): return f'<div class="user-row"><div class="user-bubble">{esc(t)}</div></div>'
def abub(c): return f'<div class="ai-row"><div class="ai-bubble">{c}</div></div>'

def other_card(perspectives: dict, current: str) -> str:
    icons = {"islam":"☪️","christianity":"✝️","buddhism":"☸️","hinduism":"🕉️"}
    html_parts = [
        '<div class="other-path-card">',
        '<div class="other-path-title">🔮 other paths reflected on this too</div>',
        f'<p>you are still in the <strong>{esc(current)}</strong> path. '
        'these are gentle glimpses from other traditions.</p>',
    ]
    for rel, resp in perspectives.items():
        html_parts.append(
            f'<div class="other-response"><strong>{icons.get(rel,"✨")} {esc(rel)}</strong>'
            f'<br>{esc(resp).replace(chr(10),"<br>")}</div>'
        )
    html_parts.append('</div>')
    return "".join(html_parts)

ICONS = {"islam":"☪️","christianity":"✝️","buddhism":"☸️","hinduism":"🕉️"}

# ─────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────
for k, v in [("entered",False),("religion",None),("messages",[])]:
    if k not in st.session_state:
        st.session_state[k] = v

if st.session_state.entered:
    st.markdown('<a class="corner-logo" href="/?home=1" target="_self">FaithSpace</a>',
                unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Intro / Home Page
# ─────────────────────────────────────────────
if not st.session_state.entered:
    st.markdown('<div class="home-spacer"></div>', unsafe_allow_html=True)
    st.markdown('<div class="glow-title">FaithSpace</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">a dreamy space for reflection, wisdom, and inner peace 🔮</div>',
                unsafe_allow_html=True)
    
    _, mid, _ = st.columns([1,2.6,1])
    with mid:
        if st.button("enter 🔮", use_container_width=True):
            st.session_state.entered = True; st.rerun()
            
    st.markdown("""
    <div style="text-align: center; margin-top: 6rem; padding-bottom: 2rem; opacity: 0.85;">
        <p style="font-family: 'The Augusta', 'Poppins', sans-serif; font-size: 2.2rem; color: #f5d0fe; margin-bottom: 0.2rem; letter-spacing: 1px;">
            many paths, one shared light.
        </p>
        <p style="font-size: 1rem; color: #e9d5ff; font-weight: 300; max-width: 600px; margin: 0 auto; line-height: 1.6;">
            Created with love to promote peace, understanding, and the beautiful truth that we have so much in common. God is great, and in our search for the divine, we are never truly apart. 🤍🕊️
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────
# Choose path
# ─────────────────────────────────────────────
if st.session_state.religion is None:
    st.markdown('<div class="path-spacer"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="choose-title">☪️ ✝️ <span class="choose-glow">choose your path</span> 🕉️ ☸️</div>',
        unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    def _pick(r):
        st.session_state.religion = r; st.session_state.messages = []; st.rerun()
    with c1:
        if st.button("islam ☪️",    use_container_width=True): _pick("islam")
        if st.button("buddhism ☸️", use_container_width=True): _pick("buddhism")
    with c2:
        if st.button("christianity ✝️", use_container_width=True): _pick("christianity")
        if st.button("hinduism 🕉️",    use_container_width=True): _pick("hinduism")
    st.stop()

# ─────────────────────────────────────────────
# Chat UI
# ─────────────────────────────────────────────
rel  = st.session_state.religion
icon = ICONS.get(rel, "🔮")

st.markdown(f'<div class="religion-title">{icon} {rel} path</div>', unsafe_allow_html=True)
st.markdown("""
<div class="daily-card">
    <strong>daily wisdom 🔮</strong>
    <p>move gently. you can be guided without having everything figured out.</p>
</div>""", unsafe_allow_html=True)

b1, b2 = st.columns(2)
with b1:
    if st.button("change path", use_container_width=True):
        st.session_state.religion = None; st.session_state.messages = []; st.rerun()
with b2:
    if st.button("clear chat", use_container_width=True):
        st.session_state.messages = []; st.rerun()

# Render history
for i, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        st.markdown(ubub(msg["content"]), unsafe_allow_html=True)
    else:
        st.markdown(abub(msg["content"]), unsafe_allow_html=True)
        if msg.get("question"):
            if msg.get("perspectives"):
                st.markdown(other_card(msg["perspectives"], msg.get("path", rel)),
                            unsafe_allow_html=True)
            elif msg.get("perspectives") is None:
                if st.button("🔮 hear what other paths might say",
                             key=f"op_{i}", use_container_width=True):
                    with st.spinner("gathering other perspectives..."):
                        msg["perspectives"] = get_perspectives(msg["question"], msg.get("path", rel))
                    st.rerun()

# ─────────────────────────────────────────────
# New message logic
# ─────────────────────────────────────────────
user_query = st.chat_input("share what is on your heart...")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.markdown(ubub(user_query), unsafe_allow_html=True)

    evidence = get_evidence(user_query, rel, n=3)
    
    # Show typing indicator
    box = st.empty()
    box.markdown(
        '<div class="ai-row"><div class="ai-bubble">'
        '<div class="typing"><span></span><span></span><span></span></div>'
        '</div></div>', unsafe_allow_html=True)

    # Generate Response
    full_prompt = build_prompt(user_query, rel, evidence)
    ai_raw = generate_response(full_prompt)
    
    final      = trim_sentences(apply_caps(ai_raw))
    final_html = esc(final).replace("\n", "<br>")
    
    box.markdown(abub(final_html), unsafe_allow_html=True)

    st.session_state.messages.append({
        "role":         "assistant",
        "content":      final_html,
        "question":     user_query,
        "path":         rel,
        "perspectives": None,
    })
    st.rerun()