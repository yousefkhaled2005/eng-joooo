import streamlit as st
import edge_tts
import asyncio
import tempfile
import os
import time

# ==========================================
# 1. إعدادات الصفحة المتقدمة (Page Config)
# ==========================================
st.set_page_config(
    page_title="Eng. Yousef Khaled | Pro AI Studio",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://wa.me/201007097545',
        'Report a bug': "https://wa.me/201007097545",
        'About': "# تم التطوير بواسطة المهندس يوسف خالد"
    }
)

# ==========================================
# 2. تصميم الواجهة الخرافي (Advanced CSS)
# ==========================================
st.markdown("""
<style>
    /* استيراد خطوط عربية حديثة */
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&display=swap');
    
    /* المتغيرات اللونية */
    :root {
        --primary-color: #4A90E2;
        --secondary-color: #FF4B4B;
        --bg-gradient: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        --card-bg: #ffffff;
        --text-color: #2c3e50;
    }

    /* تنسيق الصفحة العام */
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif;
        direction: rtl;
        text-align: right;
    }
    
    /* خلفية متدرجة للصفحة */
    .stApp {
        background-image: url("https://www.transparenttextures.com/patterns/cubes.png");
        background-color: #f8f9fa;
    }

    /* تصميم الهيدر الرئيسي */
    .hero-header {
        background: linear-gradient(120deg, #155799, #159957);
        padding: 40px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        animation: fadeIn 1.5s ease-in-out;
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 900;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
    }

    /* تصميم الكروت (Containers) */
    .stTextArea, .stSelectbox, .stSlider {
        background-color: white;
        border-radius: 15px;
        padding: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    
    /* أزرار التشغيل */
    .stButton > button {
        background: linear-gradient(90deg, #FF4B4B 0%, #FF9068 100%);
        color: white;
        border: none;
        padding: 15px 30px;
        border-radius: 50px;
        font-size: 18px;
        font-weight: bold;
        box-shadow: 0 10px 20px rgba(255, 75, 75, 0.3);
        width: 100%;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 25px rgba(255, 75, 75, 0.4);
    }

    /* القائمة الجانبية */
    section[data-testid="stSidebar"] {
        background-color: #1e2329;
        color: white;
    }
    
    /* روابط السوشيال */
    .social-link {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 12px;
        margin: 8px 0;
        border-radius: 10px;
        color: white !important;
        text-decoration: none;
        font-weight: bold;
        transition: 0.3s;
    }
    .linkedin-btn { background: #0077b5; }
    .whatsapp-btn { background: #25D366; }
    .portfolio-btn { background: #E1306C; }
    
    .social-link:hover { opacity: 0.9; transform: scale(1.02); }

    /* أنيميشن */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }

</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. مكتبة الأصوات الضخمة (Mega Database)
# ==========================================
VOICE_DATABASE = {
    "🌍 العربية (Arabic)": {
        "🇪🇬 مصر - شاكر (رسمي/إخباري)": "ar-EG-ShakirNeural",
        "🇪🇬 مصر - سلمى (إعلاني/ودود)": "ar-EG-SalmaNeural",
        "🇸🇦 السعودية - حامد (وقور)": "ar-SA-HamedNeural",
        "🇸🇦 السعودية - زارية (تفاعلي)": "ar-SA-ZariyahNeural",
        "🇦🇪 الإمارات - فاطمة": "ar-AE-FatimaNeural",
        "🇦🇪 الإمارات - حمد": "ar-AE-HamdanNeural",
        "🇯🇴 الأردن - تيم": "ar-JO-TaimNeural",
        "🇩🇿 الجزائر - إسماعيل": "ar-DZ-IsmaelNeural",
        "🇧🇭 البحرين - علي": "ar-BH-AliNeural",
        "🇮🇶 العراق - باسل": "ar-IQ-BasselNeural",
        "🇱🇾 ليبيا - عمر": "ar-LY-OmarNeural",
        "🇶🇦 قطر - أمل": "ar-QA-AmalNeural",
        "🇾🇪 اليمن - مريم": "ar-YE-MaryamNeural",
    },
    "🇺🇸 الإنجليزية (English)": {
        "🇺🇸 US - Guy (Professional)": "en-US-GuyNeural",
        "🇺🇸 US - Aria (Energetic)": "en-US-AriaNeural",
        "🇺🇸 US - Christopher (Deep/Documentary)": "en-US-ChristopherNeural",
        "🇺🇸 US - Jenny (Assistant)": "en-US-JennyNeural",
        "🇬🇧 UK - Ryan (Narrator)": "en-GB-RyanNeural",
        "🇬🇧 UK - Sonia (News)": "en-GB-SoniaNeural",
        "🇬🇧 UK - Libby (Soft)": "en-GB-LibbyNeural",
        "🇦🇺 Australia - Natasha": "en-AU-NatashaNeural",
    },
    "🌐 لغات أخرى (Global)": {
        "🇫🇷 French - Henri": "fr-FR-HenriNeural",
        "🇫🇷 French - Denise": "fr-FR-DeniseNeural",
        "🇩🇪 German - Conrad": "de-DE-ConradNeural",
        "🇩🇪 German - Katja": "de-DE-KatjaNeural",
        "🇪🇸 Spanish - Alvaro": "es-ES-AlvaroNeural",
        "🇮🇹 Italian - Diego": "it-IT-DiegoNeural",
        "🇯🇵 Japanese - Keita": "ja-JP-KeitaNeural",
        "🇨🇳 Chinese - Xiaoxiao": "zh-CN-XiaoxiaoNeural",
        "🇷🇺 Russian - Dmitry": "ru-RU-DmitryNeural",
    }
}

# ==========================================
# 4. دوال المعالجة (Core Logic)
# ==========================================
async def generate_audio_stream(text, voice, rate_multiplier, pitch_hz):
    # حساب السرعة
    if rate_multiplier == 1.0:
        rate_str = "+0%"
    else:
        percentage = int((rate_multiplier - 1) * 100)
        rate_str = f"{percentage:+d}%"
    
    # حساب حدة الصوت (Pitch)
    pitch_str = f"{pitch_hz:+d}Hz"
    
    communicate = edge_tts.Communicate(text, voice, rate=rate_str, pitch=pitch_str)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        await communicate.save(tmp_file.name)
        return tmp_file.name

# ==========================================
# 5. الشريط الجانبي (Sidebar Portfolio)
# ==========================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center;">
        <img src="https://cdn-icons-png.flaticon.com/512/4140/4140047.png" width="100" style="border-radius: 50%; border: 3px solid #4A90E2;">
        <h2 style="color: white; margin-top: 10px;">المهندس يوسف خالد</h2>
        <p style="color: #ccc; font-size: 0.9rem;">AI & Automation Engineer<br>Full Stack Developer</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # قائمة الخدمات
    st.markdown("### 🛠️ خدماتي الاحترافية")
    with st.expander("🤖 أتمتة الأعمال (Automation)", expanded=True):
        st.write("تحويل المهام اليدوية والبيانات إلى أنظمة تعمل أوتوماتيكياً بالكامل لتوفير الوقت والجهد.")
    with st.expander("🌐 تصميم وتطوير المواقع"):
        st.write("إنشاء مواقع ويب عصرية وتطبيقات (SaaS) باستخدام أحدث تقنيات AI & Python.")
    with st.expander("💎 تفعيل اشتراكات Premium"):
        st.write("توفير حسابات ChatGPT Pro, Gemini Advanced, Midjourney.")

    st.markdown("---")
    
    # أزرار التواصل
    st.markdown("### 🔗 تواصل معي")
    st.markdown("""
    <a href="https://www.linkedin.com/in/yousefkhaleda" target="_blank" class="social-link linkedin-btn">
        <span>LinkedIn Profile 👔</span>
    </a>
    <a href="https://drive.google.com/drive/folders/1F0ziAJ-vRuAd_3GngeyYltMK3iFdUERa?usp=drive_link" target="_blank" class="social-link portfolio-btn">
        <span>معرض الأعمال (Portfolio) 📂</span>
    </a>
    <a href="https://wa.me/201007097545" target="_blank" class="social-link whatsapp-btn">
        <span>WhatsApp (01007097545) 💬</span>
    </a>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption("© 2026 Developed by Eng. Yousef Khaled")

# ==========================================
# 6. المنطقة الرئيسية (Main Content)
# ==========================================

# الهيدر المتحرك
st.markdown("""
<div class="hero-header">
    <div class="hero-title">🎙️ Eng. Yousef Studio</div>
    <div class="hero-subtitle">أقوى منصة لتحويل النص إلى صوت بشري باستخدام الذكاء الاصطناعي</div>
</div>
""", unsafe_allow_html=True)

# التبويبات الرئيسية
tab1, tab2 = st.tabs(["🎛️ ستوديو التحويل (Voice Studio)", "ℹ️ عن المطور (About Me)"])

with tab1:
    # تقسيم الشاشة
    col_settings, col_input = st.columns([1, 2])
    
    with col_settings:
        st.markdown("### ⚙️ إعدادات الصوت")
        
        # 1. اختيار اللغة/الفئة
        category = st.selectbox("🌐 اختر اللغة / المنطقة:", list(VOICE_DATABASE.keys()))
        
        # 2. اختيار الصوت بناءً على الفئة
        voice_options = VOICE_DATABASE[category]
        selected_voice_name = st.selectbox("👤 اختر المعلق الصوتي:", list(voice_options.keys()))
        selected_voice_code = voice_options[selected_voice_name]
        
        st.markdown("---")
        
        # 3. التحكم في السرعة (x1, x1.5)
        st.markdown("**⚡ سرعة القراءة (Speed):**")
        speed = st.select_slider(
            "",
            options=[0.5, 0.75, 1.0, 1.25, 1.5, 2.0],
            value=1.0,
            format_func=lambda x: f"{x}x"
        )
        
        # 4. التحكم في حدة الصوت (Pitch) - ميزة جديدة
        st.markdown("**🎚️ طبقة الصوت (Pitch):**")
        pitch = st.slider("", -50, 50, 0, step=5, format="%d Hz")
        if pitch > 0: st.caption("صوت أرفع (High)")
        elif pitch < 0: st.caption("صوت أضخم (Deep)")
        else: st.caption("طبيعي (Normal)")

    with col_input:
        st.markdown("### 📝 مساحة العمل")
        
        text_area = st.text_area(
            label="",
            placeholder="اكتب النص الذي تريد تحويله هنا... يمكنك كتابة نصوص طويلة للمقالات، الإعلانات، أو الفيديوهات التعليمية.",
            height=300
        )
        
        # عداد الحروف
        st.caption(f"عدد الحروف: {len(text_area)} حرف")
        
        # زر التحويل العملاق
        generate_btn = st.button("🚀 تحويل النص إلى صوت (Generate Audio)")

    # منطقة النتائج
    if generate_btn:
        if not text_area.strip():
            st.warning("⚠️ يرجى كتابة نص أولاً!")
        else:
            st.markdown("---")
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # محاكاة التحميل
            status_text.text("جاري الاتصال بالسيرفرات السحابية...")
            time.sleep(0.5)
            progress_bar.progress(30)
            status_text.text("جاري معالجة طبقة الصوت والسرعة...")
            
            try:
                # عملية التوليد الفعلية
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                output_file = loop.run_until_complete(
                    generate_audio_stream(text_area, selected_voice_code, speed, pitch)
                )
                
                progress_bar.progress(100)
                status_text.text("✅ تم التحويل بنجاح!")
                st.balloons() # احتفال
                
                # عرض النتيجة في كارت جميل
                st.markdown("""
                <div style="background-color: #d4edda; color: #155724; padding: 20px; border-radius: 10px; text-align: center; margin-top: 20px;">
                    <h3>✨ ملفك الصوتي جاهز!</h3>
                </div>
                """, unsafe_allow_html=True)
                
                res_col1, res_col2 = st.columns([3, 1])
                
                with res_col1:
                    st.audio(output_file, format="audio/mp3")
                
                with res_col2:
                    with open(output_file, "rb") as file:
                        btn = st.download_button(
                            label="⬇️ تحميل MP3 عالي الجودة",
                            data=file,
                            file_name=f"Yousef_Studio_{int(time.time())}.mp3",
                            mime="audio/mp3",
                            use_container_width=True
                        )
                        
            except Exception as e:
                st.error(f"حدث خطأ أثناء المعالجة: {e}")
                progress_bar.empty()

with tab2:
    st.markdown("### 👨‍💻 نبذة عن المطور")
    st.info("""
    **المهندس يوسف خالد**
    
    مبتكر ومطور برمجيات شامل (Full Stack Developer) ومتخصص في حلول الذكاء الاصطناعي.
    أقوم بمساعدة الشركات والأفراد على:
    1. أتمتة المهام اليومية المملة.
    2. بناء أدوات SaaS مثل هذه الأداة.
    3. تقديم استشارات تقنية في مجالات الويب والتصميم.
    
    **للتواصل التجاري:** 01007097545
    """)
    
    # عرض مشاريع أخرى (Placeholder)
    st.markdown("#### 🌟 مشاريع أخرى")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.image("https://cdn-icons-png.flaticon.com/512/3062/3062634.png", width=50)
        st.write("**Queen Travel System**")
    with c2:
        st.image("https://cdn-icons-png.flaticon.com/512/3144/3144456.png", width=50)
        st.write("**Hoor Fashion Store**")
    with c3:
        st.image("https://cdn-icons-png.flaticon.com/512/1680/1680899.png", width=50)
        st.write("**Automation Bots**")
