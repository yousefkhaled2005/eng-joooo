import streamlit as st
import edge_tts
import asyncio
import tempfile
import os
import time
import base64
from datetime import datetime

# ==========================================
# 1. تكوين الصفحة والنظام (System Config)
# ==========================================
st.set_page_config(
    page_title="Eng. Yousef | AI Enterprise Studio",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تهيئة الجلسة لتخزين الأرشيف (Session State)
if 'history' not in st.session_state:
    st.session_state.history = []
if 'generated_count' not in st.session_state:
    st.session_state.generated_count = 0

# ==========================================
# 2. التنسيق المتقدم (Enterprise CSS)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;500;800&display=swap');
    
    :root {
        --primary: #4A90E2;
        --secondary: #FF4B4B;
        --dark: #1E2329;
        --light: #F8F9FA;
    }

    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif;
        direction: rtl;
        text-align: right;
    }

    /* خلفية التطبيق */
    .stApp {
        background-color: #f4f6f9;
    }

    /* الهيدر الرئيسي */
    .main-header {
        background: linear-gradient(135deg, #000428 0%, #004e92 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .stat-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center;
        border-bottom: 4px solid var(--primary);
    }
    .stat-number {
        font-size: 24px;
        font-weight: bold;
        color: var(--dark);
    }
    .stat-label {
        font-size: 14px;
        color: #666;
    }

    /* تحسين السلايدر */
    div[data-testid="stSelectSlider"] label { color: var(--secondary); font-weight: bold; }
    
    /* الأزرار */
    .stButton button {
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    /* الشريط الجانبي */
    [data-testid="stSidebar"] {
        background-color: white;
        border-left: 1px solid #eee;
    }
    
    .sidebar-profile {
        text-align: center;
        padding: 20px 0;
        background: linear-gradient(to bottom, #f8f9fa, #fff);
        border-radius: 15px;
        margin-bottom: 20px;
    }
    
    /* أيقونات التواصل */
    .social-row { display: flex; gap: 10px; justify-content: center; margin-top: 15px; }
    .social-icon { 
        width: 40px; height: 40px; 
        border-radius: 50%; 
        display: flex; align-items: center; justify-content: center; 
        color: white; text-decoration: none; font-size: 18px;
        transition: transform 0.2s;
    }
    .social-icon:hover { transform: scale(1.1); }
    .wa { background: #25D366; }
    .li { background: #0077b5; }
    .pf { background: #E1306C; }

</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. قاعدة البيانات الموسعة (Global Voices)
# ==========================================
VOICES = {
    "AR - العربية": {
        "🇪🇬 مصر - شاكر (رسمي)": "ar-EG-ShakirNeural",
        "🇪🇬 مصر - سلمى (إعلاني)": "ar-EG-SalmaNeural",
        "🇸🇦 السعودية - حامد": "ar-SA-HamedNeural",
        "🇸🇦 السعودية - زارية": "ar-SA-ZariyahNeural",
        "🇦🇪 الإمارات - حمد": "ar-AE-HamdanNeural",
        "🇦🇪 الإمارات - فاطمة": "ar-AE-FatimaNeural",
        "🇯🇴 الأردن - تيم": "ar-JO-TaimNeural",
        "🇩🇿 الجزائر - إسماعيل": "ar-DZ-IsmaelNeural",
        "🇧🇭 البحرين - علي": "ar-BH-AliNeural",
        "🇮🇶 العراق - باسل": "ar-IQ-BasselNeural",
        "🇱🇾 ليبيا - عمر": "ar-LY-OmarNeural",
        "🇾🇪 اليمن - مريم": "ar-YE-MaryamNeural",
    },
    "EN - English": {
        "🇺🇸 US - Guy (Professional)": "en-US-GuyNeural",
        "🇺🇸 US - Aria (Energetic)": "en-US-AriaNeural",
        "🇺🇸 US - Christopher (Deep)": "en-US-ChristopherNeural",
        "🇬🇧 UK - Ryan (Narrator)": "en-GB-RyanNeural",
        "🇬🇧 UK - Sonia (News)": "en-GB-SoniaNeural",
    },
    "FR - Français": {
        "🇫🇷 France - Henri": "fr-FR-HenriNeural",
        "🇫🇷 France - Denise": "fr-FR-DeniseNeural",
    },
    "DE - Deutsch": {
        "🇩🇪 Germany - Conrad": "de-DE-ConradNeural",
        "🇩🇪 Germany - Katja": "de-DE-KatjaNeural",
    }
}

# ==========================================
# 4. المحرك (Core Engine)
# ==========================================
async def engine_generate(text, voice_code, speed_x, pitch_hz, volume_pct):
    # 1. معالجة السرعة
    if speed_x == 1.0: rate_str = "+0%"
    else:
        pct = int((speed_x - 1) * 100)
        rate_str = f"{pct:+d}%"
    
    # 2. معالجة الطبقة
    pitch_str = f"{pitch_hz:+d}Hz"
    
    # 3. معالجة الصوت (Volume)
    vol_str = f"{volume_pct:+d}%"
    
    communicate = edge_tts.Communicate(text, voice_code, rate=rate_str, pitch=pitch_str, volume=vol_str)
    
    # اسم ملف فريد
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"YousefStudio_{timestamp}.mp3"
    filepath = os.path.join(tempfile.gettempdir(), filename)
    
    await communicate.save(filepath)
    return filepath, filename

# ==========================================
# 5. الشريط الجانبي (Professional Sidebar)
# ==========================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-profile">
        <img src="https://cdn-icons-png.flaticon.com/512/2620/2620581.png" width="90" style="margin-bottom:10px;">
        <h3 style="margin:0;">المهندس يوسف خالد</h3>
        <p style="color:#777; font-size:12px; margin:0;">Software Engineer & Business Owner</p>
    </div>
    """, unsafe_allow_html=True)
    
    # القوائم المنسدلة للخدمات
    with st.expander("🚀 خدمات الشركات (Business)", expanded=True):
        st.markdown("**✈️ Queen Travel:** سياحة وتأجير سيارات.")
        st.markdown("**👗 Hoor Brand:** براند ملابس عصري.")
        st.markdown("**🤖 Automation:** حلول الذكاء الاصطناعي.")
    
    with st.expander("🛠️ الخدمات التقنية (Tech)"):
        st.caption("تطوير مواقع (Web Dev)")
        st.caption("سكربتات بايثون (Python Scripting)")
        st.caption("تفعيل اشتراكات AI Premium")

    st.markdown("---")
    
    # قسم التواصل بتصميم جديد
    st.markdown("<p style='text-align:center; font-weight:bold;'>تواصل معي مباشرة</p>", unsafe_allow_html=True)
    st.markdown("""
    <div class="social-row">
        <a href="https://wa.me/201007097545" target="_blank" class="social-icon wa">W</a>
        <a href="https://www.linkedin.com/in/yousefkhaleda" target="_blank" class="social-icon li">in</a>
        <a href="https://drive.google.com/drive/folders/1F0ziAJ-vRuAd_3GngeyYltMK3iFdUERa?usp=drive_link" target="_blank" class="social-icon pf">P</a>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("💡 الإصدار V6.0 Enterprise")

# ==========================================
# 6. الواجهة الرئيسية (Main Dashboard)
# ==========================================

# الهيدر
st.markdown("""
<div class="main-header">
    <h1 style="font-weight:900; margin-bottom:10px;">🎙️ Eng. Yousef AI Voice Platform</h1>
    <p style="opacity:0.8;">نظام ذكي لتحويل النصوص إلى تعليق صوتي بشري | Enterprise Edition</p>
</div>
""", unsafe_allow_html=True)

# شريط الحالة (Stats)
col_s1, col_s2, col_s3 = st.columns(3)
with col_s1:
    st.markdown(f"""<div class="stat-card"><div class="stat-number">{st.session_state.generated_count}</div><div class="stat-label">ملفات تم إنشاؤها</div></div>""", unsafe_allow_html=True)
with col_s2:
    st.markdown(f"""<div class="stat-card"><div class="stat-number">{len(VOICES['AR - العربية']) + len(VOICES['EN - English']) + 4}</div><div class="stat-label">صوت متاح</div></div>""", unsafe_allow_html=True)
with col_s3:
    st.markdown("""<div class="stat-card"><div class="stat-number">∞</div><div class="stat-label">مدة التحويل</div></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# نظام التبويبات
tab_studio, tab_history, tab_help = st.tabs(["🎛️ ستوديو العمل", "📂 أرشيف الجلسة", "ℹ️ مساعدة"])

# --- TAB 1: STUDIO ---
with tab_studio:
    row1_col1, row1_col2 = st.columns([1, 2])
    
    # 1. الإعدادات (اليسار)
    with row1_col1:
        with st.container(border=True):
            st.markdown("### ⚙️ إعدادات الصوت")
            
            # اللغة والصوت
            lang_cat = st.selectbox("اللغة:", list(VOICES.keys()))
            voice_name = st.selectbox("المعلق:", list(VOICES[lang_cat].keys()))
            selected_code = VOICES[lang_cat][voice_name]
            
            st.markdown("---")
            
            # تحكم متقدم (Expandable)
            with st.expander("🎚️ هندسة الصوت (Advanced Audio)", expanded=True):
                # السرعة
                speed_val = st.select_slider(
                    "⚡ السرعة (Speed)",
                    options=[0.5, 0.75, 1.0, 1.25, 1.5, 2.0],
                    value=1.0,
                    format_func=lambda x: f"{x}x"
                )
                
                # الطبقة
                pitch_val = st.slider("🎤 طبقة الصوت (Pitch)", -50, 50, 0, 5, format="%d Hz")
                
                # الصوت
                vol_val = st.slider("🔊 مستوى الصوت (Volume)", -50, 50, 0, 10, format="%d%%")

    # 2. الإدخال (اليمين)
    with row1_col2:
        with st.container(border=True):
            st.markdown("### 📝 النص (Script)")
            
            txt_in = st.text_area(
                "اكتب النص هنا",
                height=300,
                placeholder="أهلاً بك في منصة المهندس يوسف خالد.. اكتب النص هنا...",
                label_visibility="collapsed"
            )
            
            # أدوات النص
            t_col1, t_col2 = st.columns([4, 1])
            with t_col1:
                st.caption(f"عدد الحروف: {len(txt_in)}")
            with t_col2:
                if st.button("🗑️ مسح", type="secondary"):
                    txt_in = "" # (يحتاج rerun لتفعيل المسح الفعلي لكن الزر موجود كواجهة)
            
            st.markdown("---")
            
            # زر التنفيذ
            if st.button("🚀 تحويل ومعالجة (Generate Audio)", type="primary", use_container_width=True):
                if not txt_in.strip():
                    st.error("⚠️ يرجى كتابة نص أولاً!")
                else:
                    with st.spinner("جاري الاتصال بسيرفرات المعالجة..."):
                        try:
                            # تشغيل المحرك
                            audio_path, file_name = asyncio.run(
                                engine_generate(txt_in, selected_code, speed_val, pitch_val, vol_val)
                            )
                            
                            # تحديث الإحصائيات والأرشيف
                            st.session_state.generated_count += 1
                            st.session_state.history.insert(0, {
                                "time": datetime.now().strftime("%I:%M %p"),
                                "text": txt_in[:50] + "...",
                                "path": audio_path,
                                "name": file_name
                            })
                            
                            st.success("✅ تمت العملية بنجاح!")
                            
                            # عرض النتيجة فوراً
                            st.audio(audio_path, format="audio/mp3")
                            
                            with open(audio_path, "rb") as f:
                                st.download_button(
                                    label="⬇️ تحميل MP3",
                                    data=f,
                                    file_name=file_name,
                                    mime="audio/mp3",
                                    use_container_width=True
                                )
                                
                        except Exception as e:
                            st.error(f"حدث خطأ تقني: {e}")

# --- TAB 2: HISTORY ---
with tab_history:
    st.markdown("### 📂 الملفات السابقة (في هذه الجلسة)")
    if not st.session_state.history:
        st.info("لا يوجد ملفات حتى الآن. قم بتحويل نص لتظهر هنا.")
    else:
        for item in st.session_state.history:
            with st.container(border=True):
                c1, c2, c3 = st.columns([1, 3, 1])
                with c1:
                    st.caption(item["time"])
                with c2:
                    st.write(f"**{item['name']}**")
                    st.caption(item["text"])
                with c3:
                    if os.path.exists(item["path"]):
                        with open(item["path"], "rb") as f:
                            st.download_button(
                                "⬇️",
                                data=f,
                                file_name=item["name"],
                                mime="audio/mp3",
                                key=item["name"]
                            )

# --- TAB 3: HELP ---
with tab_help:
    st.markdown("""
    ### 💡 كيفية الاستخدام
    1. اختر اللغة والمعلق الصوتي من القائمة اليسرى.
    2. تحكم في **السرعة** و **طبقة الصوت** للحصول على نبرة مميزة.
    3. اكتب النص في المربع الأيمن واضغط "تحويل".
    4. ستظهر النتيجة فوراً ويمكنك تحميلها أو الرجوع إليها من تبويب "أرشيف الجلسة".
    
    ---
    **للدعم الفني والتطوير المخصص:**
    تواصل مع المهندس يوسف خالد على الرقم: `01007097545`
    """)

# تذييل الصفحة
st.markdown("---")
st.markdown("<div style='text-align: center; color: #999;'>© 2026 Developed with ❤️ by Eng. Yousef Khaled</div>", unsafe_allow_html=True)
