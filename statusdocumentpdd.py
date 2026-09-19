import random
import time
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
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🌈 แบบฝึกหัดเตรียมสอบอนุบาล (28 ก.ย. - 2 ต.ค. 69)")

tab1, tab2 = st.tabs(["🇹🇭 วิชาภาษาไทย", "🔢 วิชาคณิตศาสตร์"])

# ==========================================
# 1. หมวดวิชาภาษาไทย (ครบทั้ง 44 พยัญชนะ)
# ==========================================
with tab1:
    # คลังข้อมูล 44 พยัญชนะไทยพร้อมรูปภาพประจำตัวอักษร
    THAI_DICT = {
        "ก": ("ไก่", "🐔"),
        "ข": ("ไข่", "🥚"),
        "ฃ": ("ขวด", "🍾"),
        "ค": ("ควาย", "🐃"),
        "ฅ": ("คน", "🧑"),
        "ฆ": ("ระฆัง", "🔔"),
        "ง": ("งู", "🐍"),
        "จ": ("จาน", "🍽️"),
        "ฉ": ("ฉิ่ง", "🥁"),
        "ช": ("ช้าง", "🐘"),
        "ซ": ("โซ่", "⛓️"),
        "ฌ": ("เฌอ (ต้นไม้)", "🌳"),
        "ญ": ("หญิง", "👧"),
        "ฎ": ("ชฎา", "👑"),
        "ฏ": ("ปฏัก", "🦯"),
        "ฐ": ("ฐาน", "🧱"),
        "ฑ": ("มณโฑ", "👸"),
        "ฒ": ("ผู้เฒ่า", "👴"),
        "ณ": ("เณร", "🧑‍อุปสมบท"),
        "ด": ("เด็ก", "👶"),
        "ต": ("เต่า", "🐢"),
        "ถ": ("ถุง", "🛍️"),
        "ท": ("ทหาร", "💂"),
        "ธ": ("ธง", "🇹🇭"),
        "น": ("หนู", "กวด"),
        "บ": ("ใบไม้", "🍃"),
        "ป": ("ปลา", "🐟"),
        "ผ": ("ผึ้ง", "🐝"),
        "ฝ": ("ฝา", "🥫"),
        "พ": ("พาน", "🪷"),
        "ฟ": ("ฟัน", "🦷"),
        "ภ": ("สำเภา", "⛵"),
        "ม": ("ม้า", "🐴"),
        "ย": ("ยักษ์", "👹"),
        "ร": ("เรือ", "🛶"),
        "ล": ("ลิง", "🐒"),
        "ว": ("แหวน", "💍"),
        "ศ": ("ศาลา", "🏯"),
        "ษ": ("ฤาษี", "🧙"),
        "ส": ("เสือ", "🐯"),
        "ห": ("หีบ", "📦"),
        "ฬ": ("จุฬา (ว่าว)", "🪁"),
        "อ": ("อ่าง", "🛁"),
        "ฮ": ("นกฮูก", "🦉"),
    }

    if "thai_stage" not in st.session_state:
        st.session_state.thai_stage = 1
    if "thai_score" not in st.session_state:
        st.session_state.thai_score = 0
    if "current_q_letter" not in st.session_state:
        st.session_state.current_q_letter = "ก"

    st.caption(f"🏆 ภาษาไทย: ด่านที่ {st.session_state.thai_stage} / 2")

    # --- ด่านที่ 1: บัตรภาพ ก-ฮ (ทายเสียงอ่าน) ---
    if st.session_state.thai_stage == 1:
        st.subheader("ด่านที่ 1: บอกพยัญชนะไทย (ก - ฮ)")
        st.write("ครู/ผู้ปกครองแสดงบัตรตัวอักษรให้เด็กๆ ตอบเสียงอ่าน")

        if "flash_letter" not in st.session_state:
            st.session_state.flash_letter = "ก"

        st.markdown(
            f"<div class='giant-text'>{st.session_state.flash_letter}</div>",
            unsafe_allow_html=True,
        )

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🎲 สุ่มอักษรใหม่"):
                st.session_state.flash_letter = random.choice(
                    list(THAI_DICT.keys())
                )
                st.rerun()
        with col_b:
            if st.button("ไปด่านจับคู่ 44 ตัว ➡️", type="primary"):
                st.session_state.thai_stage = 2
                st.rerun()

    # --- ด่านที่ 2: จับคู่พยัญชนะกับรูปภาพ สุ่มครบทั่วทั้ง 44 พยัญชนะ ---
    elif st.session_state.thai_stage == 2:
        st.subheader("ด่านที่ 2: จับคู่พยัญชนะกับรูปภาพ (สุ่มครบ 44 ตัว)")

        st.progress(
            min(st.session_state.thai_score / 44, 1.0),
            text=f"สะสมคำตอบถูกต้อง: {st.session_state.thai_score} / 44 ตัว",
        )

        target = st.session_state.current_q_letter
        correct_name, correct_emoji = THAI_DICT[target]

        st.markdown(
            f"<h2 style='text-align: center;'>รูปภาพไหนตรงกับพยัญชนะ: <span style='color: #FF3D00; font-size: 60px;'>'{target}'</span> ?</h2>",
            unsafe_allow_html=True,
        )

        # สร้างตัวเลือกหลอกอีก 2 ตัวเลือกที่ไม่ซ้ำกัน
        other_letters = [k for k in THAI_DICT.keys() if k != target]
        wrong_samples = random.sample(other_letters, 2)

        options = [
            (target, correct_name, correct_emoji),
            (
                wrong_samples[0],
                THAI_DICT[wrong_samples[0]][0],
                THAI_DICT[wrong_samples[0]][1],
            ),
            (
                wrong_samples[1],
                THAI_DICT[wrong_samples[1]][0],
                THAI_DICT[wrong_samples[1]][1],
            ),
        ]

        # สุ่มลำดับตัวเลือกเฉพาะในครั้งแรกของข้อนั้น
        if "shuffled_options" not in st.session_state:
            st.session_state.shuffled_options = options.copy()
            random.shuffle(st.session_state.shuffled_options)

        cols = st.columns(3)
        for idx, (letter, name, emoji) in enumerate(
            st.session_state.shuffled_options
        ):
            with cols[idx]:
                btn_text = f"{emoji} {name}"
                if st.button(btn_text, key=f"btn_{letter}", use_container_width=True):
                    if letter == target:
                        st.balloons()
                        st.success(
                            f"🎉 ถูกต้องครับ! {target} - {name} กำลังไปข้อถัดไป..."
                        )
                        st.session_state.thai_score += 1
                        # สุ่มพยัญชนะตัวใหม่สำหรับข้อถัดไป
                        st.session_state.current_q_letter = random.choice(
                            list(THAI_DICT.keys())
                        )
                        if "shuffled_options" in st.session_state:
                            del st.session_state.shuffled_options
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.error(
                            f"❌ ยังไม่ใช่ครับ! อันนี้คือ {letter} - {name} ลองใหม่นะ"
                        )

        st.write("")
        if st.button("🔄 เริ่มสุ่มคำถามใหม่"):
            st.session_state.current_q_letter = random.choice(
                list(THAI_DICT.keys())
            )
            if "shuffled_options" in st.session_state:
                del st.session_state.shuffled_options
            st.rerun()


