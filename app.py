import os
import re
import time
import random
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Mind Mentor AI - Pratima's Study Companion",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# SESSION STATE & THEME INITIALIZATION
# =========================================================
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

if "meta" not in st.session_state:
    st.session_state.meta = {}

# =========================================================
# SYSTEM PROMPT (PRATIMA + WBCHSE CLASS 11 SCIENCE + BENGALI)
# =========================================================
SYSTEM_PROMPT = """তুমি "Mind Mentor AI", প্রতীমার (একাদশ শ্রেণির বিজ্ঞান বিভাগের ছাত্রী, WBCHSE) জন্য একজন অভিজাত AI টিউটর, একাডেমিক গাইড এবং সহানুভূতিশীল ব্যক্তিগত উপদেষ্টা।
তোমার লক্ষ্য হলো স্পষ্ট, সুসংগঠিত এবং গভীর অন্তর্দৃষ্টিপূর্ণ উত্তর প্রদান করা।

অত্যন্ত গুরুত্বপূর্ণ নিয়ম:
1. ভাষা: তোমার সমস্ত উত্তর অবশ্যই **বাংলায়** হতে হবে। তবে গাণিতিক প্রতীক, ইংরেজি পরিভাষা (যেমন Photosynthesis, Integration, Derivation ইত্যাদি যেখানে প্রয়োজন) এবং কোড ব্লক ইংরেজিতে থাকতে পারে।
2. পাঠ্যক্রম: তুমি পশ্চিমবঙ্গ উচ্চমাধ্যমিক শিক্ষা সংসদ (WBCHSE) এর একাদশ শ্রেণির বিজ্ঞান বিভাগের সিলেবাস (পদার্থবিদ্যা, রসায়ন, জীববিদ্যা, গণিত) খুব ভালোভাবে জানো।
3. গণিত ও সূত্র (MATH FORMATTING):
   - ইনলাইন গণিতের জন্য `$` ব্যবহার করো (যেমন $E=mc^2$)।
   - ব্লক সমীকরণের জন্য `$$` আলাদা লাইনে ব্যবহার করো।
   - কখনোই গণিতকে ব্র্যাকেট `( \int x dx )` বা `\[ \]` দিয়ে মুড়বে না।
4. টেবিল ও তালিকা:
   - ডেটা প্রদর্শনের জন্য মার্কডাউন টেবিল (`| ... |`) ব্যবহার করো।
   - বুলেট পয়েন্টের জন্য `-` বা `*` এবং সাব-হেডিঙের জন্য `###` ব্যবহার করো।
5. ব্যক্তিগত পরামর্শ: প্রতীমা যখন পড়াশোনার চাপ, ক্যারিয়ার বা ব্যক্তিগত কোনো সমস্যা নিয়ে কথা বলবে, তখন তুমি একজন বড় দাদা/দিদি বা বন্ধুর মতো সহানুভূতিশীল এবং উৎসাহব্যঞ্জক পরামর্শ দেবে।

পেডাগগি (শিক্ষাদান পদ্ধতি):
1. সোক্রেটিক পদ্ধতি: প্রতীমাকে প্রশ্ন করে উত্তরের দিকে নিয়ে যাও। "কেন" এবং "কীভাবে" ব্যাখ্যা করো।
2. বাস্তব উদাহরণ: কঠিন বিষয়গুলো বোঝাতে দৈনন্দিন জীবনের উদাহরণ দাও।
3. বোঝাপড়া যাচাই: একাডেমিক ব্যাখ্যার শেষে একটি ছোট প্রশ্ন করো যাতে প্রতীমা বুঝতে পারে সে বিষয়টি আয়ত্ত করেছে কিনা।
"""

if "messages" not in st.session_state:
    st.session_state.messages = [SystemMessage(content=SYSTEM_PROMPT)]
    st.session_state.meta[0] = {"time": datetime.now().strftime("%H:%M")}

# =========================================================
# DYNAMIC CSS (MODERN MINIMALIST AI UI)
# =========================================================
theme = st.session_state.theme

