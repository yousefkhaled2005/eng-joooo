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
WHATSAPP_NUMBER_E164 = "201007097545"  # Egypt +20
WHATSAPP_URL = f"https://wa.me/{WHATSAPP_NUMBER_E164}"
FACEBOOK_URL = ""  # optional

# Icons (real)
LINKEDIN_ICON = "https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png"
DRIVE_ICON    = "https://upload.wikimedia.org/wikipedia/commons/d/da/Google_Drive_logo.png"
WHATSAPP_ICON = "https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg"
FACEBOOK_ICON = "https://upload.wikimedia.org/wikipedia/commons/5/51/Facebook_f_logo_%282019%29.svg"

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
    """Run async safely in Streamlit."""
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
    """
    index[lang]['Male'/'Female'][locale] = list of voices
    lang derived from locale prefix (ar, en, ...)
    """
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
    out = []
    for v in voices_list:
        if (
            s in (v.get("FriendlyName","") or "").lower()
            or s in (v.get("ShortName","") or "").lower()
            or s in (v.get("Locale","") or "").lower()
            or s in (v.get("Gender","") or "").lower()
        ):
            out.append(v)
    return out

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
# UI language toggle (RTL/LTR)
# =========================
ui_lang = st.sidebar.selectbox("🌐 Interface Language", ["العربية", "English"], index=0)
RTL = (ui_lang == "العربية")

def inject_css(rtl: bool):
    direction = "rtl" if rtl else "ltr"
    align = "right" if rtl else "left"

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
    radial-gradient(circle at 12% 12%, rgba(0,119,181,0.12), transparent 45%),
    radial-gradient(circle at 88% 20%, rgba(37,211,102,0.11), transparent 45%),
    radial-gradient(circle at 65% 88%, rgba(213,51,105,0.09), transparent 45%),
    linear-gradient(135deg, #f8fafc 0%, #eef3fb 100%);
}}

.hero {{
  background: linear-gradient(120deg, #0b1220, #13263a, #214b60);
  color: white;
  padding: 26px 18px;
  border-radius: 20px;
  box-shadow: 0 16px 40px rgba(0,0,0,0.18);
  margin-bottom: 14px;
  position: relative;
  overflow: hidden;
}}

.hero:before {{
  content: "";
  position: absolute;
  top: -40%;
  {("right" if rtl else "left")}: -30%;
  width: 360px;
  height: 360px;
  background: radial-gradient(circle, rgba(255,255,255,0.18), transparent 60%);
  transform: rotate(12deg);
}}

.hero h1 {{ margin: 0; font-weight: 900; font-size: 34px; }}
.hero p  {{ margin: 6px 0 0; opacity: 0.92; font-size: 15px; }}

.card {{
  background: rgba(255,255,255,0.78);
  border: 1px solid rgba(255,255,255,0.62);
  border-radius: 20px;
  box-shadow: 0 12px 32px rgba(15,32,39,0.10);
  backdrop-filter: blur(12px);
  padding: 14px;
}}

.kpi {{
  display:inline-block;
  padding: 7px 10px;
  border-radius: 999px;
  background: rgba(255,255,255,0.72);
  border: 1px solid rgba(0,0,0,0.06);
  font-size: 12px;
  margin: 0 6px 8px 0;
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
  width: 100%;
  padding: 12px 14px;
  border-radius: 16px;
  color: white !important;
  text-decoration: none;
  font-weight: 900;
  text-align: center;
  box-shadow: 0 12px 22px rgba(0,0,0,0.14);
  transition: transform .18s ease, opacity .18s ease;
}}
.social-btn:hover {{ transform: translateY(-2px); opacity: 0.96; }}

.social-btn img {{
  width: 20px;
  height: 20px;
  object-fit: contain;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,.25));
}}

