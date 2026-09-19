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
        font-size: 80px !important;
        text-align: center;
        margin: 20px 0;
        line-height: 1.3;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🌈 แบบฝึกหัดเตรียมสอบอนุบาล (28 ก.ย. - 2 ต.ค. 69)")

tab1, tab2, tab3 = st.tabs(["🇹🇭 วิชาภาษาไทย", "🔢 วิชาคณิตศาสตร์ (1-10)", "🔤 วิชาภาษาอังกฤษ (A-Z)"])

# ==========================================
# 1. หมวดวิชาภาษาไทย (ครบทั้ง 44 พยัญชนะ)
# ==========================================
with tab1:
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
        "ฌ": ("เฌอ", "🌳"),
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
        "น": ("หนู", "🐭"),
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
        "ฬ": ("จุฬา", "🪁"),
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

        if "shuffled_options" not in st.session_state:
            st.session_state.shuffled_options = options.copy()
            random.shuffle(st.session_state.shuffled_options)

        cols = st.columns(3)
        for idx, (letter, name, emoji) in enumerate(
            st.session_state.shuffled_options
        ):
            with cols[idx]:
                btn_text = f"{emoji} {name}"
                if st.button(
                    btn_text, key=f"btn_th_{letter}", use_container_width=True
                ):
                    if letter == target:
                        st.balloons()
                        st.success(
                            f"🎉 ถูกต้องครับ! {target} - {name} กำลังไปข้อถัดไป..."
                        )
                        st.session_state.thai_score += 1
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
        if st.button("🔄 สุ่มโจทย์พยัญชนะใหม่"):
            st.session_state.current_q_letter = random.choice(
                list(THAI_DICT.keys())
            )
            if "shuffled_options" in st.session_state:
                del st.session_state.shuffled_options
            st.rerun()