if theme == "Dark":
    css_vars = """
        --bg-base: #171717;
        --bg-sidebar: #171717;
        --bg-surface: #212121;
        --bg-hover: #2a2a2a;
        --bg-active: #323232;
        --bg-input: #212121;
        --text-primary: #ececec;
        --text-secondary: #b4b4b4;
        --text-tertiary: #737373;
        --border-subtle: #2e2e2e;
        --border-strong: #404040;
        --accent: #818cf8;
        --accent-hover: #6366f1;
        --accent-bg: rgba(129, 140, 248, 0.08);
        --user-bubble: #2a2a2a;
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    """
else:
    css_vars = """
        --bg-base: #ffffff;
        --bg-sidebar: #f9f9f9;
        --bg-surface: #ffffff;
        --bg-hover: #f4f4f5;
        --bg-active: #e4e4e7;
        --bg-input: #f4f4f5;
        --text-primary: #171717;
        --text-secondary: #525252;
        --text-tertiary: #a3a3a3;
        --border-subtle: #e4e4e7;
        --border-strong: #d4d4d8;
        --accent: #4f46e5;
        --accent-hover: #4338ca;
        --accent-bg: rgba(79, 70, 229, 0.05);
        --user-bubble: #f4f4f5;
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.05);
    """

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Hind+Siliguri:wght@300;400;500;600;700&display=swap');

:root {{
    {css_vars}
}}

* {{
    scroll-behavior: smooth;
    box-sizing: border-box;
}}

html, body, [class*="stApp"] {{
    font-family: 'Inter', 'Hind Siliguri', system-ui, sans-serif !important;
    background-color: var(--bg-base) !important;
    color: var(--text-primary) !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}}

/* Main Container - Centered and clean */
.block-container {{
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
    max-width: 800px !important; 
    margin: 0 auto;
}}

/* Hide Streamlit Chrome */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header[data-testid="stHeader"] {{ 
    background: transparent !important; 
    backdrop-filter: blur(8px);
}}

/* Typography */
.stMarkdown, .stMarkdown p, .stMarkdown li {{
    color: var(--text-primary) !important;
    line-height: 1.75;
    font-size: 1rem;
    font-weight: 400;
    font-family: 'Inter', 'Hind Siliguri', system-ui, sans-serif !important;
}}
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    margin-top: 1.5rem;
    letter-spacing: -0.02em;
}}
.stMarkdown h3 {{
    font-size: 1.1rem !important;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid var(--border-subtle);
}}
.stMarkdown strong {{ 
    color: var(--text-primary); 
    font-weight: 600; 
}}
.stCaption, [data-testid="stCaptionContainer"] {{
    color: var(--text-tertiary) !important;
    font-size: 0.85rem !important;
}}

/* =========================================
   SIDEBAR
   ========================================= */
section[data-testid="stSidebar"] {{
    background-color: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border-subtle);
}}
section[data-testid="stSidebar"] > div {{
    padding-top: 1.5rem;
    padding-right: 1.5rem;
    padding-left: 1.5rem;
}}

.brand-block {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0.5rem 0 1.5rem 0;
    border-bottom: 1px solid var(--border-subtle);
    margin-bottom: 1.5rem;
}}
.brand-icon {{
    width: 36px; height: 36px;
    border-radius: 8px;
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
}}
.brand-text h2 {{
    margin: 0; font-size: 1.1rem; font-weight: 600; color: var(--text-primary);
    letter-spacing: -0.02em;
}}
.brand-text span {{
    font-size: 0.75rem; color: var(--text-tertiary); font-weight: 500;
    letter-spacing: 0.02em;
}}

.section-label {{
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-tertiary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin: 1.5rem 0 0.6rem 0;
}}

.stat-pill {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 0.8rem;
    color: var(--text-secondary);
    font-weight: 500;
}}
.stat-dot {{
    width: 6px; height: 6px; border-radius: 50%;
    background: #10b981;
    box-shadow: 0 0 4px #10b981;
}}

/* Buttons */
.stButton > button, .stDownloadButton > button {{
    background-color: transparent !important;
    border: 1px solid var(--border-subtle) !important;
    color: var(--text-primary) !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 1rem !important;
    transition: all 0.15s ease !important;
    width: 100%;
    box-shadow: none !important;
    font-family: 'Inter', 'Hind Siliguri', system-ui, sans-serif !important;
}}
.stButton > button:hover, .stDownloadButton > button:hover {{
    background-color: var(--bg-hover) !important;
    border-color: var(--border-strong) !important;
    color: var(--text-primary) !important;
    transform: none !important;
    box-shadow: none !important;
}}
.stButton > button:active {{
    background-color: var(--bg-active) !important;
}}
.stButton > button p {{ text-align: left !important; }}

