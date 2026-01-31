import streamlit as st
import edge_tts
import asyncio
import tempfile
import base64
import time
from collections import defaultdict

# =========================
# Config (Links)
# =========================
LINKEDIN_URL = "https://www.linkedin.com/in/yousefkhaleda"
PORTFOLIO_DRIVE_URL = "https://drive.google.com/drive/folders/1F0ziAJ-vRuAd_3GngeyYltMK3iFdUERa?usp=drive_link"
WHATSAPP_NUMBER_E164 = "201007097545"  # Egypt +20
WHATSAPP_URL = f"https://wa.me/{WHATSAPP_NUMBER_E164}"
FACEBOOK_URL = ""  # optional

# =========================
# Page setup
# =========================
st.set_page_config(
    page_title="Eng. Yousef | Global AI Voice Studio",
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
        lang = locale.split("-")[0].lower()  # ar / en / ...
        index[lang][gender][locale].append(v)

    # sort each list
    for lang in index:
        for gender in index[lang]:
            for locale in index[lang][gender]:
                index[lang][gender][locale] = sorted(
                    index[lang][gender][locale],
                    key=lambda x: (x.get("FriendlyName") or "")
                )
    return index

def voice_label(v):
    # nice readable label
    return f"{v.get('FriendlyName','')}  •  {v.get('ShortName','')}"

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

# =========================
# Global UI language toggle
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
    radial-gradient(circle at 10% 10%, rgba(21,87,153,0.14), transparent 45%),
    radial-gradient(circle at 90% 20%, rgba(21,153,87,0.12), transparent 45%),
    radial-gradient(circle at 60% 90%, rgba(213,51,105,0.10), transparent 45%),
    linear-gradient(135deg, #f8fafc 0%, #eef3fb 100%);
}}