# ==========================================
# 2. หมวดวิชาคณิตศาสตร์ (แยก 3 หมวดย่อย 1-10)
# ==========================================
with tab2:
    NUM_MAPPING = {
        1: "๑",
        2: "๒",
        3: "๓",
        4: "๔",
        5: "๕",
        6: "๖",
        7: "๗",
        8: "๘",
        9: "๙",
        10: "๑๐",
    }

    sub_math = st.radio(
        "📌 เลือกหัวข้อคณิตศาสตร์ที่ต้องการฝึก:",
        [
            "1️⃣ จับคู่เลขไทย (๑-๑๐) กับ อารบิก (1-10)",
            "2️⃣ นับจำนวนสิ่งของ (1-10)",
            "3️⃣ เปรียบเทียบขนาด (สั้น-ยาว / สูง-เตี้ย / เล็ก-ใหญ่)",
        ],
        horizontal=False,
    )

    st.divider()

    if "1️⃣" in sub_math:
        st.subheader("1. จับคู่เลขไทย (๑-๑๐) กับ เลขอารบิก (1-10)")

        if "math_target_num" not in st.session_state:
            st.session_state.math_target_num = random.randint(1, 10)

        target_n = st.session_state.math_target_num
        target_thai = NUM_MAPPING[target_n]

        st.markdown(
            f"<h2 style='text-align: center;'>เลขไทย <span style='color: #FF3D00; font-size: 80px;'>'{target_thai}'</span> ตรงกับเลขอารบิกตัวไหน?</h2>",
            unsafe_allow_html=True,
        )

        wrong_nums = [n for n in range(1, 11) if n != target_n]
        math_choices = random.sample(wrong_nums, 3) + [target_n]

        if "shuffled_math_num" not in st.session_state:
            st.session_state.shuffled_math_num = math_choices.copy()
            random.shuffle(st.session_state.shuffled_math_num)

        cols = st.columns(4)
        for idx, n_ans in enumerate(st.session_state.shuffled_math_num):
            with cols[idx]:
                if st.button(
                    str(n_ans), key=f"btn_num_{n_ans}", use_container_width=True
                ):
                    if n_ans == target_n:
                        st.balloons()
                        st.success(
                            f"🎉 เก่งมาก! เลขไทย {target_thai} คือ เลขอารบิก {target_n} กำลังไปข้อถัดไป..."
                        )
                        st.session_state.math_target_num = random.randint(
                            1, 10
                        )
                        if "shuffled_math_num" in st.session_state:
                            del st.session_state.shuffled_math_num
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.error(f"❌ ยังไม่ใช่ครับ! อันนี้คือเลข {n_ans}")

        st.write("")
        if st.button("🎲 สุ่มเลขใหม่"):
            st.session_state.math_target_num = random.randint(1, 10)
            if "shuffled_math_num" in st.session_state:
                del st.session_state.shuffled_math_num
            st.rerun()

    elif "2️⃣" in sub_math:
        st.subheader("2. นับจำนวนและระบุตัวเลข (1-10)")

        if "count_item_num" not in st.session_state:
            st.session_state.count_item_num = random.randint(1, 10)

        count_n = st.session_state.count_item_num
        apples_str = " ".join(["🍊"] * count_n)

        st.write("นับส้มสิว่ามีกี่ผล? 🍊")
        st.markdown(
            f"<div class='emoji-box'>{apples_str}</div>", unsafe_allow_html=True
        )

        wrong_counts = [n for n in range(1, 11) if n != count_n]
        count_choices = random.sample(wrong_counts, 2) + [count_n]

        if "shuffled_count_choices" not in st.session_state:
            st.session_state.shuffled_count_choices = count_choices.copy()
            random.shuffle(st.session_state.shuffled_count_choices)

        cols = st.columns(3)
        for idx, c_ans in enumerate(st.session_state.shuffled_count_choices):
            with cols[idx]:
                if st.button(
                    f"{c_ans} ผล",
                    key=f"btn_count_{c_ans}",
                    use_container_width=True,
                ):
                    if c_ans == count_n:
                        st.balloons()
                        st.success(
                            f"🎉 ถูกต้อง! มีส้มทั้งหมด {count_n} ผล กำลังไปข้อถัดไป..."
                        )
                        st.session_state.count_item_num = random.randint(1, 10)
                        if "shuffled_count_choices" in st.session_state:
                            del st.session_state.shuffled_count_choices
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.error("❌ ลองนับใหม่อีกทีนะ 1...2...3...")

        st.write("")
        if st.button("🎲 เปลี่ยนจำนวนส้มใหม่"):
            st.session_state.count_item_num = random.randint(1, 10)
            if "shuffled_count_choices" in st.session_state:
                del st.session_state.shuffled_count_choices
            st.rerun()

    elif "3️⃣" in sub_math:
        st.subheader("3. เปรียบเทียบขนาด")

        if "size_sub_stage" not in st.session_state:
            st.session_state.size_sub_stage = 1

        st.caption(
            f"ข้อที่ {st.session_state.size_sub_stage} / 3 (สั้น-ยาว, สูง-เตี้ย, เล็ก-ใหญ่)"
        )

        if st.session_state.size_sub_stage == 1:
            st.write("📍 **ข้อ 1: สิ่งไหน 'ยาว' กว่ากัน?**")
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("✏️✏️✏️ ดินสอยาว", use_container_width=True):
                    st.balloons()
                    st.success("🎉 ถูกต้องครับ! กำลังไปข้อถัดไป...")
                    time.sleep(1.5)
                    st.session_state.size_sub_stage = 2
                    st.rerun()
            with col_b:
                if st.button("✏️ ดินสอสั้น", use_container_width=True):
                    st.error("❌ อันนี้สั้นกว่าครับ")

        elif st.session_state.size_sub_stage == 2:
            st.write("📍 **ข้อ 2: สัตว์ตัวไหน 'สูง' กว่ากัน?**")
            col_c, col_d = st.columns(2)
            with col_c:
                if st.button("🦒 ยีราฟสูง", use_container_width=True):
                    st.balloons()
                    st.success("🎉 เก่งมาก! ยีราฟตัวสูง กำลังไปข้อถัดไป...")
                    time.sleep(1.5)
                    st.session_state.size_sub_stage = 3
                    st.rerun()
            with col_d:
                if st.button("🐧 เพนกวินเตี้ย", use_container_width=True):
                    st.error("❌ เพนกวินตัวเตี้ยกว่าครับ")

        elif st.session_state.size_sub_stage == 3:
            st.write("📍 **ข้อ 3: สิ่งไหน 'เล็ก' กว่ากัน?**")
            col_e, col_f = st.columns(2)
            with col_e:
                if st.button("⚽ ฟุตบอลใหญ่", use_container_width=True):
                    st.error("❌ ฟุตบอลลูกใหญ่กว่านะ")
            with col_f:
                if st.button("🎾 เทนนิสเล็ก", use_container_width=True):
                    st.balloons()
                    st.success(
                        "🎉 ถูกต้อง! ลูกเทนนิสเล็กกว่า ผ่านครบทุกข้อแล้ว 🏆"
                    )

            if st.button("🔄 เริ่มเล่นเปรียบเทียบขนาดใหม่", type="primary"):
                st.session_state.size_sub_stage = 1
                st.rerun()


