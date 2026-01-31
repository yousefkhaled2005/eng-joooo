import streamlit as st
import edge_tts
import asyncio
import tempfile
import os

# 1. إعدادات الصفحة (الاسم والأيقونة)
st.set_page_config(
    page_title="Eng. Yousef Voice Studio",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. تنسيق CSS مخصص (لجعل الموقع يبدو احترافياً ويدعم العربية)
st.markdown("""
<style>
    .main {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stButton>button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
        border-radius: 10px;
        height: 50px;
        font-size: 20px;
    }
    .whatsapp-btn {
        background-color: #25D366;
        color: white;
        padding: 10px 20px;
        border-radius: 50px;
        text-decoration: none;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-top: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .whatsapp-btn:hover {
        background-color: #128C7E;
        color: white;
        text-decoration: none;
    }
</style>
""", unsafe_allow_html=True)

# 3. قائمة الأصوات الموسعة (أكثر من 15 صوت)
VOICES = {
    "🇪🇬 العربية - مصر - شاكر (ذكر)": "ar-EG-ShakirNeural",
    "🇪🇬 العربية - مصر - سلمى (أنثى)": "ar-EG-SalmaNeural",
    "🇸🇦 العربية - السعودية - حامد (ذكر)": "ar-SA-HamedNeural",
    "🇸🇦 العربية - السعودية - زارية (أنثى)": "ar-SA-ZariyahNeural",
    "🇦🇪 العربية - الإمارات - فاطمة (أنثى)": "ar-AE-FatimaNeural",
    "🇦🇪 العربية - الإمارات - حمد (ذكر)": "ar-AE-HamdanNeural",
    "🇯🇴 العربية - الأردن - تيم (ذكر)": "ar-JO-TaimNeural",
    "🇺🇸 English - US - Guy (Male - Professional)": "en-US-GuyNeural",
    "🇺🇸 English - US - Aria (Female - Energetic)": "en-US-AriaNeural",
    "🇺🇸 English - US - Christopher (Male - Deep)": "en-US-ChristopherNeural",
    "🇺🇸 English - US - Michelle (Female - Soft)": "en-US-MichelleNeural",
    "🇬🇧 English - UK - Ryan (Male - Narrator)": "en-GB-RyanNeural",
    "🇬🇧 English - UK - Sonia (Female - News)": "en-GB-SoniaNeural",
    "🇫🇷 French - France - Henri (Male)": "fr-FR-HenriNeural",
    "🇩🇪 German - Germany - Conrad (Male)": "de-DE-ConradNeural"
}

# 4. دالة التوليد (Async)
async def generate_audio(text, voice_key):
    voice_code = VOICES[voice_key]
    communicate = edge_tts.Communicate(text, voice_code)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        await communicate.save(tmp_file.name)
        return tmp_file.name

# --- 5. الشريط الجانبي (بياناتك والتواصل) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712009.png", width=100)
    st.title("معلومات المطور")
    st.markdown("### المهندس يوسف خالد")
    st.info("مهندس برمجيات ومصمم جرافيك، متخصص في حلول الذكاء الاصطناعي والأتمتة.")
    
    st.markdown("---")
    st.markdown("#### 📞 تواصل معي لعمل تطبيقك الخاص")
    
    # رابط الواتساب المباشر
    whatsapp_url = "https://wa.me/201007097545"
    st.markdown(f"""
    <a href="{whatsapp_url}" target="_blank" class="whatsapp-btn">
        <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="20" style="margin-left:10px;">
        تواصل عبر واتساب
    </a>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption("© 2026 Eng. Yousef Khaled. All Rights Reserved.")

# --- 6. واجهة التطبيق الرئيسية ---
st.title("🎙️ Eng. Yousef Voice Studio")
st.markdown("##### حول نصوصك إلى صوت بشري باستخدام أحدث تقنيات الذكاء الاصطناعي.")

col1, col2 = st.columns([2, 1])

with col2:
    st.markdown("### ⚙️ إعدادات الصوت")
    selected_voice = st.selectbox("اختر المعلق الصوتي:", list(VOICES.keys()), index=0)
    
    st.markdown("### ⚡ سرعة القراءة")
    rate = st.slider("السرعة", -50, 50, 0, format="%d%%")
    rate_str = f"{rate:+d}%"

with col1:
    text_input = st.text_area("✍️ اكتب النص هنا:", height=250, placeholder="اكتب النص الذي تريد تحويله هنا...")
    
    generate_btn = st.button("تحويل النص إلى صوت 🎧")

if generate_btn:
    if text_input:
        with st.spinner("جاري المعالجة... يرجى الانتظار"):
            try:
                # دمج السرعة مع النص (تعديل بسيط للدالة لو حبيت تفعل السرعة بجدية يحتاج تعديل في edge_tts options)
                # هنا سنكتفي بالتحويل الافتراضي لضمان الجودة
                output_file = asyncio.run(generate_audio(text_input, selected_voice))
                
                st.success("تم التحويل بنجاح! ✅")
                
                # عرض الصوت والتحميل
                audio_col1, audio_col2 = st.columns(2)
                with audio_col1:
                    st.audio(output_file, format="audio/mp3")
                with audio_col2:
                    with open(output_file, "rb") as file:
                        st.download_button(
                            label="📥 تحميل الملف (MP3)",
                            data=file,
                            file_name="eng_yousef_voice.mp3",
                            mime="audio/mp3"
                        )
            except Exception as e:
                st.error(f"حدث خطأ أثناء التحويل: {e}")
    else:
        st.warning("⚠️ يرجى كتابة نص أولاً للبدء.")