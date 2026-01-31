import streamlit as st
import edge_tts
import asyncio
import tempfile
import os

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="Eng. Yousef Voice Studio",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. حقن CSS (تصميم احترافي + خط عربي + ألوان البراند)
st.markdown("""
<style>
    /* استيراد خط Cairo من جوجل */
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }
    
    /* تصميم الهيدر الرئيسي */
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* تصميم الأزرار */
    .stButton>button {
        width: 100%;
        background-color: #ff4b4b;
        color: white;
        border-radius: 8px;
        height: 55px;
        font-size: 18px;
        font-weight: bold;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #d43f3f;
        transform: scale(1.02);
    }
    
    /* تصميم الشريط الجانبي */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-left: 1px solid #ddd;
    }
    
    /* كارت المعلومات في السايد بار */
    .profile-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        text-align: center;
    }
    
    /* زر الواتساب */
    .whatsapp-btn {
        background-color: #25D366;
        color: white !important;
        padding: 12px 20px;
        border-radius: 50px;
        text-decoration: none;
        font-weight: bold;
        display: block;
        text-align: center;
        margin-top: 10px;
        box-shadow: 0 4px 6px rgba(37, 211, 102, 0.3);
        transition: transform 0.2s;
    }
    .whatsapp-btn:hover {
        transform: scale(1.05);
    }
    
    /* التذييل (Footer) */
    .footer {
        text-align: center;
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid #eee;
        color: #666;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# 3. قائمة الأصوات
VOICES = {
    "🇪🇬 مصر - شاكر (رسمي/إخباري)": "ar-EG-ShakirNeural",
    "🇪🇬 مصر - سلمى (إعلاني/ودود)": "ar-EG-SalmaNeural",
    "🇸🇦 السعودية - حامد (وقور)": "ar-SA-HamedNeural",
    "🇸🇦 السعودية - زارية (تفاعلي)": "ar-SA-ZariyahNeural",
    "🇦🇪 الإمارات - حمد": "ar-AE-HamdanNeural",
    "🇺🇸 English - US - Guy": "en-US-GuyNeural",
    "🇺🇸 English - US - Aria": "en-US-AriaNeural",
    "🇬🇧 English - UK - Ryan": "en-GB-RyanNeural",
}

# 4. دالة المعالجة
async def generate_audio(text, voice_key, rate_value):
    voice_code = VOICES[voice_key]
    rate_str = f"{rate_value:+d}%"
    communicate = edge_tts.Communicate(text, voice_code, rate=rate_str)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        await communicate.save(tmp_file.name)
        return tmp_file.name

# --- 5. الشريط الجانبي (بروفايل المهندس يوسف) ---
with st.sidebar:
    # صورة بروفايل (افتراضية أو رابط صورتك)
    st.markdown("""
        <div class="profile-card">
            <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" width="80" style="margin-bottom: 10px;">
            <h3 style="margin:0; color:#333;">المهندس / يوسف خالد</h3>
            <p style="color:#777; font-size:14px;">Software Engineer & Graphic Designer</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🚀 خدماتي وأعمالي")
    st.info("💻 **تطوير برمجيات ومواقع:** تصميم مواقع ويب، سكربتات بايثون، حلول AI.")
    st.success("🎨 **تصميم جرافيك:** هويات بصرية، إعلانات سوشيال ميديا (Verno, Moga Travel).")
    st.warning("✈️ **كوين ترافيل (Queen Travel):** خدمات السياحة وتأجير السيارات.")
    st.error("👗 **براند حور (Hoor):** أحدث صيحات الموضة والملابس.")

    st.markdown("---")
    st.markdown("### 📞 تواصل معي")
    st.markdown("**رقم الهاتف:** `01007097545`")
    
    # زر واتساب احترافي
    whatsapp_url = "https://wa.me/201007097545"
    st.markdown(f"""
    <a href="{whatsapp_url}" target="_blank" class="whatsapp-btn">
        <i class="fab fa-whatsapp"></i> تواصل عبر واتساب فوراً
    </a>
    """, unsafe_allow_html=True)

# --- 6. المنطقة الرئيسية ---

# هيدر مخصص
st.markdown("""
<div class="main-header">
    <h1>🎙️ ستوديو المهندس يوسف خالد الصوتي</h1>
    <p>Eng. Yousef Khaled Voice Over Studio</p>
</div>
""", unsafe_allow_html=True)

st.write("حول نصوصك إلى تعليق صوتي احترافي (AI) لاستخدامه في الفيديوهات، الإعلانات، والمشاريع التعليمية.")

# تقسيم الشاشة
col1, col2 = st.columns([2, 1])

with col2:
    with st.container(border=True):
        st.markdown("### 🎛️ لوحة التحكم")
        selected_voice = st.selectbox("اختر المعلق الصوتي:", list(VOICES.keys()))
        
        st.markdown("---")
        st.markdown("**⚡ سرعة الصوت:**")
        speed = st.slider("", min_value=-50, max_value=100, value=0, step=10, format="%d%%")
        
        if speed == 0:
            st.caption("الوضع الطبيعي (1x)")
        elif speed > 0:
            st.caption("تسريع")
        else:
            st.caption("تبطيء")

with col1:
    with st.container(border=True):
        st.markdown("### 📝 النص المراد تحويله")
        text_input = st.text_area("", height=280, placeholder="اكتب النص هنا... مثال: أهلاً بكم في شركة كوين ترافيل للسياحة...")
        
        generate_btn = st.button("🚀 تحويل النص إلى صوت (Generate)")

# منطقة النتائج
if generate_btn:
    if text_input:
        st.markdown("---")
        st.markdown("### 🎧 النتيجة النهائية")
        with st.spinner("جاري المعالجة باستخدام سيرفرات الذكاء الاصطناعي..."):
            try:
                output_file = asyncio.run(generate_audio(text_input, selected_voice, speed))
                
                # عرض مشغل الصوت وزر التحميل بجانب بعض
                res_col1, res_col2 = st.columns([3, 1])
                with res_col1:
                    st.audio(output_file, format="audio/mp3")
                with res_col2:
                    with open(output_file, "rb") as file:
                        st.download_button(
                            label="⬇️ تحميل MP3",
                            data=file,
                            file_name="Eng_Yousef_Studio_Output.mp3",
                            mime="audio/mp3",
                            use_container_width=True
                        )
                st.success("تمت العملية بنجاح! ✅")
            except Exception as e:
                st.error(f"عذراً، حدث خطأ: {e}")
    else:
        st.warning("⚠️ من فضلك اكتب نصاً أولاً.")

# --- 7. التذييل (Footer) ---
st.markdown("""
<div class="footer">
    <p>جميع الحقوق محفوظة © 2026 - تم التطوير بواسطة <b>المهندس يوسف خالد</b></p>
    <p>📞 01007097545 | 🌐 Queen Travel | 👗 Hoor Brand</p>
</div>
""", unsafe_allow_html=True)
