import random
import streamlit as st

st.set_page_config(
    page_title="เกมผ่านด่านอนุบาล 2", page_icon="🎮", layout="centered"
)

# Custom CSS: ตกแต่งสไตล์เกมการ์ตูน น่ารัก ปรับปุ่มใหญ่พิเศษ
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #FFFDE7 0%, #FFF0F5 50%, #E0F7FA 100%);
    }

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
    
    .stButton > button:active {
        transform: scale(0.95) !important;
    }

    .giant-text {
        font-size: 160px !important;
        font-weight: 900;
        text-align: center;
        color: #FF3D00;
        text-shadow: 4px 4px 0px #FFD600;
        margin: 10px 0;
    }

    .emoji-box {
        font-size: 90px !important;
        text-align: center;
        margin: 20px 0;
    }

    .stage-card {
        background-color: #FFFFFF;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🌈 แบบฝึกหัดเตรียมสอบอนุบาล (28 ก.ย. - 2 ต.ค. 69)")

tab1, tab2 = st.tabs(["🇹🇭 วิชาภาษาไทย", "🔢 วิชาคณิตศาสตร์"])

# ==========================================
# 1. หมวดวิชาภาษาไทย (ระบบผ่านด่านทีละข้อ)
# ==========================================
with tab1:
    if "thai_stage" not in st.session_state:
        st.session_state.thai_stage = 1

    st.caption(f"🏆 ภาษาไทย: ด่านที่ {st.session_state.thai_stage} / 3")

    # --- ด่านที่ 1: บัตรภาพ ก-ฮ ---
    if st.session_state.thai_stage == 1:
        st.subheader("ด่านที่ 1: บอกพยัญชนะไทย (ก - ฮ)")
        st.write("ครู/ผู้ปกครองแสดงบัตรตัวอักษรให้เด็กๆ ตอบเสียงอ่าน")

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

        st.markdown(
            f"<div class='giant-text'>{st.session_state.current_letter}</div>",
            unsafe_allow_html=True,
        )

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🎲 สุ่มอักษรใหม่"):
                st.session_state.current_letter = random.choice(thai_letters)
                st.rerun()
        with col_b:
            if st.button("ผ่านด่านนี้ ➡️", type="primary"):
                st.session_state.thai_stage = 2
                st.rerun()

    # --- ด่านที่ 2: จับคู่พยัญชนะกับรูปภาพ (ก - ไก่) ---
    elif st.session_state.thai_stage == 2:
        st.subheader("ด่านที่ 2: จับคู่พยัญชนะกับรูปภาพ")
        st.write("ข้อใดตรงกับตัวอักษร **'ก'**?")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🐔 ไก่", use_container_width=True):
                st.balloons()
                st.success("🎉 ถูกต้องครับ! ก - ไก่")
                if st.button("ไปด่านต่อไป ➡️", type="primary"):
                    st.session_state.thai_stage = 3
                    st.rerun()
        with col2:
            if st.button("🥚 ไข่", use_container_width=True):
                st.error("❌ อันนี้ ข.ไข่ ครับ ลองใหม่นะ")
        with col3:
            if st.button("🐃 ควาย", use_container_width=True):
                st.error("❌ อันนี้ ค.ควาย ครับ ลองใหม่นะ")

    # --- ด่านที่ 3: จับคู่พยัญชนะกับรูปภาพ (ม - ม้า) ---
    elif st.session_state.thai_stage == 3:
        st.subheader("ด่านที่ 3: จับคู่พยัญชนะกับรูปภาพ")
        st.write("ข้อใดตรงกับตัวอักษร **'ม'**?")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🐴 ม้า", use_container_width=True):
                st.balloons()
                st.success("🎉 เก่งมากเลย! ผ่านด่านภาษาไทยครบแล้ว")
                if st.button("🔄 เล่นใหม่อีกครั้ง"):
                    st.session_state.thai_stage = 1
                    st.rerun()
        with col2:
            if st.button("🐘 ช้าง", use_container_width=True):
                st.error("❌ อันนี้ ช.ช้าง ครับ")
        with col3:
            if st.button("🐟 ปลา", use_container_width=True):
                st.error("❌ อันนี้ ป.ปลา ครับ")


# ==========================================
# 2. หมวดวิชาคณิตศาสตร์ (ระบบผ่านด่านทีละข้อ)
# ==========================================
with tab2:
    if "math_stage" not in st.session_state:
        st.session_state.math_stage = 1

    st.caption(f"🏆 คณิตศาสตร์: ด่านที่ {st.session_state.math_stage} / 5")

    # --- ด่านที่ 1: จับคู่เลขไทย-อารบิก (๓) ---
    if st.session_state.math_stage == 1:
        st.subheader("ด่านที่ 1: จับคู่เลขไทย ๑-๕ กับ เลขอารบิก 1-5")
        st.write("เลขไทย **'๓'** ตรงกับเลขอารบิกตัวไหน?")

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
                st.success("🎉 เก่งมาก! ๓ เท่ากับ 3")
                if st.button("ไปข้อถัดไป ➡️", type="primary"):
                    st.session_state.math_stage = 2
                    st.rerun()
        with c4:
            if st.button("4"):
                st.error("ยังไม่ใช่ครับ")
        with c5:
            if st.button("5"):
                st.error("ยังไม่ใช่ครับ")

    # --- ด่านที่ 2: จับคู่เลขไทย-อารบิก (๕) ---
    elif st.session_state.math_stage == 2:
        st.subheader("ด่านที่ 2: จับคู่เลขไทย ๑-๕ กับ เลขอารบิก 1-5")
        st.write("เลขไทย **'๕'** ตรงกับเลขอารบิกตัวไหน?")

        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            if st.button("1 "):
                st.error("ยังไม่ใช่ครับ")
        with c2:
            if st.button("2 "):
                st.error("ยังไม่ใช่ครับ")
        with c3:
            if st.button("4 "):
                st.error("ยังไม่ใช่ครับ")
        with c4:
            if st.button("5 "):
                st.balloons()
                st.success("🎉 ถูกต้อง! ๕ เท่ากับ 5")
                if st.button("ไปข้อถัดไป ➡️", type="primary"):
                    st.session_state.math_stage = 3
                    st.rerun()
        with c5:
            if st.button("3 "):
                st.error("ยังไม่ใช่ครับ")

    # --- ด่านที่ 3: นับจำนวนส้ม (1-10) ---
    elif st.session_state.math_stage == 3:
        st.subheader("ด่านที่ 3: นับจำนวนสิ่งของ (1-10)")
        st.write("นับส้มสิว่ามีกี่ผล? 🍊")
        st.markdown(
            "<div class='emoji-box'>🍊 🍊 🍊 🍊 🍊 🍊</div>",
            unsafe_allow_html=True,
        )

        col_x, col_y, col_z = st.columns(3)
        with col_x:
            if st.button("4 ผล", use_container_width=True):
                st.error("❌ ลองนับใหม่อีกทีนะ")
        with col_y:
            if st.button("6 ผล", use_container_width=True):
                st.balloons()
                st.success("🎉 ถูกต้อง! มีส้ม 6 ผล")
                if st.button("ไปข้อถัดไป ➡️", type="primary"):
                    st.session_state.math_stage = 4
                    st.rerun()
        with col_z:
            if st.button("8 ผล", use_container_width=True):
                st.error("❌ ลองนับใหม่อีกทีนะ")

    # --- ด่านที่ 4: เปรียบเทียบ สั้น - ยาว ---
    elif st.session_state.math_stage == 4:
        st.subheader("ด่านที่ 4: เปรียบเทียบขนาด (สั้น - ยาว)")
        st.write("สิ่งไหน **'ยาว'** กว่ากัน?")

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("✏️✏️✏️ ดินสอยาว", use_container_width=True):
                st.balloons()
                st.success("🎉 ถูกต้องครับ!")
                if st.button("ไปด่านสุดท้าย ➡️", type="primary"):
                    st.session_state.math_stage = 5
                    st.rerun()
        with col_b:
            if st.button("✏️ ดินสอสั้น", use_container_width=True):
                st.error("❌ อันนี้สั้นกว่าครับ")

    # --- ด่านที่ 5: เปรียบเทียบ สูง - เตี้ย / เล็ก - ใหญ่ ---
    elif st.session_state.math_stage == 5:
        st.subheader("ด่านที่ 5: เปรียบเทียบขนาด (สูง - เตี้ย)")
        st.write("สัตว์ตัวไหน **'สูง'** กว่ากัน?")

        col_c, col_d = st.columns(2)
        with col_c:
            if st.button("🦒 ยีราฟสูง", use_container_width=True):
                st.balloons()
                st.success("🎉 เก่งมาก! ตอบถูกครบทุกด่านแล้วครับ 🏆")
                if st.button("🔄 เริ่มเล่นคณิตศาสตร์ใหม่"):
                    st.session_state.math_stage = 1
                    st.rerun()
        with col_d:
            if st.button("🐧 เพนกวินเตี้ย", use_container_width=True):
                st.error("❌ เพนกวินตัวเตี้ยกว่าครับ")