/* Clear chat button */
div[data-testid="stSidebar"] .stButton:last-of-type > button {{
    color: #ef4444 !important;
    border-color: rgba(239, 68, 68, 0.2) !important;
}}
div[data-testid="stSidebar"] .stButton:last-of-type > button:hover {{
    background-color: rgba(239, 68, 68, 0.08) !important;
    border-color: #ef4444 !important;
}}

/* Radio and Select boxes */
div[role="radiogroup"] {{
    gap: 8px;
}}
div[role="radiogroup"] label {{
    background: var(--bg-surface) !important;
    border: 1px solid var(--border-subtle) !important;
    padding: 6px 16px !important;
    border-radius: 8px !important;
    transition: all 0.15s ease !important;
    color: var(--text-secondary) !important;
}}
div[role="radiogroup"] label:hover {{
    background: var(--bg-hover) !important;
    border-color: var(--border-strong) !important;
}}
div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) {{
    background: var(--accent-bg) !important;
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}}

/* BaseUI Select (Accent color) */
div[data-baseweb="select"] > div {{
    background-color: var(--bg-surface) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
}}

/* Hero Header */
.hero-wrap {{
    text-align: center;
    padding: 3rem 0 2.5rem 0;
}}
.hero-badge {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: var(--accent-bg);
    color: var(--accent);
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    padding: 6px 14px;
    border-radius: 999px;
    margin-bottom: 1.2rem;
    border: 1px solid rgba(129, 140, 248, 0.2);
}}
.hero-title {{
    font-size: 2.2rem;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.03em;
    color: var(--text-primary);
}}
.hero-sub {{
    color: var(--text-secondary);
    font-size: 1.05rem;
    margin-top: 0.8rem;
    font-weight: 400;
    line-height: 1.6;
}}

/* Empty State */
.empty-state {{
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    margin-bottom: 1.5rem;
}}
.empty-state-icon {{
    font-size: 2rem;
    margin-bottom: 0.8rem;
    background: var(--bg-hover);
    width: 60px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    margin: 0 auto 1rem auto;
}}
.empty-state p {{
    color: var(--text-secondary);
    font-size: 0.95rem;
    max-width: 480px;
    margin: 0 auto;
    line-height: 1.7;
}}
.suggestion-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-top: 1.5rem;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}}
.suggestion-chip {{
    background: var(--bg-base);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 14px 16px;
    font-size: 0.88rem;
    color: var(--text-primary);
    text-align: left;
    font-weight: 500;
    transition: all 0.15s ease;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 10px;
}}
.suggestion-chip:hover {{
    border-color: var(--accent);
    background: var(--accent-bg);
}}

/* =========================================
   CHAT MESSAGES (MINIMALIST AI STYLE)
   ========================================= */
div[data-testid="stChatMessage"] {{
    background-color: transparent !important;
    border: none !important;
    padding: 1.25rem 0 !important;
    animation: fadeIn 0.3s ease;
}}
@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(4px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

/* Avatars */
div[data-testid="stChatMessageAvatarUser"] {{
    background: var(--accent) !important;
    color: white !important;
    box-shadow: none !important;
    border-radius: 6px !important; 
}}
div[data-testid="stChatMessageAvatarAssistant"] {{
    background: var(--bg-surface) !important;
    border: 1px solid var(--border-subtle) !important;
    box-shadow: none !important;
    border-radius: 6px !important;
}}

/* User message bubble */
div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) .stMarkdown {{
    background: var(--user-bubble);
    border-radius: 1.25rem; 
    padding: 1rem 1.25rem;
    display: inline-block;
    max-width: 100%;
}}

/* Assistant message typography */
div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) .stMarkdown {{
    padding: 0.25rem 0;
    color: var(--text-primary);
}}

.msg-timestamp {{
    font-size: 0.72rem;
    color: var(--text-tertiary);
    margin-top: 6px;
    font-weight: 500;
    letter-spacing: 0.02em;
}}

