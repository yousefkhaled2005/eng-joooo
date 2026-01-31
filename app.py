import streamlit as st
import edge_tts
import asyncio
import tempfile
import os
import time

# ==========================================
# 1. إعدادات الصفحة
# ==========================================
st.set_page_config(
    page_title="Eng. Yousef Khaled | Pro AI Studio",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. تنسيق CSS (تم تحسين شكل السلايدر)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif;
        direction: rtl;
        text-align: right;
    }
    
    .stApp {
        background-color: #f8f9fa;
        background-image: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }

    /* تحسين شكل السلايدر ليكون نقاط محددة */
    div[data-testid="stSelectSlider"] > div > div > div {
        cursor: pointer;
    }

    /* الهيدر */
    .hero-header {
        background: linear-gradient(120deg, #2b5876 0%, #4e4376 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    /* زر التحويل */
    .stButton > button {
        background: linear-gradient(90deg, #d53369 0%, #daae51 100%);
        color: white;
        border: none;
        padding: 10px 20px;
        font-size: 18px;
        border-radius: 10px;
        width: 100%;
        transition: transform 0.2s;
    }
    .stButton > button:hover {
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. البيانات والدوال
# ==========================================
VOICE_DATABASE = {
    "🌍 العربية (Arabic)": {
        "🇪🇬 مصر - شاكر (رسمي)": "ar-EG-ShakirNeural",
        "🇪🇬 مصر - سلمى (ودود)": "ar-EG-SalmaNeural",
        "🇸🇦 السعودية - حامد": "ar-SA-HamedNeural",
        "🇸🇦 السعودية - زارية": "ar-SA-ZariyahNeural",
        "🇦🇪 الإمارات - حمد": "ar-AE-HamdanNeural",
        "🇯🇴 الأردن - تيم": "ar-JO-TaimNeural",
    },
    "🇺🇸 الإنجليزية (English)": {
        "🇺🇸 US - Guy": "en-US-GuyNeural",
        "🇺🇸 US - Aria": "en-US-AriaNeural",
        "🇬🇧 UK - Ryan": "en-GB-RyanNeural",
    }
}

async def generate_audio_stream(text, voice, rate_str, pitch_hz):
    # تحويل الـ Pitch لصيغة نصية
    pitch_str = f"{pitch_hz:+d}Hz"
    communicate = edge_tts.Communicate(text, voice, rate=rate_str, pitch=pitch_str)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        await communicate.save(tmp_file.name)
        return tmp_file.name

# ==========================================
# 4. واجهة التطبيق
# ==========================================

# الشريط الجانبي (نفس بياناتك)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4140/4140047.png", width=80)
    st.markdown("### المهندس يوسف خالد")
    st.caption("AI & Automation Engineer")
    st.markdown("---")
    st.markdown("**🔗 تواصل معي:**")
    st.markdown("[LinkedIn Profile](https://www.linkedin.com/in/yousefkhaleda)")
    st.markdown("[WhatsApp: 01007097545](https://wa.me/201007097545)")

# الهيدر
st.markdown("""
<div class="hero-header">
    <h1 style='margin:0'>🎙️ Eng. Yousef AI Studio</h1>
    <p>تحويل النص إلى صوت احترافي</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    st.info("🎛️ **إعدادات الصوت**")
    
    # 1. اختيار الصوت
    cat = st.selectbox("اللغة:", list(VOICE_DATABASE.keys()))
    voice_name = st.selectbox("المعلق:", list(VOICE_DATABASE[cat].keys()))
    voice_code = VOICE_DATABASE[cat][voice_name]
    
    st.markdown("---")
    
    # 2. سرعة القراءة (التعديل الجديد هنا) ⚡
    # قمنا بعمل خريطة لربط الاسم بالقيمة الفعلية
    speed_options = {
        "x0.5 (بطيء جداً)": "-50%",
        "x0.75 (بطيء)": "-25%",
        "x1.0 (طبيعي)": "+0%",
        "x1.25 (سريع)": "+25%",
        "x1.5 (سريع جداً)": "+50%",
        "x2.0 (أقصى سرعة)": "+100%"
    }
    
    # السلايدر الآن يختار من القائمة دي بس
    selected_speed_label = st.select_slider(
        "⚡ سرعة القراءة (Speed):",
        options=list(speed_options.keys()),
        value="x1.0 (طبيعي)"
    )
    # استخراج القيمة الحقيقية (مثل +50%)
    real_speed_value = speed_options[selected_speed_label]
    
    st.markdown("---")
    
    # 3. طبقة الصوت
    pitch = st.slider("🎚️ طبقة الصوت (Pitch):", -50, 50, 0, step=5, format="%d Hz")

with col2:
    st.success("📝 **مساحة العمل**")
    text_area = st.text_area("", height=320, placeholder="اكتب النص هنا...")
    
    generate_btn = st.button("🚀 تحويل ومعاينة (Generate)")

# منطقة النتائج والمعاينة
if generate_btn and text_area:
    st.markdown("---")
    with st.spinner("جاري المعالجة..."):
        try:
            # تشغيل الدالة
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            output_file = loop.run_until_complete(
                generate_audio_stream(text_area, voice_code, real_speed_value, pitch)
            )
            
            # عرض المعاينة بشكل واضح
            st.markdown("### 🎧 معاينة الصوت (Preview):")
            
            # 1. مشغل الصوت المدمج (للمعاينة الفورية)
            st.audio(output_file, format="audio/mp3")
            
            # 2. زر التحميل
            with open(output_file, "rb") as file:
                st.download_button(
                    label="⬇️ تحميل الملف (Download MP3)",
                    data=file,
                    file_name="Yousef_AI_Voice.mp3",
                    mime="audio/mp3",
                    use_container_width=True
                )
                
            st.success("✅ تم التحويل بنجاح!")
            
        except Exception as e:
            st.error(f"حدث خطأ: {e}")