.linkedin {{ background: linear-gradient(90deg, #0077b5, #0a66c2); }}
.drive    {{ background: linear-gradient(90deg, #1fa463, #0f9d58); }}
.whatsapp {{ background: linear-gradient(90deg, #25D366, #128C7E); }}
.facebook {{ background: linear-gradient(90deg, #1877F2, #0b5fcc); }}

.stButton > button {{
  background: linear-gradient(90deg, #d53369 0%, #daae51 100%);
  border: none;
  border-radius: 16px;
  color: white;
  font-weight: 900;
  height: 54px;
  width: 100%;
  box-shadow: 0 14px 24px rgba(213,51,105,0.18);
  transition: transform .18s ease, box-shadow .18s ease;
}}
.stButton > button:hover {{
  transform: translateY(-2px);
  box-shadow: 0 18px 30px rgba(213,51,105,0.22);
}}

.small-note {{
  opacity: 0.80;
  font-size: 13px;
}}

hr {{ border-top: 1px solid rgba(0,0,0,0.06); }}
</style>
""",
        unsafe_allow_html=True,
    )

inject_css(RTL)

# =========================
# Sidebar (Profile)
# =========================
with st.sidebar:
    st.markdown("## 👨‍💻 يوسف خالد" if RTL else "## 👨‍💻 Yousef Khaled")
    st.caption("AI & Automation Engineer | Web / Mobile / AI Solutions")

    st.markdown(
        """
<div class="card">
  <span class="kpi">AI</span>
  <span class="kpi">Web</span>
  <span class="kpi">Mobile</span>
  <span class="kpi">Automation</span>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("### 🚀 خدماتي:" if RTL else "### 🚀 Services:")
    st.markdown(
        """
- 🚀 تفعيل اشتراكات Gemini & ChatGPT Pro  
- 🤖 أتمتة المهام البشرية بالكامل  
- 🌐 بناء مواقع SaaS وحلول AI (Web/Mobile)  
""" if RTL else
        """
- 🚀 Guidance for Gemini & ChatGPT Pro subscription setup  
- 🤖 Full automation of manual workflows  
- 🌐 Build SaaS products & AI solutions (Web/Mobile)  
"""
    )

    st.markdown("---")
    st.markdown("### 🔗 روابط:" if RTL else "### 🔗 Links:")
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

    if FACEBOOK_URL.strip():
        st.markdown(
            f"""
<a class="social-btn facebook" href="{FACEBOOK_URL}" target="_blank">
  <img src="{FACEBOOK_ICON}" alt="Facebook"/> Facebook
</a>
""",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.caption("© 2026 جميع الحقوق محفوظة لصالح Eng. Yousef Khaled Gouda" if RTL else "© 2026 All rights reserved — Eng. Yousef Khaled Gouda")

# =========================
# Header
# =========================
st.markdown(
    f"""
<div class="hero">
  <h1>{"🎙️ منصة المهندس يوسف خالد جودة لتحويل الكتابة لصوت" if RTL else "🎙️ Eng. Yousef Khaled Gouda — Voice Studio"}</h1>
  <p>{"عربي/إنجليزي — ذكور/إناث — سرعات واضحة x0.5 إلى x2 + معاينة وتحميل" if RTL else "Arabic/English — Male/Female — Clear speeds x0.5 to x2 + Preview & Download"}</p>
</div>
""",
    unsafe_allow_html=True,
)

# =========================
# Load & index voices
# =========================
with st.spinner("جاري تحميل مكتبة الأصوات..." if RTL else "Loading voice library..."):
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
# Layout
# =========================
left, right = st.columns([2, 1], gap="large")

with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### ⚙️ الإعدادات" if RTL else "### ⚙️ Settings")

    # Search
    search = st.text_input("🔎 ابحث عن صوت (اسم/كود/Locale):" if RTL else "🔎 Search (name/code/locale):", value="")

    # Tabs per language
    tab_ar, tab_en = st.tabs(["🇸🇦 العربية" if RTL else "🇸🇦 Arabic", "🇺🇸 English"])
    selected_voice_shortname = None

    # ---------- Arabic ----------
    with tab_ar:
        ar_locales = locales_for(AR_LANG)
        if not ar_locales:
            st.warning("لا توجد أصوات عربية متاحة حالياً." if RTL else "No Arabic voices found.")
        else:
            default_ar = "ar-EG" if "ar-EG" in ar_locales else ar_locales[0]
            ar_locale = st.selectbox("🌍 Locale (Arabic):", ar_locales, index=ar_locales.index(default_ar))

            c_m, c_f = st.columns(2, gap="medium")

            with c_m:
                st.markdown("#### 👨 ذكور" if RTL else "#### 👨 Male")
                male_list = filter_voices(voices_for(AR_LANG, "Male", ar_locale), search)
                male_choice = st.selectbox(
                    "اختر صوت ذكر:" if RTL else "Select male voice:",
                    options=[voice_label(v) for v in male_list] if male_list else ["—"],
                    disabled=(not male_list),
                )

            with c_f:
                st.markdown("#### 👩 إناث" if RTL else "#### 👩 Female")
                female_list = filter_voices(voices_for(AR_LANG, "Female", ar_locale), search)
                female_choice = st.selectbox(
                    "اختر صوت أنثى:" if RTL else "Select female voice:",
                    options=[voice_label(v) for v in female_list] if female_list else ["—"],
                    disabled=(not female_list),
                )

            use_gender = st.radio(
                "استخدم:" if RTL else "Use:",
                options=["👨 ذكر" if RTL else "👨 Male", "👩 أنثى" if RTL else "👩 Female"],
                horizontal=True,
                index=0
            )

            if use_gender.startswith("👨") and male_list:
                selected_voice_shortname = male_list[[voice_label(v) for v in male_list].index(male_choice)]["ShortName"]
            elif use_gender.startswith("👩") and female_list:
                selected_voice_shortname = female_list[[voice_label(v) for v in female_list].index(female_choice)]["ShortName"]
            else:
                selected_voice_shortname = (male_list[0]["ShortName"] if male_list else (female_list[0]["ShortName"] if female_list else None))

    # ---------- English ----------
    with tab_en:
        en_locales = locales_for(EN_LANG)
        if not en_locales:
            st.warning("لا توجد أصوات إنجليزية متاحة حالياً." if RTL else "No English voices found.")
        else:
            default_en = "en-US" if "en-US" in en_locales else en_locales[0]
            en_locale = st.selectbox("🌍 Locale (English):", en_locales, index=en_locales.index(default_en))

            c_m, c_f = st.columns(2, gap="medium")

            with c_m:
                st.markdown("#### 👨 Male")
                male_list = filter_voices(voices_for(EN_LANG, "Male", en_locale), search)
                male_choice = st.selectbox(
                    "Select male voice:",
                    options=[voice_label(v) for v in male_list] if male_list else ["—"],
                    disabled=(not male_list),
                )

            with c_f:
                st.markdown("#### 👩 Female")
                female_list = filter_voices(voices_for(EN_LANG, "Female", en_locale), search)
                female_choice = st.selectbox(
                    "Select female voice:",
                    options=[voice_label(v) for v in female_list] if female_list else ["—"],
                    disabled=(not female_list),
                )

            use_gender = st.radio(
                "Use:",
                options=["👨 Male", "👩 Female"],
                horizontal=True,
                index=0
            )

            if use_gender.startswith("👨") and male_list:
                selected_voice_shortname = male_list[[voice_label(v) for v in male_list].index(male_choice)]["ShortName"]
            elif use_gender.startswith("👩") and female_list:
                selected_voice_shortname = female_list[[voice_label(v) for v in female_list].index(female_choice)]["ShortName"]
            else:
                selected_voice_shortname = (male_list[0]["ShortName"] if male_list else (female_list[0]["ShortName"] if female_list else None))

    st.markdown("---")

    # Speed
    st.markdown("### ⚡ السرعة (x)" if RTL else "### ⚡ Speed (x)")
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

    # Pitch
    st.markdown("### 🎚️ طبقة الصوت (Pitch)" if RTL else "### 🎚️ Pitch")
    pitch = st.slider("Pitch (Hz):", -50, 50, 0, step=5)

    st.markdown('</div>', unsafe_allow_html=True)

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📝 أدخل النص المراد تحويله" if RTL else "### 📝 Enter your text")
    text = st.text_area(
        label="",
        height=260,
        placeholder="اكتب ما تريد تحويله لصوت احترافي..." if RTL else "Type your text here...",
    )
    st.caption(("عدد الحروف: " if RTL else "Characters: ") + str(len(text)))
    generate = st.button("🚀 توليد الصوت + معاينة" if RTL else "🚀 Generate + Preview")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# Output
# =========================
if generate:
    if not text.strip():
        st.warning("⚠️ اكتب نص الأول." if RTL else "⚠️ Please type text first.")
    elif not selected_voice_shortname:
        st.error("⚠️ لا يوجد صوت متاح حالياً لهذا الاختيار." if RTL else "⚠️ No voice available for this selection.")
    else:
        st.markdown("---")
        with st.spinner("جاري توليد الصوت..." if RTL else "Generating audio..."):
            try:
                out_path = run_async(generate_audio(text, selected_voice_shortname, rate_str, pitch))
                st.success("✅ تم التوليد بنجاح!" if RTL else "✅ Generated successfully!")

                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown("### 🎧 معاينة" if RTL else "### 🎧 Preview")
                    st.audio(out_path, format="audio/mpeg")

                with c2:
                    st.markdown("### ⬇️ تحميل" if RTL else "### ⬇️ Download")
                    with open(out_path, "rb") as f:
                        st.download_button(
                            "تحميل MP3" if RTL else "Download MP3",
                            data=f,
                            file_name=f"Yousef_AI_Voice_{int(time.time())}.mp3",
                            mime="audio/mpeg",
                            use_container_width=True,
                        )

                # Preview link
                try:
                    data_url = make_data_audio_link(out_path)
                    st.markdown("### 🔗 رابط معاينة" if RTL else "### 🔗 Preview Link")
                    st.markdown(
                        f'<a href="{data_url}" target="_blank">👉 {"افتح المعاينة في تبويب جديد" if RTL else "Open preview in a new tab"}</a>',
                        unsafe_allow_html=True,
                    )
                    st.caption("لو النص طويل جدًا: استخدم زر التحميل." if RTL else "If audio is large, use download.")
                except Exception:
                    st.caption("تعذر إنشاء رابط معاينة مباشر." if RTL else "Could not create preview link.")

            except Exception as e:
                st.error(("حدث خطأ: " if RTL else "Error: ") + str(e))

st.markdown("---")
st.markdown(
    "<div class='small-note'>المنصة تعمل بتقنيات AI Web Mobile | متخصصون في الأتمتة الشاملة</div>"
    if RTL else
    "<div class='small-note'>Built for AI • Web • Mobile — Specialized in full automation</div>",
    unsafe_allow_html=True,
)