/* Code blocks */
.stMarkdown code {{
    background-color: var(--bg-surface) !important;
    color: var(--accent) !important;
    border: 1px solid var(--border-subtle);
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 0.88em;
    font-family: 'JetBrains Mono', monospace;
}}
.stMarkdown pre {{
    background-color: #0d0d0d !important; 
    border: 1px solid var(--border-subtle) !important;
    border-radius: 8px !important;
    box-shadow: none;
}}
.stMarkdown pre code {{
    border: none;
    padding: 0;
    color: #e2e8f0 !important;
    background: transparent !important;
}}

/* MathJax */
.MathJax {{
    color: var(--text-primary) !important;
    font-size: 1.05em !important;
}}

/* Tables */
.stMarkdown table {{
    width: 100%;
    border-collapse: collapse;
    margin: 1.5rem 0;
    font-size: 0.92rem;
    border: 1px solid var(--border-subtle);
    border-radius: 8px;
    overflow: hidden;
}}
.stMarkdown th {{
    background-color: var(--bg-surface);
    color: var(--text-primary);
    font-weight: 600;
    text-align: left;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-subtle);
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}}
.stMarkdown td {{
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-subtle);
    color: var(--text-primary);
    background-color: var(--bg-base);
}}
.stMarkdown tr:last-child td {{ border-bottom: none; }}
.stMarkdown tr:hover td {{ background-color: var(--bg-hover); }}

/* Blockquotes */
.stMarkdown blockquote {{
    border-left: 3px solid var(--accent);
    background: var(--bg-surface);
    padding: 0.8rem 1.2rem;
    border-radius: 0 8px 8px 0;
    color: var(--text-secondary) !important;
    margin: 1.2rem 0;
}}

/* =========================================
   CHAT INPUT (SLEEK PILL)
   ========================================= */
.stChatInput {{
    background: linear-gradient(to bottom, transparent, var(--bg-base) 30%) !important;
    padding-top: 40px !important;
    padding-bottom: 1rem !important;
}}
.stChatInput textarea {{
    background-color: var(--bg-input) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 24px !important; 
    padding: 14px 24px !important;
    font-size: 0.95rem !important;
    line-height: 1.5 !important;
    box-shadow: var(--shadow-sm) !important;
    transition: all 0.2s ease !important;
}}
.stChatInput textarea:focus {{
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px var(--accent-bg) !important;
    transform: none;
    background-color: var(--bg-input) !important;
}}
.stChatInput textarea::placeholder {{
    color: var(--text-tertiary) !important;
    font-weight: 400;
}}
.stChatInput button {{
    color: var(--accent) !important;
    background: var(--accent-bg) !important;
    border-radius: 50% !important;
    width: 36px !important;
    height: 36px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin-right: 8px !important;
    transition: all 0.15s ease !important;
}}
.stChatInput button:hover {{
    background: var(--accent) !important;
    color: white !important;
    transform: none;
}}

hr, [data-testid="stDivider"] {{
    border-color: var(--border-subtle) !important;
    margin: 1.5rem 0 !important;
}}

.stAlert {{
    border-radius: 8px !important;
    border: 1px solid var(--border-subtle) !important;
    background: var(--bg-surface) !important;
    box-shadow: none;
}}

.stSpinner > div {{
    text-align: left;
    color: var(--text-secondary) !important;
}}

