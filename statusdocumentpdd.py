import random
import streamlit as st

st.set_page_config(
    page_title="แบบฝึกหัดเตรียมสอบอนุบาล", page_icon="🎨", layout="centered"
)

# Custom CSS: ปรับสีพื้นหลังธีมเด็กสดใส + ขยายขนาดปุ่มและไอคอน
st.markdown(
    """
    <style>
    /* พื้นหลังการ์ตูนโทนสดใส (ไล่สีพาสเทล เหลือง-ชมพู-ฟ้า) */
    .stApp {
        background: linear-gradient(135deg, #FFFDE7 0%, #FFF0F5 50%, #E0F7FA 100%);
    }

    /* ปรับแต่งปุ่มให้ใหญ่ โค้งมน สีสดใส และมีมิติ */
    .stButton > button {
        font-size: 32px !important;
        font-weight: bold !important;
        padding: 20px 30px !important;
        border-radius: 25px !important;
        background-color: #FF6F61 !important;
        color: white !important;
        border: 4px solid #FFFFFF !important;
        box-shadow: 0px 6px 15px rgba(0,0,0,0.15) !important;
        transition: transform 0.2s !important;
    }
    
    /* เอฟเฟกต์เมื่อกดปุ่ม */
    .stButton > button:active {
        transform: scale(0.95) !important;
    }

    /* ปรับขนาดตัวหนังสือข้อสอบ/ตัวอักษรใหญ่ยักษ์ */
    .giant-text {
        font-size: 160px !important;
        font-weight: 900;
        text-align: center;
        color: #FF3D00;
        text-shadow: 4px 4px 0px #FFD600;
        margin: 10px 0;
    }

    /* ปรับขนาดตัวเลือกอีโมจิให้ใหญ่เป็นพิเศษ */
    .emoji-box {
        font-size: 80px !important;
        text-align: center;
        margin: 15px 0;
    }

    /* ปรับแต่งแท็บให้ใหญ่และน่ารัก */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 24px !important;
        font-weight: bold !important;
        border-radius: 15px !important;
        padding: 10px 20px !important;
        background-color: #FFFFFF !important;
        box-shadow: 0px 4px 8px rgba(0,0,0,0.05) !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🌈 แบบฝึกหัดเตรียมสอบอนุบาล (28 ก.ย. - 2 ต.ค. 69)")[span_0](start_span)[span_0](end_span)

tab1, tab2 = st.tabs(["🇹🇭 วิชาภาษาไทย", "🔢 วิชาคณิตศาสตร์"])

# ==========================================
# 1. หมวดวิชาภาษาไทย
# ==========================================
with tab1:
    st.header("🇹🇭 วิชาภาษาไทย")

    # 1.1 ทายพยัญชนะ ก-ฮ (ไม่มีภาพ)
    st.subheader("1. บอกพยัญชนะไทย (ก - ฮ)")[span_1](start_span)[span_1](end_span)
    st.caption("ครู/ผู้ปกครองแสดงบัตรตัวอักษรแล้วให้เด็กๆ ตอบเสียงอ่าน")[span_2](start_span)[span_2](end_span)

    thai_letters = [
        "ก",
        "ข",
        "ฃ",
        "ค",
        "ฅ",
        "ฆ",
        "ง",
        "จ",
        "ฉ",
        "ช",
        "ซ",
        "ฌ",
        "ญ",
        "ฎ",
        "ฏ",
        "ฐ",
        "ฑ",
        "ฒ",
        "ณ",
        "ด",
        "ต",
        "ถ",
        "ท",
        "ธ",
        "น",
        "บ",
        "ป",
        "ผ",
        "ฝ",
        "พ",
        "ฟ",
        "ภ",
        "ม",
        "ย",
        "ร",
        "ล",
        "ว",
        "ศ",
        "ษ",
        "ส",
        "ห",
        "ฬ",
        "อ",
        "ฮ",
    ][span_3](start_span)[span_3](end_span)

    if "current_letter" not in st.session_state:
        st.session_state.current_letter = "ก"

    if st.button("🎲 สุ่มพยัญชนะใหม่", type="primary"):
        st.session_state.current_letter = random.choice(thai_letters)

    # แสดงพยัญชนะขนาดใหญ่ยักษ์
    st.markdown(
        f"<div class='giant-text'>{st.session_state.current_letter}</div>",
        unsafe_allow_html=True,
    )

    st.divider()

    # 1.2 จับคู่พยัญชนะกับรูปภาพ
    st.subheader("2. จับคู่พยัญชนะกับรูปภาพ")[span_4](start_span)[span_4](end_span)
    st.write("เลือกรูปภาพให้ตรงกับตัวอักษร **'ก'**")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🐔 ไก่", use_container_width=True):
            st.balloons()
            st.success("🎉 ถูกต้องครับ! ก - ไก่")
    with col2:
        if st.button("🥚 ไข่", use_container_width=True):
            st.error("❌ อันนี้ ข.ไข่ ครับ ลองใหม่นะ")
    with col3:
        if st.button("🐃 ควาย", use_container_width=True):
            st.error("❌ อันนี้ ค.ควาย ครับ ลองใหม่นะ")

# ==========================================
# 2. หมวดวิชาคณิตศาสตร์
# ==========================================
with tab2:
    st.header("🔢 วิชาคณิตศาสตร์")

    # 2.1 จับคู่เลขไทย-อารบิก
    st.subheader("1. จับคู่เลขไทย (๑-๕) กับ เลขอารบิก (1-5)")[span_5](start_span)[span_5](end_span)
    st.write("เลขไทย **'๓'** ตรงกับเลขอารบิกตัวไหน?")[span_6](start_span)[span_6](end_span)

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        if st.button("1"):
            st.error("ยังไม่ใช่ครับ")
    with c2:
        if st.button("2"):
            st.error("ยังไม่ใช่ครับ")
    with c3:
        if st.button("3"):
            st.balloons()
            st.success("🎉 เก่งมาก! ๓ เท่ากับ 3")[span_7](start_span)[span_7](end_span)
    with c4:
        if st.button("4"):
            st.error("ยังไม่ใช่ครับ")
    with c5:
        if st.button("5"):
            st.error("ยังไม่ใช่ครับ")

    st.divider()

    # 2.2 นับจำนวนและเลือกตัวเลข 1-10
    st.subheader("2. นับจำนวนสิ่งของ (1-10)")[span_8](start_span)[span_8](end_span)
    st.write("นับส้มสิว่ามีกี่ผล? 🍊")
    st.markdown(
        "<div class='emoji-box'>🍊 🍊 🍊 🍊</div>", unsafe_allow_html=True
    )

    ans_num = st.radio(
        "เลือกคำตอบที่ถูกต้อง:",
        ["2 ผล", "4 ผล", "6 ผล"],
        horizontal=True,
    )
    if st.button("ตรวจคำตอบ"):
        if ans_num == "4 ผล":
            st.balloons()
            st.success("🎉 ถูกต้อง! มีส้ม 4 ผล")
        else:
            st.error("❌ ลองนับใหม่อีกทีนะ 1...2...3...4")

    st.divider()

    # 2.3 เปรียบเทียบขนาด
    st.subheader("3. เปรียบเทียบขนาด")[span_9](start_span)[span_9](end_span)

    # ข้อที่ 1: สั้น - ยาว
    st.write("📍 **ข้อ 1: สิ่งไหน 'ยาว' กว่ากัน?**")[span_10](start_span)[span_10](end_span)
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("✏️✏️✏️ ดินสอยาว", use_container_width=True):[span_11](start_span)[span_11](end_span)
            st.success("🎉 ถูกต้องครับ!")
    with col_b:
        if st.button("✏️ ดินสอสั้น", use_container_width=True):[span_12](start_span)[span_12](end_span)
            st.error("❌ อันนี้สั้นกว่าครับ")

    # ข้อที่ 2: สูง - เตี้ย
    st.write("📍 **ข้อ 2: สัตว์ตัวไหน 'สูง' กว่ากัน?**")[span_13](start_span)[span_13](end_span)
    col_c, col_d = st.columns(2)
    with col_c:
        if st.button("🦒 ยีราฟสูง", use_container_width=True):[span_14](start_span)[span_14](end_span)
            st.success("🎉 เก่งมาก! ยีราฟตัวสูง")[span_15](start_span)[span_15](end_span)
    with col_d:
        if st.button("🐧 เพนกวินเตี้ย", use_container_width=True):[span_16](start_span)[span_16](end_span)
            st.error("❌ เพนกวินตัวเตี้ยกว่าครับ")[span_17](start_span)[span_17](end_span)

    # ข้อที่ 3: เล็ก - ใหญ่
    st.write("📍 **ข้อ 3: สิ่งไหน 'เล็ก' กว่ากัน?**")[span_18](start_span)[span_18](end_span)
    col_e, col_f = st.columns(2)
    with col_e:
        if st.button("⚽ ฟุตบอลใหญ่", use_container_width=True):[span_19](start_span)[span_19](end_span)
            st.error("❌ ฟุตบอลลูกใหญ่กว่านะ")
    with col_f:
        if st.button("🎾 เทนนิสเล็ก", use_container_width=True):[span_20](start_span)[span_20](end_span)
            st.success("🎉 ถูกต้อง! ลูกเทนนิสเล็กกว่า")