# ==========================================
# 2. หมวดวิชาคณิตศาสตร์ (ผ่านทีละข้อ)
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
                st.success("🎉 เก่งมาก! ๓ เท่ากับ 3 กำลังไปข้อถัดไป...")
                time.sleep(1.5)
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
                st.success("🎉 ถูกต้อง! ๕ เท่ากับ 5 กำลังไปข้อถัดไป...")
                time.sleep(1.5)
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
                st.success("🎉 ถูกต้อง! มีส้ม 6 ผล กำลังไปข้อถัดไป...")
                time.sleep(1.5)
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
                st.success("🎉 ถูกต้องครับ! กำลังไปด่านสุดท้าย...")
                time.sleep(1.5)
                st.session_state.math_stage = 5
                st.rerun()
        with col_b:
            if st.button("✏️ ดินสอสั้น", use_container_width=True):
                st.error("❌ อันนี้สั้นกว่าครับ")

    # --- ด่านที่ 5: เปรียบเทียบ สูง - เตี้ย ---
    elif st.session_state.math_stage == 5:
        st.subheader("ด่านที่ 5: เปรียบเทียบขนาด (สูง - เตี้ย)")
        st.write("สัตว์ตัวไหน **'สูง'** กว่ากัน?")

        col_c, col_d = st.columns(2)
        with col_c:
            if st.button("🦒 ยีราฟสูง", use_container_width=True):
                st.balloons()
                st.success("🎉 เก่งมาก! ตอบถูกครบทุกด่านแล้วครับ 🏆")
        with col_d:
            if st.button("🐧 เพนกวินเตี้ย", use_container_width=True):
                st.error("❌ เพนกวินตัวเตี้ยกว่าครับ")

        if st.button("🔄 เริ่มเล่นคณิตศาสตร์ใหม่", type="primary"):
            st.session_state.math_stage = 1
            st.rerun()