/* Minimalist scrollbar */
::-webkit-scrollbar {{ width: 8px; height: 8px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: var(--border-strong); border-radius: 4px; }}
::-webkit-scrollbar-thumb:hover {{ background: var(--text-tertiary); }}
</style>
""", unsafe_allow_html=True)

# =========================================================
# MATH & MARKDOWN CLEANER
# =========================================================
def clean_and_format(text):
    if not isinstance(text, str):
        return text
    text = text.replace(r'\[', '$$').replace(r'\]', '$$')
    text = text.replace(r'\(', '$').replace(r'\)', '$')
    text = re.sub(
        r'\(\s*(\\(?:int|sum|prod|lim|frac|sqrt|alpha|beta|gamma|theta|pi|infty|leq|geq|neq|approx|times|div|cdot|text|mathbf|mathrm).*?)\s*\)',
        r'$\1$',
        text
    )
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text

# =========================================================
# AI SETUP
# =========================================================
load_dotenv()
api = os.getenv("MISTRAL_API_KEY")

if not api:
    st.error("🚫 **MISTRAL_API_KEY পাওয়া যায়নি।** অনুগ্রহ করে আপনার `.env` ফাইলে এটি যুক্ত করুন।")
    st.stop()

model = ChatMistralAI(model="mistral-small-latest", mistral_api_key=api)

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("""
    <div class="brand-block">
        <div class="brand-icon">🧠</div>
        <div class="brand-text">
            <h2>Mind Mentor AI</h2>
            <span>প্রতীমার স্টাডি পার্টনার</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    n_exchanges = sum(1 for m in st.session_state.messages if isinstance(m, HumanMessage))
    st.markdown(f"""
    <div class="stat-pill"><span class="stat-dot"></span> {n_exchanges}টি প্রশ্ন এই সেশনে</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">সেটিংস</div>', unsafe_allow_html=True)

    st.session_state.theme = st.radio(
        "থিম",
        ["Dark", "Light"],
        horizontal=True,
        index=0 if st.session_state.theme == "Dark" else 1,
        label_visibility="collapsed"
    )

    st.markdown('<div class="section-label">দ্রুত অ্যাকশন</div>', unsafe_allow_html=True)

    def _add_prompt(text):
        st.session_state.messages.append(HumanMessage(content=text))
        st.session_state.meta[len(st.session_state.messages) - 1] = {"time": datetime.now().strftime("%H:%M")}

    if st.button("💡 একটি ধারণা ব্যাখ্যা করো", use_container_width=True):
        _add_prompt("আমি একটি নতুন বিষয় সম্পর্কে জানতে চাই। আমাকে জিজ্ঞেস করো সেটি কী, এবং তারপর সহজ বাংলায় উপমা দিয়ে বোঝাও।")
        st.rerun()

    if st.button("🗓️ স্টাডি প্ল্যান তৈরি করো", use_container_width=True):
        _add_prompt("আমার জন্য একটি সুসংগঠিত পড়াশোনার রুটিন তৈরি করতে সাহায্য করো। আমি কী পড়ছি, আমার লক্ষ্য কী এবং আমার কাছে কতটা সময় আছে তা আমাকে জিজ্ঞেস করো।")
        st.rerun()

    if st.button("📐 গণিতের সমস্যা সমাধান করো", use_container_width=True):
        _add_prompt("আমার কাছে একটি গণিতের সমস্যা আছে। আমাকে সেটি দিতে বলো, এবং তারপর সঠিক ফরম্যাটিং ব্যবহার করে ধাপে ধাপে সমাধান করো।")
        st.rerun()

    if st.button("🎯 আমাকে কুইজ দাও", use_container_width=True):
        _add_prompt("আমার পছন্দের একটি বিষয়ে আমাকে কুইজ দাও। প্রথমে বিষয়টি জিজ্ঞেস করো, তারপর একবারে একটি করে প্রশ্ন করো এবং আমার উত্তর যাচাই করো।")
        st.rerun()

    st.markdown('<div class="section-label">নোটস এবং ম্যানেজমেন্ট</div>', unsafe_allow_html=True)

    if len(st.session_state.messages) > 1:
        notes = f"# Mind Mentor AI - প্রতীমার স্টাডি নোটস\n_রপ্তানি করা হয়েছে {datetime.now().strftime('%d %B, %Y %H:%M')}_\n\n---\n\n"
        for msg in st.session_state.messages:
            if isinstance(msg, HumanMessage):
                notes += f"### ❓ প্রশ্ন\n{msg.content}\n\n"
            elif isinstance(msg, AIMessage):
                notes += f"### 💡 উত্তর\n{msg.content}\n\n---\n\n"

        st.download_button(
            label="📥 নোটস ডাউনলোড করুন (.md)",
            data=notes,
            file_name=f"mindmentor_notes_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown",
            use_container_width=True
        )
    else:
        st.button("📥 নোটস ডাউনলোড করুন (.md)", disabled=True, use_container_width=True)

    if st.button("🗑️ চ্যাট ইতিহাস মুছে ফেলুন", use_container_width=True):
        st.session_state.messages = [SystemMessage(content=SYSTEM_PROMPT)]
        st.session_state.meta = {0: {"time": datetime.now().strftime("%H:%M")}}
        st.rerun()

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    st.caption("Powered by Mistral AI · Mind Mentor AI")

# =========================================================
# HERO HEADER
# =========================================================
st.markdown(
    """<div class="hero-wrap">
        <div class="hero-badge">🎓 একাদশ শ্রেণি · বিজ্ঞান বিভাগ (WBCHSE)</div>
        <h1 class="hero-title">স্বাগতম, প্রতীমা!</h1>
        <p class="hero-sub">WBCHSE সিলেবাস অনুযায়ী পদার্থবিদ্যা, রসায়ন, জীববিদ্যা ও গণিতের সম্পূর্ণ সমাধান, সহজ বাংলায়।<br>আমি Mind Mentor AI, তোমার ব্যক্তিগত স্টাডি গাইড।</p>
    </div>""",
    unsafe_allow_html=True
)

# =========================================================
# CHAT FEED
# =========================================================
has_conversation = any(not isinstance(m, SystemMessage) for m in st.session_state.messages)

if not has_conversation:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-icon">✨</div>
        <p><strong>চলো শুরু করি!</strong><br>তোমার একাদশ শ্রেণির বিজ্ঞান যাত্রার সঙ্গী হিসেবে আমি প্রস্তুত। পড়াশোনার যেকোনো সন্দেহ বা ব্যক্তিগত পরামর্শের জন্য আমাকে জিজ্ঞেস করতে পারো।</p>
        <div class="suggestion-grid">
            <div class="suggestion-chip">📊 সহজ বাংলায় গ্রেডিয়েন্ট ডিসেন্ট বোঝাও</div>
            <div class="suggestion-chip">📐 সমাধান করো: ∫x²e^x dx</div>
            <div class="suggestion-chip">🧬 মাইটোসিস ও মিয়োসিসের পার্থক্য কী?</div>
            <div class="suggestion-chip">💬 পরীক্ষার চাপে খুব দুশ্চিন্তা হচ্ছে</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

for idx, msg in enumerate(st.session_state.messages):
    if isinstance(msg, SystemMessage):
        continue
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    avatar = "👩🏻‍🎓" if role == "user" else "🧠"

    with st.chat_message(role, avatar=avatar):
        st.markdown(clean_and_format(msg.content))
        ts = st.session_state.meta.get(idx, {}).get("time")
        if ts:
            align = "right" if role == "user" else "left"
            st.markdown(f"<div class='msg-timestamp' style='text-align:{align};'>{ts}</div>", unsafe_allow_html=True)

# =========================================================
# CHAT INPUT
# =========================================================
if prompt := st.chat_input("পড়াশোনা বা ব্যক্তিগত যেকোনো প্রশ্ন বাংলায় জিজ্ঞেস করো..."):
    if not prompt.strip():
        st.warning("অনুগ্রহ করে একটি প্রশ্ন বা চিন্তা লিখুন।")
    else:
        st.session_state.messages.append(HumanMessage(content=prompt))
        user_idx = len(st.session_state.messages) - 1
        st.session_state.meta[user_idx] = {"time": datetime.now().strftime("%H:%M")}

        with st.chat_message("user", avatar="👩🏻‍🎓"):
            st.markdown(prompt)
            st.markdown(f"<div class='msg-timestamp' style='text-align:right;'>{st.session_state.meta[user_idx]['time']}</div>", unsafe_allow_html=True)

        with st.chat_message("assistant", avatar="🧠"):
            thinking_labels = [
                "চিন্তা করা হচ্ছে...",
                "উত্তর সাজানো হচ্ছে...",
                "যুক্তি বিশ্লেষণ করা হচ্ছে...",
            ]
            with st.spinner(random.choice(thinking_labels)):
                try:
                    result = model.invoke(st.session_state.messages)
                    response = clean_and_format(result.content)
                except Exception as e:
                    response = (
                        "⚠️ **মডেলের সাথে সংযোগ স্থাপনে কিছু সমস্যা হয়েছে।**\n\n"
                        f"```\n{str(e)}\n```\n\n"
                        "অনুগ্রহ করে আপনার `MISTRAL_API_KEY` এবং ইন্টারনেট সংযোগ পরীক্ষা করুন।"
                    )

            st.markdown(response)
            ai_idx = len(st.session_state.messages)
            ts_now = datetime.now().strftime("%H:%M")
            st.markdown(f"<div class='msg-timestamp' style='text-align:left;'>{ts_now}</div>", unsafe_allow_html=True)

        st.session_state.messages.append(AIMessage(content=response))
        st.session_state.meta[ai_idx] = {"time": ts_now}
