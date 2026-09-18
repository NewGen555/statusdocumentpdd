import random
import streamlit as st

st.set_page_config(
    page_title="แบบฝึกหัดเตรียมสอบอนุบาล", page_icon="🎈", layout="centered"
)

# ตกแต่ง CSS ให้ปุ่มและตัวหนังสือใหญ่เหมาะกับเด็กอนุบาลบน iPad
st.markdown(
    """
    <style>
    .stButton>button {
        font-size: 24px !important;
        padding: 15px 25px !important;
        border-radius: 15px !important;
    }
    .big-text {
        font-size: 110px !important;
        font-weight: bold;
        text-align: center;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🎈 แบบฝึกหัดเตรียมความพร้อมอนุบาล (28 ก.ย. - 2 ต.ค. 69)")

tab1, tab2 = st.tabs(["🇹🇭 วิชาภาษาไทย", "🔢 วิชาคณิตศาสตร์"])

# ==========================================
# 1. หมวดวิชาภาษาไทย
# ==========================================
with tab1:
    st.header("🇹🇭 วิชาภาษาไทย")

    # 1.1 ทายพยัญชนะ ก-ฮ (ไม่มีภาพ)
    st.subheader("1. บอกพยัญชนะไทย (ก - ฮ)")
    st.caption("ครู/ผู้ปกครองแสดงบัตรตัวอักษรแล้วให้เด็กๆ ตอบเสียงอ่าน")

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
    ]

    if "current_letter" not in st.session_state:
        st.session_state.current_letter = "ก"

    if st.button("🎲 เปลี่ยนตัวอักษรใหม่", type="primary"):
        st.session_state.current_letter = random.choice(thai_letters)

    st.markdown(
        f"<div class='big-text' style='color: #FF5722;'>{st.session_state.current_letter}</div>",
        unsafe_allow_html=True,
    )

    st.divider()

    # 1.2 โยงเส้นจับคู่พยัญชนะกับรูปภาพ
    st.subheader("2. จับคู่พยัญชนะกับรูปภาพ")
    st.write("โจทย์: เลือกรูปภาพให้ตรงกับตัวอักษร **'ก'**")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🐔 ไก่", use_container_width=True):
            st.balloons()
            st.success("🎉 ถูกต้องครับ! ก - ไก่")
    with col2:
        if st.button("ไข่ 🥚", use_container_width=True):
            st.error("❌ อันนี้ ข.ไข่ ครับ ลองใหม่นะ")
    with col3:
        if st.button("ควาย 🐃", use_container_width=True):
            st.error("❌ อันนี้ ค.ควาย ครับ ลองใหม่นะ")

# ==========================================
# 2. หมวดวิชาคณิตศาสตร์
# ==========================================
with tab2:
    st.header("🔢 วิชาคณิตศาสตร์")

    # 2.1 จับคู่เลขไทย-อารบิก
    st.subheader("1. จับคู่เลขไทย (๑-๕) กับ เลขอารบิก (1-5)")
    st.write("โจทย์: เลขไทย **'๓'** ตรงกับเลขอารบิกตัวไหน?")

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        if st.button("1"):
            st.error("ยังไม่ใช่ครับ")
    with c2:
        if st.button("2"):
            st.error("ยังไม่ใช่ครับ")
    with c3:
        if st.button("3", type="primary"):
            st.balloons()
            st.success("🎉 เก่งมาก! ๓ เท่ากับ 3")
    with c4:
        if st.button("4"):
            st.error("ยังไม่ใช่ครับ")
    with c5:
        if st.button("5"):
            st.error("ยังไม่ใช่ครับ")

    st.divider()

    # 2.2 นับจำนวนและเลือกตัวเลข 1-10
    st.subheader("2. นับจำนวนสิ่งของ (1-10)")
    st.write("ลองนับดูสิว่ามีส้มกี่ผล? 🍊")
    st.markdown(
        "<h2 style='text-align: center;'>🍊 🍊 🍊 🍊</h2>", unsafe_allow_html=True
    )

    ans_num = st.radio(
        "เลือกคำตอบที่ถูกต้อง:",
        ["2 ผล", "4 ผล", "6 ผล"],
        horizontal=True,
    )
    if st.button("ตรวจคำตอบการนับ"):
        if ans_num == "4 ผล":
            st.balloons()
            st.success("🎉 ถูกต้อง! มีส้ม 4 ผล")
        else:
            st.error("❌ ลองนับใหม่อีกทีนะ 1...2...3...4")

    st.divider()

    # 2.3 เปรียบเทียบขนาด
    st.subheader("3. เปรียบเทียบขนาดและทางกายภาพ")

    # ข้อที่ 1: สั้น - ยาว
    st.write("📍 **ข้อ 1: สิ่งไหน 'ยาว' กว่ากัน?**")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("✏️✏️✏️ ดินสอยาว", use_container_width=True):
            st.success("🎉 ถูกต้องครับ!")
    with col_b:
        if st.button("✏️ ดินสอสั้น", use_container_width=True):
            st.error("❌ อันนี้สั้นกว่าครับ")

    # ข้อที่ 2: สูง - เตี้ย
    st.write("📍 **ข้อ 2: สัตว์ตัวไหน 'สูง' กว่ากัน?**")
    col_c, col_d = st.columns(2)
    with col_c:
        if st.button("🦒 ยีราฟ", use_container_width=True):
            st.success("🎉 เก่งมาก! ยีราฟตัวสูง")
    with col_d:
        if st.button("เพนกวิน 🐧", use_container_width=True):
            st.error("❌ เพนกวินตัวเตี้ยกว่าครับ")

    # ข้อที่ 3: เล็ก - ใหญ่
    st.write("📍 **ข้อ 3: สิ่งไหน 'เล็ก' กว่ากัน?**")
    col_e, col_f = st.columns(2)
    with col_e:
        if st.button("⚽ ลูกฟุตบอลใหญ่", use_container_width=True):
            st.error("❌ ฟุตบอลลูกใหญ่กว่านะ")
    with col_f:
        if st.button("เทนนิส 🎾", use_container_width=True):
            st.success("🎉 ถูกต้อง! ลูกเทนนิสเล็กกว่า")