# ==========================================
# 3. หมวดวิชาภาษาอังกฤษ (A - Z ครบ 26 ตัว)
# ==========================================
with tab3:
    ENG_DICT = {
        "A": ("Apple", "🍎"),
        "B": ("Bird", "🐦"),
        "C": ("Cat", "🐱"),
        "D": ("Dog", "🐶"),
        "E": ("Elephant", "🐘"),
        "F": ("Fish", "🐟"),
        "G": ("Giraffe", "🦒"),
        "H": ("Horse", "🐴"),
        "I": ("Ice cream", "🍦"),
        "J": ("Juice", "🧃"),
        "K": ("Kangaroo", "🦘"),
        "L": ("Lion", "🦁"),
        "M": ("Monkey", "🐒"),
        "N": ("Nest", "🪹"),
        "O": ("Owl", "🦉"),
        "P": ("Pig", "🐷"),
        "Q": ("Queen", "👸"),
        "R": ("Rabbit", "🐰"),
        "S": ("Sun", "☀️"),
        "T": ("Tiger", "🐯"),
        "U": ("Umbrella", "☂️"),
        "V": ("Van", "🚐"),
        "W": ("Watermelon", "🍉"),
        "X": ("Xylophone", "🎼"),
        "Y": ("Yacht", "🛥️"),
        "Z": ("Zebra", "🦓"),
    }

    if "eng_stage" not in st.session_state:
        st.session_state.eng_stage = 1
    if "eng_score" not in st.session_state:
        st.session_state.eng_score = 0
    if "current_eng_letter" not in st.session_state:
        st.session_state.current_eng_letter = "A"

    st.caption(f"🏆 ภาษาอังกฤษ: ด่านที่ {st.session_state.eng_stage} / 2")

    if st.session_state.eng_stage == 1:
        st.subheader("ด่านที่ 1: บอกตัวอักษรภาษาอังกฤษ (A - Z)")
        st.write("ทายออกเสียงอ่านตัวอักษรภาษาอังกฤษที่กำหนด")

        if "flash_eng_letter" not in st.session_state:
            st.session_state.flash_eng_letter = "A"

        st.markdown(
            f"<div class='giant-text'>{st.session_state.flash_eng_letter}</div>",
            unsafe_allow_html=True,
        )

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🎲 สุ่มตัวอักษรใหม่"):
                st.session_state.flash_eng_letter = random.choice(
                    list(ENG_DICT.keys())
                )
                st.rerun()
        with col_b:
            if st.button("ไปด่านจับคู่ A-Z ➡️", type="primary"):
                st.session_state.eng_stage = 2
                st.rerun()

    elif st.session_state.eng_stage == 2:
        st.subheader("ด่านที่ 2: จับคู่ตัวอักษร A-Z กับรูปภาพคำศัพท์")

        st.progress(
            min(st.session_state.eng_score / 26, 1.0),
            text=f"สะสมคำตอบถูกต้อง: {st.session_state.eng_score} / 26 ตัว",
        )

        eng_target = st.session_state.current_eng_letter
        eng_correct_word, eng_correct_emoji = ENG_DICT[eng_target]

        st.markdown(
            f"<h2 style='text-align: center;'>รูปภาพไหนตรงกับตัวอักษร: <span style='color: #FF3D00; font-size: 60px;'>'{eng_target}'</span> ?</h2>",
            unsafe_allow_html=True,
        )

        other_eng_letters = [k for k in ENG_DICT.keys() if k != eng_target]
        wrong_eng_samples = random.sample(other_eng_letters, 2)

        eng_options = [
            (eng_target, eng_correct_word, eng_correct_emoji),
            (
                wrong_eng_samples[0],
                ENG_DICT[wrong_eng_samples[0]][0],
                ENG_DICT[wrong_eng_samples[0]][1],
            ),
            (
                wrong_eng_samples[1],
                ENG_DICT[wrong_eng_samples[1]][0],
                ENG_DICT[wrong_eng_samples[1]][1],
            ),
        ]

        if "shuffled_eng_options" not in st.session_state:
            st.session_state.shuffled_eng_options = eng_options.copy()
            random.shuffle(st.session_state.shuffled_eng_options)

        cols = st.columns(3)
        for idx, (l_code, word, emoji) in enumerate(
            st.session_state.shuffled_eng_options
        ):
            with cols[idx]:
                btn_text = f"{emoji} {word}"
                if st.button(
                    btn_text, key=f"btn_eng_{l_code}", use_container_width=True
                ):
                    if l_code == eng_target:
                        st.balloons()
                        st.success(
                            f"🎉 Excellent! {eng_target} - {word} กำลังไปข้อถัดไป..."
                        )
                        st.session_state.eng_score += 1
                        st.session_state.current_eng_letter = random.choice(
                            list(ENG_DICT.keys())
                        )
                        if "shuffled_eng_options" in st.session_state:
                            del st.session_state.shuffled_eng_options
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.error(f"❌ Try again! อันนี้คือ {l_code} - {word}")

        st.write("")
        if st.button("🔄 สุ่มโจทย์ภาษาอังกฤษใหม่"):
            st.session_state.current_eng_letter = random.choice(
                list(ENG_DICT.keys())
            )
            if "shuffled_eng_options" in st.session_state:
                del st.session_state.shuffled_eng_options
            st.rerun()
