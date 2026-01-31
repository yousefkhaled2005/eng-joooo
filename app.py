import streamlit as st
import edge_tts
import asyncio
import tempfile
import base64
import time
from collections import defaultdict

# =========================
# Config (Your Links)
# =========================
LINKEDIN_URL = "https://www.linkedin.com/in/yousefkhaleda"
PORTFOLIO_DRIVE_URL = "https://drive.google.com/drive/folders/1F0ziAJ-vRuAd_3GngeyYltMK3iFdUERa?usp=drive_link"
WHATSAPP_NUMBER_E164 = "201007097545"
WHATSAPP_URL = f"https://wa.me/{WHATSAPP_NUMBER_E164}"
FACEBOOK_URL = ""  # optional

# Icons
LINKEDIN_ICON = "https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png"
DRIVE_ICON    = "https://upload.wikimedia.org/wikipedia/commons/d/da/Google_Drive_logo.png"
WHATSAPP_ICON = "https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg"

# Lottie animations (public JSON)
LOTTIE_HERO = "https://assets10.lottiefiles.com/packages/lf20_yr6zz3wv.json"   # AI/tech
LOTTIE_LOAD = "https://assets10.lottiefiles.com/packages/lf20_usmfx6bp.json"   # loading

# =========================
# Page setup
# =========================
st.set_page_config(
    page_title="منصة المهندس يوسف خالد جودة لتحويل الكتابة لصوت",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# Helpers
# =========================
def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            return new_loop.run_until_complete(coro)
        return loop.run_until_complete(coro)
    except RuntimeError:
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        return new_loop.run_until_complete(coro)

@st.cache_data(ttl=60 * 60, show_spinner=False)
def fetch_voices_cached():
    async def _fetch():
        return await edge_tts.list_voices()
    voices = run_async(_fetch())
    cleaned = []
    for v in voices:
        cleaned.append({
            "ShortName": v.get("ShortName"),
            "Locale": v.get("Locale"),
            "Gender": v.get("Gender"),
            "FriendlyName": v.get("FriendlyName") or v.get("Name") or v.get("ShortName"),
        })
    return cleaned

def build_voice_index(voices):
    index = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for v in voices:
        locale = v.get("Locale") or ""
        short = v.get("ShortName")
        gender = v.get("Gender") or "Unknown"
        if not locale or not short:
            continue
        lang = locale.split("-")[0].lower()
        index[lang][gender][locale].append(v)

    for lang in index:
        for gender in index[lang]:
            for locale in index[lang][gender]:
                index[lang][gender][locale] = sorted(
                    index[lang][gender][locale],
                    key=lambda x: (x.get("FriendlyName") or "")
                )
    return index

def filter_voices(voices_list, s: str):
    if not s:
        return voices_list
    s = s.lower().strip()
    return [
        v for v in voices_list
        if (
            s in (v.get("FriendlyName","") or "").lower()
            or s in (v.get("ShortName","") or "").lower()
            or s in (v.get("Locale","") or "").lower()
            or s in (v.get("Gender","") or "").lower()
        )
    ]

def voice_label(v):
    return f"{v.get('FriendlyName','')}  •  {v.get('ShortName','')}"

def make_data_audio_link(mp3_path: str) -> str:
    with open(mp3_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:audio/mpeg;base64,{b64}"

async def generate_audio(text: str, voice_shortname: str, rate_str: str, pitch_hz: int):
    pitch_str = f"{pitch_hz:+d}Hz"
    communicate = edge_tts.Communicate(text, voice_shortname, rate=rate_str, pitch=pitch_str)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        await communicate.save(tmp.name)
        return tmp.name

# =========================
# UI language (RTL/LTR)
# =========================
ui_lang = st.sidebar.selectbox("🌐 Interface Language", ["العربية", "English"], index=0)
RTL = (ui_lang == "العربية")
direction = "rtl" if RTL else "ltr"
align = "right" if RTL else "left"

# =========================
# Ultra Global CSS + Animations
# =========================
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&display=swap');

html, body, [class*="css"] {{
  font-family: 'Tajawal', sans-serif;
  direction: {direction};
  text-align: {align};
}}

.stApp {{
  background:
    radial-gradient(circle at 12% 12%, rgba(0,119,181,0.13), transparent 45%),
    radial-gradient(circle at 88% 20%, rgba(37,211,102,0.12), transparent 45%),
    radial-gradient(circle at 65% 88%, rgba(213,51,105,0.10), transparent 45%),
    linear-gradient(135deg, #f7fbff 0%, #edf3ff 100%);
}}

:root {{
  --glass: rgba(255,255,255,0.78);
  --glass-border: rgba(255,255,255,0.62);
  --shadow: 0 14px 40px rgba(0,0,0,0.10);
}}

.hero {{
  background: linear-gradient(120deg, #0b1220, #122a3d, #214b60);
  color: #fff;
  padding: 26px 18px;
  border-radius: 22px;
  box-shadow: 0 18px 50px rgba(0,0,0,0.20);
  margin-bottom: 16px;
  overflow: hidden;
  position: relative;
  animation: fadeUp 700ms ease both;
}}

.hero:before {{
  content:"";
  position:absolute;
  top:-45%;
  {("right" if RTL else "left")}:-25%;
  width:420px;
  height:420px;
  background: radial-gradient(circle, rgba(255,255,255,0.18), transparent 60%);
  transform: rotate(18deg);
}}

.hero h1 {{
  margin:0;
  font-weight: 900;
  font-size: 34px;
  letter-spacing: .2px;
}}
.hero p {{
  margin:7px 0 0;
  opacity:.92;
  font-size: 15px;
}}

.grid-kpi {{
  display:flex;
  gap:10px;
  flex-wrap:wrap;
  margin-top: 10px;
}}
.kpi {{
  padding: 7px 12px;
  border-radius: 999px;
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.18);
  backdrop-filter: blur(8px);
  font-weight: 800;
  font-size: 12px;
}}

.card {{
  background: var(--glass);
  border: 1px solid var(--glass-border);
  border-radius: 22px;
  box-shadow: var(--shadow);
  backdrop-filter: blur(12px);
  padding: 14px;
  animation: fadeUp 700ms ease both;
}}

.section-title {{
  font-weight: 900;
  font-size: 16px;
  margin: 0 0 8px;
}}

.social-row {{
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
}}

.social-btn {{
  display:flex;
  align-items:center;
  justify-content:center;
  gap:10px;
  width:100%;
  padding: 12px 14px;
  border-radius: 16px;
  color:white !important;
  text-decoration:none;
  font-weight: 900;
  box-shadow: 0 14px 24px rgba(0,0,0,0.14);
  transition: transform .18s ease, filter .18s ease;
}}
.social-btn:hover {{
  transform: translateY(-3px) scale(1.01);
  filter: brightness(1.02);
}}
.social-btn img {{
  width: 20px;
  height: 20px;
  object-fit: contain;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,.25));
}}

.linkedin {{ background: linear-gradient(90deg, #0077b5, #0a66c2); }}
.drive    {{ background: linear-gradient(90deg, #1fa463, #0f9d58); }}
.whatsapp {{ background: linear-gradient(90deg, #25D366, #128C7E); }}

.stButton > button {{
  background: linear-gradient(90deg, #d53369 0%, #daae51 100%);
  border: none;
  border-radius: 16px;
  color: white;
  font-weight: 900;
  height: 54px;
  width: 100%;
  box-shadow: 0 16px 28px rgba(213,51,105,0.18);
  transition: transform .18s ease, box-shadow .18s ease;
}}
.stButton > button:hover {{
  transform: translateY(-2px);
  box-shadow: 0 20px 34px rgba(213,51,105,0.22);
}}

.small-note {{
  opacity: .82;
  font-size: 13px;
}}

@keyframes fadeUp {{
  from {{ opacity:0; transform: translateY(12px); }}
  to   {{ opacity:1; transform: translateY(0px); }}
}}

.floating-wa {{
  position: fixed;
  bottom: 18px;
  {("left" if RTL else "right")}: 18px;
  z-index: 9999;
}}
.floating-wa a {{
  display:flex;
  align-items:center;
  gap:10px;
  padding: 12px 16px;
  border-radius: 999px;
  background: linear-gradient(90deg, #25D366, #128C7E);
  color:white !important;
  text-decoration:none;
  font-weight: 900;
  box-shadow: 0 18px 36px rgba(0,0,0,.20);
  transition: transform .18s ease;
}}
.floating-wa a:hover {{
  transform: translateY(-2px) scale(1.02);
}}
.floating-wa img {{
  width: 20px;
  height: 20px;
}}

.lottie-wrap {{
  width: 100%;
  height: 180px;
  border-radius: 18px;
  overflow: hidden;
  background: rgba(255,255,255,0.40);
  border: 1px solid rgba(255,255,255,0.55);
}}
</style>
""",
    unsafe_allow_html=True,
)

# Floating WhatsApp Button
st.markdown(
    f"""
<div class="floating-wa">
  <a href="{WHATSAPP_URL}" target="_blank">
    <img src="{WHATSAPP_ICON}" alt="WhatsApp"/>
    {"تواصل واتساب" if RTL else "Chat on WhatsApp"}
  </a>
</div>
""",
    unsafe_allow_html=True,
)

# =========================
# Sidebar
# =========================
with st.sidebar:
    st.markdown("## 👨‍💻 يوسف خالد" if RTL else "## 👨‍💻 Yousef Khaled")
    st.caption("AI & Automation Engineer | Web / Mobile / AI Solutions")

    st.markdown("---")
    st.markdown("### 🔗 Links")
    st.markdown(
        f"""
<div class="social-row">
  <a class="social-btn linkedin" href="{LINKEDIN_URL}" target="_blank">
    <img src="{LINKEDIN_ICON}" alt="LinkedIn"/> LinkedIn
  </a>
  <a class="social-btn drive" href="{PORTFOLIO_DRIVE_URL}" target="_blank">
    <img src="{DRIVE_ICON}" alt="Portfolio"/> Portfolio
  </a>
  <a class="social-btn whatsapp" href="{WHATSAPP_URL}" target="_blank">
    <img src="{WHATSAPP_ICON}" alt="WhatsApp"/> WhatsApp
  </a>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("### 🚀 " + ("خدماتي" if RTL else "Services"))
    st.markdown(
        """
- 🚀 تفعيل اشتراكات Gemini & ChatGPT Pro  
- 🤖 أتمتة المهام البشرية بالكامل  
- 🌐 بناء مواقع SaaS وحلول AI (Web/Mobile)  
""" if RTL else
        """
- 🚀 Guidance for subscription setup  
- 🤖 Full automation of manual workflows  
- 🌐 Build SaaS & AI solutions (Web/Mobile)  
"""
    )

    st.markdown("---")
    st.caption("© 2026 Eng. Yousef Khaled Gouda — All Rights Reserved")

# =========================
# Hero
# =========================
st.markdown(
    f"""
<div class="hero">
  <h1>{"🎙️ منصة المهندس يوسف خالد جودة لتحويل الكتابة لصوت" if RTL else "🎙️ Eng. Yousef Khaled Gouda — AI Voice Studio"}</h1>
  <p>{"عربي/إنجليزي — ذكور/إناث — سرعات x0.5 إلى x2 + معاينة وتحميل + رابط معاينة" if RTL else "Arabic/English — Male/Female — Speed x0.5 to x2 + Preview & Download + Share link"}</p>
  <div class="grid-kpi">
    <span class="kpi">AI</span>
    <span class="kpi">Premium UI</span>
    <span class="kpi">Multi-Voice</span>
    <span class="kpi">Speed x2</span>
    <span class="kpi">Pitch</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# Lottie hero animation (embedded)
st.markdown(
    f"""
<div class="lottie-wrap">
  <lottie-player src="{LOTTIE_HERO}" background="transparent" speed="1" style="width: 100%; height: 180px;" loop autoplay></lottie-player>
</div>
<script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>
""",
    unsafe_allow_html=True,
)

# =========================
# Load voices
# =========================
with st.spinner("جاري تحميل مكتبة الأصوات..." if RTL else "Loading voices..."):
    voices = fetch_voices_cached()
voice_index = build_voice_index(voices)

AR_LANG = "ar"
EN_LANG = "en"

def locales_for(lang_key: str):
    locales = set()
    for g in ["Male", "Female"]:
        locales.update(voice_index.get(lang_key, {}).get(g, {}).keys())
    return sorted(list(locales))

def voices_for(lang_key: str, gender: str, locale: str):
    return voice_index.get(lang_key, {}).get(gender, {}).get(locale, [])

# =========================
# Main layout
# =========================
left, right = st.columns([2, 1], gap="large")

with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f"<div class='section-title'>{'⚙️ الإعدادات' if RTL else '⚙️ Settings'}</div>", unsafe_allow_html=True)

    search = st.text_input("🔎 ابحث عن صوت (اسم/كود/Locale):" if RTL else "🔎 Search voice (name/code/locale):", value="")

    tab_ar, tab_en = st.tabs(["🇸🇦 العربية" if RTL else "🇸🇦 Arabic", "🇺🇸 English"])
    selected_voice_shortname = None

    # ---------- Arabic tab ----------
    with tab_ar:
        ar_locales = locales_for(AR_LANG)
        if not ar_locales:
            st.warning("لا توجد أصوات عربية." if RTL else "No Arabic voices.")
        else:
            default_ar = "ar-EG" if "ar-EG" in ar_locales else ar_locales[0]
            ar_locale = st.selectbox("🌍 Locale (Arabic):", ar_locales, index=ar_locales.index(default_ar))

            mcol, fcol = st.columns(2, gap="medium")

            with mcol:
                st.markdown("#### 👨 ذكور" if RTL else "#### 👨 Male")
                mlist = filter_voices(voices_for(AR_LANG, "Male", ar_locale), search)
                mchoice = st.selectbox("صوت ذكر:" if RTL else "Male voice:", [voice_label(v) for v in mlist] if mlist else ["—"], disabled=(not mlist))

            with fcol:
                st.markdown("#### 👩 إناث" if RTL else "#### 👩 Female")
                flist = filter_voices(voices_for(AR_LANG, "Female", ar_locale), search)
                fchoice = st.selectbox("صوت أنثى:" if RTL else "Female voice:", [voice_label(v) for v in flist] if flist else ["—"], disabled=(not flist))

            use_gender = st.radio("استخدم:" if RTL else "Use:", ["👨 ذكر" if RTL else "👨 Male", "👩 أنثى" if RTL else "👩 Female"], horizontal=True, index=0)

            if use_gender.startswith("👨") and mlist:
                selected_voice_shortname = mlist[[voice_label(v) for v in mlist].index(mchoice)]["ShortName"]
            elif use_gender.startswith("👩") and flist:
                selected_voice_shortname = flist[[voice_label(v) for v in flist].index(fchoice)]["ShortName"]
            else:
                selected_voice_shortname = (mlist[0]["ShortName"] if mlist else (flist[0]["ShortName"] if flist else None))

    # ---------- English tab ----------
    with tab_en:
        en_locales = locales_for(EN_LANG)
        if not en_locales:
            st.warning("No English voices.")
        else:
            default_en = "en-US" if "en-US" in en_locales else en_locales[0]
            en_locale = st.selectbox("🌍 Locale (English):", en_locales, index=en_locales.index(default_en))

            mcol, fcol = st.columns(2, gap="medium")

            with mcol:
                st.markdown("#### 👨 Male")
                mlist = filter_voices(voices_for(EN_LANG, "Male", en_locale), search)
                mchoice = st.selectbox("Male voice:", [voice_label(v) for v in mlist] if mlist else ["—"], disabled=(not mlist))

            with fcol:
                st.markdown("#### 👩 Female")
                flist = filter_voices(voices_for(EN_LANG, "Female", en_locale), search)
                fchoice = st.selectbox("Female voice:", [voice_label(v) for v in flist] if flist else ["—"], disabled=(not flist))

            use_gender = st.radio("Use:", ["👨 Male", "👩 Female"], horizontal=True, index=0)

            if use_gender.startswith("👨") and mlist:
                selected_voice_shortname = mlist[[voice_label(v) for v in mlist].index(mchoice)]["ShortName"]
            elif use_gender.startswith("👩") and flist:
                selected_voice_shortname = flist[[voice_label(v) for v in flist].index(fchoice)]["ShortName"]
            else:
                selected_voice_shortname = (mlist[0]["ShortName"] if mlist else (flist[0]["ShortName"] if flist else None))

    st.markdown("---")

    st.markdown("### ⚡ " + ("السرعة (x)" if RTL else "Speed (x)"))
    speed_map = {
        ("x0.5 (بطيء جدًا)" if RTL else "x0.5 (Very Slow)"): "-50%",
        ("x0.75 (بطيء)" if RTL else "x0.75 (Slow)"): "-25%",
        ("x1.0 (طبيعي)" if RTL else "x1.0 (Normal)"): "+0%",
        ("x1.25 (سريع)" if RTL else "x1.25 (Fast)"): "+25%",
        ("x1.5 (سريع جدًا)" if RTL else "x1.5 (Very Fast)"): "+50%",
        ("x2.0 (أقصى سرعة)" if RTL else "x2.0 (Max)"): "+100%",
    }
    speed_label = st.selectbox("اختر السرعة:" if RTL else "Choose speed:", options=list(speed_map.keys()), index=2)
    rate_str = speed_map[speed_label]
    st.caption(("✅ اختيارك: " if RTL else "✅ Selected: ") + f"**{speed_label}**")

    st.markdown("### 🎚️ " + ("طبقة الصوت" if RTL else "Pitch"))
    pitch = st.slider("Pitch (Hz):", -50, 50, 0, step=5)

    st.markdown("</div>", unsafe_allow_html=True)

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f"<div class='section-title'>{'📝 أدخل النص' if RTL else '📝 Enter Text'}</div>", unsafe_allow_html=True)

    text = st.text_area(
        label="",
        height=260,
        placeholder="اكتب ما تريد تحويله لصوت احترافي..." if RTL else "Type what you want to convert into a realistic voice...",
    )
    st.caption(("عدد الحروف: " if RTL else "Characters: ") + str(len(text)))

    generate = st.button("🚀 توليد + معاينة" if RTL else "🚀 Generate + Preview")
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# Output
# =========================
if generate:
    if not text.strip():
        st.warning("⚠️ اكتب نص الأول." if RTL else "⚠️ Please type text first.")
    elif not selected_voice_shortname:
        st.error("⚠️ لا يوجد صوت متاح لهذا الاختيار." if RTL else "⚠️ No voice available for this selection.")
    else:
        st.markdown("---")
        with st.spinner("جاري توليد الصوت..." if RTL else "Generating audio..."):
            try:
                out_path = run_async(generate_audio(text, selected_voice_shortname, rate_str, pitch))

                st.success("✅ تم التوليد بنجاح!" if RTL else "✅ Generated successfully!")

                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown("### 🎧 " + ("معاينة" if RTL else "Preview"))
                    st.audio(out_path, format="audio/mpeg")

                with c2:
                    st.markdown("### ⬇️ " + ("تحميل" if RTL else "Download"))
                    with open(out_path, "rb") as f:
                        st.download_button(
                            "تحميل MP3" if RTL else "Download MP3",
                            data=f,
                            file_name=f"Yousef_AI_Voice_{int(time.time())}.mp3",
                            mime="audio/mpeg",
                            use_container_width=True,
                        )

                # Share / preview link
                try:
                    data_url = make_data_audio_link(out_path)
                    st.markdown("### 🔗 " + ("رابط معاينة" if RTL else "Preview Link"))
                    st.markdown(
                        f'<a href="{data_url}" target="_blank">👉 {"افتح المعاينة في تبويب جديد" if RTL else "Open preview in a new tab"}</a>',
                        unsafe_allow_html=True,
                    )
                    st.caption("لو النص طويل جدًا: استخدم زر التحميل." if RTL else "If audio is large, use download.")
                except Exception:
                    st.caption("تعذر إنشاء رابط معاينة." if RTL else "Could not create preview link.")

            except Exception as e:
                st.error(("حدث خطأ: " if RTL else "Error: ") + str(e))

st.markdown("---")
st.markdown(
    "<div class='small-note'>المنصة تعمل بتقنيات AI Web Mobile | متخصصون في الأتمتة الشاملة</div>"
    if RTL else
    "<div class='small-note'>Built for AI • Web • Mobile — Specialized in full automation</div>",
    unsafe_allow_html=True,
)
