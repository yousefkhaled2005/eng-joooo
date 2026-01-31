import streamlit as st
import asyncio
import edge_tts
import os
import base64

# --- إعدادات الصفحة ---
st.set_page_config(page_title="موقع المهندس يوسف خالد", page_icon="🚀", layout="wide")

# --- تنسيق CSS مخصص لشكل خرافي ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 20px; background: linear-gradient(45deg, #007bff, #00ff88); color: white; border: none; font-weight: bold; }
    .footer { text-align: center; padding: 20px; font-size: 14px; color: #888; border-top: 1px solid #333; margin-top: 50px; }
    .whatsapp-btn { background-color: #25d366; color: white; padding: 10px 20px; border-radius: 50px; text-decoration: none; display: inline-block; }
    .profile-card { background: #1a1c24; padding: 20px; border-radius: 15px; border-left: 5px solid #007bff; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- معلومات التواصل والمطور ---
with st.sidebar:
    st.markdown(f"### 👨‍💻 المطور: يوسف خالد")
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100) # صورة تعبيرية
    st.info("مهندس كمبيوتر وجرافيك ديزاينر متخصص في الـ AI و Web Mobile.")
    st.write("🚀 تفعيل اشتراكات Gemini & ChatGPT Pro")
    st.write("🤖 أتمتة المهام البشرية بالكامل")
    
    st.markdown(f"[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/yousefkhaleda)")
    st.markdown(f"[![Portfolio](https://img.shields.io/badge/Portfolio-Google_Drive-orange?style=for-the-badge&logo=google-drive)](https://drive.google.com/drive/folders/1F0ziAJ-vRuAd_3GngeyYltMK3iFdUERa?usp=drive_link)")
    st.markdown(f'<a href="https://wa.me/201007097545" class="whatsapp-btn">💬 تواصل واتساب</a>', unsafe_allow_html=True)

# --- الواجهة الرئيسية ---
st.title("🎙️ منصة المهندس يوسف لتحويل النص إلى صوت (AI)")
st.subheader("تحويل ذكي، أصوات متعددة، وتحكم كامل في السرعة")

col1, col2 = st.columns([2, 1])

with col1:
    text_input = st.text_area("أدخل النص المراد تحويله هنا:", placeholder="اكتب ما تريد تحويله لصوت احترافي...", height=250)
    
with col2:
    # قائمة الأصوات الاحترافية
    voices = {
        "عربي - شاكر (ذكر)": "ar-EG-ShakirNeural",
        "عربي - سلمى (أنثى)": "ar-EG-SalmaNeural",
        "عربي - حمدان (إماراتي)": "ar-AE-HamdanNeural",
        "English - Guy (Male)": "en-US-GuyNeural",
        "English - Ava (Female)": "en-US-AvaNeural"
    }
    selected_voice_label = st.selectbox("اختر الصوت:", list(voices.keys()))
    voice = voices[selected_voice_label]
    
    # اختيار السرعة من قائمة
    speed_options = {"x0.5 (بطيء)": "-50%", "x1.0 (طبيعي)": "+0%", "x1.5 (سريع)": "+50%", "x2.0 (سريع جداً)": "+100%"}
    speed_label = st.selectbox("سرعة الصوت:", list(speed_options.keys()))
    speed = speed_options[speed_label]

# --- وظيفة المعالجة ---
async def generate_audio(text, voice, speed):
    communicate = edge_tts.Communicate(text, voice, rate=speed)
    await communicate.save("output.mp3")

if st.button("توليد الصوت الآن 🔥"):
    if text_input.strip():
        with st.spinner("جاري معالجة الصوت بأعلى جودة..."):
            asyncio.run(generate_audio(text_input, voice, speed))
            
            # عرض الصوت للمعاينة
            audio_file = open("output.mp3", "rb")
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format="audio/mp3")
            
            # زر التحميل
            st.download_button(
                label="📥 تحميل الملف الصوتي",
                data=audio_bytes,
                file_name=f"Yousef_AI_{selected_voice_label}.mp3",
                mime="audio/mp3"
            )
    else:
        st.warning("من فضلك أدخل نصاً أولاً!")

# --- فوتر الحقوق ---
st.markdown("---")
st.markdown(f"""
    <div class="footer">
        <p>جميع الحقوق محفوظة © 2026 لصالح المهندس <b>يوسف خالد جودة محسب</b></p>
        <p>المنصة تعمل بتقنيات AI Web Mobile | متخصصون في الأتمتة الشاملة</p>
    </div>
""", unsafe_allow_html=True)
