import streamlit as st
import edge_tts
import asyncio
import tempfile
import os
import base64
import time
from collections import defaultdict

# =========================
# Config (Edit your links)
# =========================
LINKEDIN_URL = "https://www.linkedin.com/in/yousefkhaleda"
PORTFOLIO_DRIVE_URL = "https://drive.google.com/drive/folders/1F0ziAJ-vRuAd_3GngeyYltMK3iFdUERa?usp=drive_link"
WHATSAPP_NUMBER_E164 = "201007097545"  # Egypt +20
WHATSAPP_URL = f"https://wa.me/{WHATSAPP_NUMBER_E164}"

# لو عندك فيسبوك حطّه هنا (ولو مش عايز، سيبه فاضي)
FACEBOOK_URL = ""

# =========================
# Page setup
# =========================
st.set_page_config(
    page_title="Eng. Yousef | AI Voice Studio",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# Fancy UI CSS
# =========================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Tajawal', sans-serif;
    direction: rtl;
    text-align: right;
}

.stApp {
    background:
      radial-gradient(circle at 10% 10%, rgba(21,87,153,0.18), transparent 45%),
      radial-gradient(circle at 90% 20%, rgba(21,153,87,0.16), transparent 45%),
      radial-gradient(circle at 60% 90%, rgba(213,51,105,0.12), transparent 45%),
      linear-gradient(135deg, #f7f9fc 0%, #eef3fb 100%);
}

.hero {
    background: linear-gradient(120deg, #0f2027, #203a43, #2c5364);
    color: white;
    padding: 26px 18px;
    border-radius: 18px;
    box-shadow: 0 12px 35px rgba(0,0,0,0.18);
    margin-bottom: 18px;
}

.hero h1 { margin: 0; font-weight: 900; font-size: 34px; }
.hero p  { margin: 6px 0 0; opacity: 0.9; }

.glass {
    background: rgba(255,255,255,0.65);
    border: 1px solid rgba(255,255,255,0.55);
    border-radius: 18px;
    box-shadow: 0 10px 30px rgba(15,32,39,0.10);
    backdrop-filter: blur(10px);
    padding: 14px;
}

.badge {
    display:inline-block;
    padding: 6px 10px;
    border-radius: 999px;
    background: rgba(255,255,255,0.75);
    border: 1px solid rgba(0,0,0,0.06);
    font-size: 13px;
    margin-left: 6px;
}

a.clean-link { text-decoration: none; }

.social-btn {
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
}
.social-btn:hover { transform: translateY(-2px); opacity: 0.95; }
.linkedin { background: linear-gradient(90deg, #0077b5, #0a66c2); }
.drive    { background: linear-gradient(90deg, #1fa463, #0f9d58); }
.whatsapp { background: linear-gradient(90deg, #25D366, #128C7E); }
.facebook { background: linear-gradient(90deg, #1877F2, #0b5fcc); }

.stButton > button {
    background: linear-gradient(90deg, #d53369 0%, #daae51 100%);
    border: none;
    border-radius: 14px;
    color: white;
    font-weight: 900;
    height: 52px;
    width: 100%;
    box-shadow: 0 12px 22px rgba(213,51,105,0.20);
    transition: transform .18s ease, box-shadow .18s ease;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 16px 28px rgba(213,51,105,0.25);
}

.small-note { opacity: 0.75; font-size: 13px; }
hr { border-top: 1px solid rgba(0,0,0,0.06); }
</style>
""",
    unsafe_allow_html=True,
)

# =========================
# Helpers
# =========================
def run_async(coro):
    """Run async safely in Streamlit."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Fallback: new loop
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
    """Fetch ALL available voices from Microsoft via edge-tts."""
    async def _fetch():
        return await edge_tts.list_voices()

    voices = run_async(_fetch())
    # Normalize minimal fields
    cleaned = []
    for v in voices:
        cleaned.append({
            "Name": v.get("Name"),
            "ShortName": v.get("ShortName"),
            "Locale": v.get("Locale"),
            "Gender": v.get("Gender"),
            "FriendlyName": v.get("FriendlyName") or v.get("Name"),
        })
    return cleaned

def group_voices(voices):
    # Group by locale (ar-EG, en-US...)
    by_locale = defaultdict(list)
    for v in voices:
        if v["Locale"] and v["ShortName"]:
            by_locale[v["Locale"]].append(v)
    # Sort each group
    for loc in by_locale:
        by_locale[loc] = sorted(by_locale[loc], key=lambda x: (x["Gender"] or "", x["FriendlyName"] or ""))
    return dict(sorted(by_locale.items(), key=lambda kv: kv[0]))

def make_data_audio_link(mp3_path: str) -> str:
    """Create a data: URL for preview/download link (works best for moderate file sizes)."""
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
# Sidebar (Profile & Links)
# =========================
with st.sidebar:
    st.markdown("## 👨‍💻 المهندس يوسف خالد")
    st.caption("AI & Automation Engineer | Web / Mobile / AI Solutions")

    st.markdown(
        """
<div class="glass">
<span class="badge">AI</span>
<span class="badge">Web</span>
<span class="badge">Mobile</span>
<span class="badge">Automation</span>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("### 🧩 اللي بعمله:")
    st.markdown(
        """
- 🤖 أتمتة المهام البشرية وتحويلها لأنظمة تعمل **أوتوماتيك بالكامل**
- 🌐 بناء مواقع وSaaS (Web Apps) + حلول AI
- 💼 مساعدة في **إعداد وتفعيل** اشتراكات Gemini / ChatGPT **بشكل رسمي عبر القنوات المتاحة**  
""".strip()
    )

    st.markdown("---")
    st.markdown("### 🔗 الروابط:")
    st.markdown(
        f"""
<a class="social-btn linkedin" href="{LINKEDIN_URL}" target="_blank">LinkedIn 👔</a>
<a class="social-btn drive" href="{PORTFOLIO_DRIVE_URL}" target="_blank">Google Drive Portfolio 📂</a>
<a class="social-btn whatsapp" href="{WHATSAPP_URL}" target="_blank">WhatsApp 💬</a>
""",
        unsafe_allow_html=True,
    )
    if FACEBOOK_URL.strip():
        st.markdown(
            f"""<a class="social-btn facebook" href="{FACEBOOK_URL}" target="_blank">Facebook</a>""",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.caption("© 2026 جميع الحقوق محفوظة لصالح Eng. Yousef Khaled")

# =========================
# Header
# =========================
st.markdown(
    """
<div class="hero">
  <h1>🎙️ Eng. Yousef | AI Voice Studio</h1>
  <p>حوّل أي نص لصوت واقعي + اختر السرعة بصيغة واضحة (x1 / x1.5 / x2) + رابط معاينة</p>
</div>
""",
    unsafe_allow_html=True,
)

# =========================
# Load voices
# =========================
with st.spinner("جاري تحميل مكتبة الأصوات..."):
    all_voices = fetch_voices_cached()
voices_by_locale = group_voices(all_voices)

# =========================
# Main layout
# =========================
left, right = st.columns([2, 1], gap="large")

with right:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("### ⚙️ الإعدادات")

    # Locale selection
    locale_list = list(voices_by_locale.keys())
    default_locale = "ar-EG" if "ar-EG" in voices_by_locale else (locale_list[0] if locale_list else "")
    locale = st.selectbox("🌍 اللغة/الدولة (Locale):", options=locale_list, index=locale_list.index(default_locale) if default_locale in locale_list else 0)

    # Search + voice select
    search = st.text_input("🔎 ابحث عن صوت (اسم/ذكر/أنثى):", value="")
    voice_items = voices_by_locale.get(locale, [])

    def label_voice(v):
        g = "ذكر" if (v.get("Gender") == "Male") else ("أنثى" if (v.get("Gender") == "Female") else "—")
        return f"{v.get('FriendlyName','')} — ({g})"

    filtered = voice_items
    if search.strip():
        s = search.strip().lower()
        filtered = [v for v in voice_items if (v.get("FriendlyName","").lower().find(s) != -1 or (v.get("Gender","").lower().find(s) != -1)]

    if not filtered:
        st.warning("لا توجد نتائج للبحث داخل هذه اللغة. جرّب Locale تاني أو امسح البحث.")
        filtered = voice_items

    voice_label_map = {label_voice(v): v["ShortName"] for v in filtered}
    selected_voice_label = st.selectbox("🎤 اختر الصوت:", options=list(voice_label_map.keys()))
    selected_voice_shortname = voice_label_map[selected_voice_label]

    st.markdown("---")

    # Speed as LIST (x1 / x1.5 ...)
    st.markdown("### ⚡ السرعة (واضحة للمستخدم)")
    speed_map = {
        "x0.5 (بطيء جدًا)": "-50%",
        "x0.75 (بطيء)": "-25%",
        "x1.0 (طبيعي)": "+0%",
        "x1.25 (سريع)": "+25%",
        "x1.5 (سريع جدًا)": "+50%",
        "x2.0 (أقصى سرعة)": "+100%",
    }
    speed_label = st.selectbox("اختر السرعة:", options=list(speed_map.keys()), index=2)
    rate_str = speed_map[speed_label]
    st.caption(f"✅ اختيارك: **{speed_label}**")

    st.markdown("---")

    # Pitch
    st.markdown("### 🎚️ طبقة الصوت (اختياري)")
    pitch = st.slider("Pitch (Hz):", -50, 50, 0, step=5)
    if pitch == 0:
        st.caption("طبيعي")
    elif pitch > 0:
        st.caption("أرفع")
    else:
        st.caption("أعمق")

    st.markdown('</div>', unsafe_allow_html=True)

with left:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("### 📝 اكتب النص هنا")
    text = st.text_area(
        label="",
        height=260,
        placeholder="اكتب النص العربي أو الإنجليزي... (ينفع نصوص طويلة للإعلانات/الفيديوهات/التعليم)",
    )
    st.caption(f"عدد الحروف: {len(text)}")
    generate = st.button("🚀 توليد الصوت + معاينة")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# Output area
# =========================
if generate:
    if not text.strip():
        st.warning("⚠️ اكتب نص الأول.")
    else:
        st.markdown("---")
        with st.spinner("جاري توليد الصوت..."):
            try:
                out_path = run_async(generate_audio(text, selected_voice_shortname, rate_str, pitch))

                st.success("✅ تم التوليد بنجاح!")
                c1, c2 = st.columns([3, 1])

                with c1:
                    st.markdown("### 🎧 معاينة داخل الموقع")
                    st.audio(out_path, format="audio/mp3")

                with c2:
                    st.markdown("### ⬇️ تحميل")
                    with open(out_path, "rb") as f:
                        st.download_button(
                            "تحميل MP3",
                            data=f,
                            file_name=f"Yousef_AI_Voice_{int(time.time())}.mp3",
                            mime="audio/mpeg",
                            use_container_width=True,
                        )

                # Preview link (data url)
                # ملاحظة: لو الملف كبير جدًا، data: link ممكن يبقى تقيل. لكن لمعظم الحالات شغال ممتاز.
                try:
                    data_url = make_data_audio_link(out_path)
                    st.markdown("### 🔗 رابط معاينة (يفتح الصوت في صفحة جديدة)")
                    st.markdown(
                        f'<a class="clean-link" href="{data_url}" target="_blank">👉 افتح المعاينة في تبويب جديد</a>',
                        unsafe_allow_html=True,
                    )
                    st.caption("لو النص طويل جدًا والرابط بقى تقيل: استخدم زر التحميل العادي.")
                except Exception:
                    st.caption("تعذر إنشاء رابط معاينة مباشر (استخدم زر التحميل).")

            except Exception as e:
                st.error(f"حدث خطأ أثناء التوليد: {e}")

st.markdown("---")
st.markdown(
    "<div class='small-note'>ملاحظة: الأصوات تُجلب تلقائيًا من edge-tts، يعني كل ما Microsoft تضيف أصوات هتظهر عندك تلقائي.</div>",
    unsafe_allow_html=True,
)