.hero {{
  background: linear-gradient(120deg, #0f2027, #203a43, #2c5364);
  color: white;
  padding: 24px 18px;
  border-radius: 18px;
  box-shadow: 0 14px 35px rgba(0,0,0,0.16);
  margin-bottom: 14px;
}}

.hero h1 {{ margin: 0; font-weight: 900; font-size: 34px; }}
.hero p  {{ margin: 6px 0 0; opacity: 0.92; font-size: 15px; }}

.card {{
  background: rgba(255,255,255,0.72);
  border: 1px solid rgba(255,255,255,0.60);
  border-radius: 18px;
  box-shadow: 0 10px 26px rgba(15,32,39,0.10);
  backdrop-filter: blur(10px);
  padding: 14px;
}}

.kpi {{
  display:inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(255,255,255,0.70);
  border: 1px solid rgba(0,0,0,0.06);
  font-size: 12px;
  margin: 0 6px 6px 0;
}}

.social-btn {{
  display:block;
  width: 100%;
  padding: 10px 12px;
  border-radius: 12px;
  color: white !important;
  text-decoration: none;
  font-weight: 800;
  text-align: center;
  margin: 8px 0;
  box-shadow: 0 10px 18px rgba(0,0,0,0.12);
  transition: transform .18s ease, opacity .18s ease;
}}
.social-btn:hover {{ transform: translateY(-2px); opacity: 0.95; }}

.linkedin {{ background: linear-gradient(90deg, #0077b5, #0a66c2); }}
.drive    {{ background: linear-gradient(90deg, #1fa463, #0f9d58); }}
.whatsapp {{ background: linear-gradient(90deg, #25D366, #128C7E); }}
.facebook {{ background: linear-gradient(90deg, #1877F2, #0b5fcc); }}

.stButton > button {{
  background: linear-gradient(90deg, #d53369 0%, #daae51 100%);
  border: none;
  border-radius: 14px;
  color: white;
  font-weight: 900;
  height: 52px;
  width: 100%;
  box-shadow: 0 12px 22px rgba(213,51,105,0.18);
  transition: transform .18s ease, box-shadow .18s ease;
}}
.stButton > button:hover {{
  transform: translateY(-2px);
  box-shadow: 0 16px 28px rgba(213,51,105,0.22);
}}

.small-note {{
  opacity: 0.78;
  font-size: 13px;
}}

hr {{ border-top: 1px solid rgba(0,0,0,0.06); }}
</style>
""",
        unsafe_allow_html=True,
    )

inject_css(RTL)

# =========================
# Sidebar (Profile & Links)
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
- 🤖 أتمتة المهام وتحويلها لأنظمة تعمل أوتوماتيك بالكامل
- 🌐 بناء مواقع وSaaS (Web Apps) + حلول AI
- 💎 مساعدة في إعداد الاشتراكات عبر القنوات الرسمية المتاحة
""" if RTL else
        """
- 🤖 Automate manual workflows into fully automated systems
- 🌐 Build modern websites & SaaS products + AI solutions
- 💎 Help with official subscription setup guidance
"""
    )

    st.markdown("---")
    st.markdown("### 🔗 روابط:" if RTL else "### 🔗 Links:")
    st.markdown(
        f"""
<a class="social-btn linkedin" href="{LINKEDIN_URL}" target="_blank">LinkedIn</a>
<a class="social-btn drive" href="{PORTFOLIO_DRIVE_URL}" target="_blank">Portfolio</a>
<a class="social-btn whatsapp" href="{WHATSAPP_URL}" target="_blank">WhatsApp</a>
""",
        unsafe_allow_html=True,
    )
    if FACEBOOK_URL.strip():
        st.markdown(
            f"""<a class="social-btn facebook" href="{FACEBOOK_URL}" target="_blank">Facebook</a>""",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.caption("© 2026 جميع الحقوق محفوظة لصالح Eng. Yousef Khaled" if RTL else "© 2026 All rights reserved — Eng. Yousef Khaled")

# =========================
# Header
# =========================
st.markdown(
    f"""
<div class="hero">
  <h1>{"🎙️ منصة المهندس يوسف خالد جودة لتحويل الكتابة لصوت" if RTL else "🎙️ Eng. Yousef Khaled Gouda Voice Studio"}</h1>
  <p>{"عربي/إنجليزي — ذكور/إناث — تحكم في السرعة بصيغة x0.5 إلى x2 + معاينة وتحميل" if RTL else "Arabic/English — Male/Female — Speed control x0.5 to x2 + Preview & Download"}</p>
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

# Arabic / English only (as requested)
AR_LANG = "ar"
EN_LANG = "en"

# Some voices may have different gender keys; we focus on Male/Female
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
    st.markdown("### ⚙️ الإعدادات" if RTL else "### ⚙️ Settings")

    # Tabs: Arabic / English
    t_ar, t_en = st.tabs(["🇸🇦 العربية" if RTL else "🇸🇦 Arabic", "🇺🇸 English"])

    selected_voice_shortname = None

    # Shared search
    search = st.text_input("🔎 ابحث عن صوت (اسم/ذكر/أنثى/كود):" if RTL else "🔎 Search voice (name/gender/code):", value="")

    # ---------- Arabic tab ----------
    with t_ar:
        ar_locales = locales_for(AR_LANG)
        if not ar_locales:
            st.warning("لا توجد أصوات عربية متاحة حالياً." if RTL else "No Arabic voices found.")
        else:
            default_ar = "ar-EG" if "ar-EG" in ar_locales else ar_locales[0]
            ar_locale = st.selectbox("🌍 الدولة/اللغة (Arabic Locale):", ar_locales, index=ar_locales.index(default_ar))

            male_col, female_col = st.columns(2, gap="medium")

            # Male section
            with male_col:
                st.markdown("#### 👨 ذكور" if RTL else "#### 👨 Male")
                ar_male = filter_voices(voices_for(AR_LANG, "Male", ar_locale), search)
                if not ar_male:
                    st.info("لا توجد نتائج للذكور بهذا البحث." if RTL else "No male results for this search.")
                    male_choice = None
                else:
                    male_labels = [voice_label(v) for v in ar_male]
                    male_choice = st.selectbox("اختر صوت ذكر:" if RTL else "Select a male voice:", male_labels)

            # Female section
            with female_col:
                st.markdown("#### 👩 إناث" if RTL else "#### 👩 Female")
                ar_female = filter_voices(voices_for(AR_LANG, "Female", ar_locale), search)
                if not ar_female:
                    st.info("لا توجد نتائج للإناث بهذا البحث." if RTL else "No female results for this search.")
                    female_choice = None
                else:
                    female_labels = [voice_label(v) for v in ar_female]
                    female_choice = st.selectbox("اختر صوت أنثى:" if RTL else "Select a female voice:", female_labels)

            use_gender = st.radio(
                "استخدم:" if RTL else "Use:",
                options=["👨 ذكر" if RTL else "👨 Male", "👩 أنثى" if RTL else "👩 Female"],
                horizontal=True,
                index=0
            )

            if (use_gender.startswith("👨") and male_choice) and ar_male:
                selected_voice_shortname = ar_male[[voice_label(v) for v in ar_male].index(male_choice)]["ShortName"]
            elif (use_gender.startswith("👩") and female_choice) and ar_female:
                selected_voice_shortname = ar_female[[voice_label(v) for v in ar_female].index(female_choice)]["ShortName"]
            else:
                # fallback if chosen list empty
                if ar_male:
                    selected_voice_shortname = ar_male[0]["ShortName"]
                elif ar_female:
                    selected_voice_shortname = ar_female[0]["ShortName"]

    # ---------- English tab ----------
    with t_en:
        en_locales = locales_for(EN_LANG)
        if not en_locales:
            st.warning("لا توجد أصوات إنجليزية متاحة حالياً." if RTL else "No English voices found.")
        else:
            default_en = "en-US" if "en-US" in en_locales else en_locales[0]
            en_locale = st.selectbox("🌍 Country/Locale (English):", en_locales, index=en_locales.index(default_en))

            male_col, female_col = st.columns(2, gap="medium")

            with male_col:
                st.markdown("#### 👨 Male")
                en_male = filter_voices(voices_for(EN_LANG, "Male", en_locale), search)
                if not en_male:
                    st.info("No male results for this search.")
                    male_choice = None
                else:
                    male_labels = [voice_label(v) for v in en_male]
                    male_choice = st.selectbox("Select a male voice:", male_labels)

            with female_col:
                st.markdown("#### 👩 Female")
                en_female = filter_voices(voices_for(EN_LANG, "Female", en_locale), search)
                if not en_female:
                    st.info("No female results for this search.")
                    female_choice = None
                else:
                    female_labels = [voice_label(v) for v in en_female]
                    female_choice = st.selectbox("Select a female voice:", female_labels)

            use_gender = st.radio(
                "Use:",
                options=["👨 Male", "👩 Female"],
                horizontal=True,
                index=0
            )

            if (use_gender.startswith("👨") and male_choice) and en_male:
                selected_voice_shortname = en_male[[voice_label(v) for v in en_male].index(male_choice)]["ShortName"]
            elif (use_gender.startswith("👩") and female_choice) and en_female:
                selected_voice_shortname = en_female[[voice_label(v) for v in en_female].index(female_choice)]["ShortName"]
            else:
                if en_male:
                    selected_voice_shortname = en_male[0]["ShortName"]
                elif en_female:
                    selected_voice_shortname = en_female[0]["ShortName"]

    st.markdown("---")
    st.markdown("### ⚡ السرعة" if RTL else "### ⚡ Speed")
    speed_map = {
        "x0.5 (Very Slow)" if not RTL else "x0.5 (بطيء جدًا)": "-50%",
        "x0.75 (Slow)" if not RTL else "x0.75 (بطيء)": "-25%",
        "x1.0 (Normal)" if not RTL else "x1.0 (طبيعي)": "+0%",
        "x1.25 (Fast)" if not RTL else "x1.25 (سريع)": "+25%",
        "x1.5 (Very Fast)" if not RTL else "x1.5 (سريع جدًا)": "+50%",
        "x2.0 (Max)" if not RTL else "x2.0 (أقصى سرعة)": "+100%",
    }
    speed_label = st.selectbox("اختر السرعة:" if RTL else "Choose speed:", options=list(speed_map.keys()), index=2)
    rate_str = speed_map[speed_label]
    st.caption(("✅ اختيارك: " if RTL else "✅ Selected: ") + f"**{speed_label}**")

    st.markdown("---")
    st.markdown("### 🎚️ طبقة الصوت (اختياري)" if RTL else "### 🎚️ Pitch (optional)")
    pitch = st.slider("Pitch (Hz):", -50, 50, 0, step=5)

    st.markdown('</div>', unsafe_allow_html=True)

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📝 أدخل النص" if RTL else "### 📝 Enter your text")
    text = st.text_area(
        label="",
        height=260,
        placeholder="اكتب ما تريد تحويله لصوت احترافي..." if RTL else "Type what you want to convert into a professional voice...",
    )
    st.caption(("عدد الحروف: " if RTL else "Characters: ") + str(len(text)))

    generate = st.button("🚀 توليد + معاينة" if RTL else "🚀 Generate + Preview")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# Output
# =========================
if generate:
    if not text.strip():
        st.warning("⚠️ اكتب نص الأول." if RTL else "⚠️ Please type some text first.")
    elif not selected_voice_shortname:
        st.error("اختيار الصوت غير متاح حالياً." if RTL else "Voice selection not available.")
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
                        f'<a class="clean-link" href="{data_url}" target="_blank">👉 {"افتح المعاينة في تبويب جديد" if RTL else "Open preview in a new tab"}</a>',
                        unsafe_allow_html=True,
                    )
                    st.caption("لو النص طويل جدًا: استخدم زر التحميل." if RTL else "If the audio is large, use the download button.")
                except Exception:
                    st.caption("تعذر إنشاء رابط معاينة مباشر." if RTL else "Could not create a preview link.")

            except Exception as e:
                st.error(("حدث خطأ: " if RTL else "Error: ") + str(e))

st.markdown("---")
st.markdown(
    "<div class='small-note'>المنصة تعمل بتقنيات AI Web Mobile | متخصصون في الأتمتة الشاملة</div>"
    if RTL else
    "<div class='small-note'>Built for AI • Web • Mobile — Specialized in full automation</div>",
    unsafe_allow_html=True,
)

