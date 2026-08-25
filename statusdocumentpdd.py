import streamlit as st
import sqlite3
import os
import shutil
import requests
from datetime import datetime
import fitz  # PyMuPDF สำหรับปั๊ม ตรา Stamp ลงบน PDF

# -------------------------------------------------------------
# 1. การตั้งค่าหน้าตา Web App & Custom CSS (โทนสี ม่วง-เทา-ฟ้า)
# -------------------------------------------------------------
st.set_page_config(
    page_title="Document Approval System",
    page_icon="📄",
    layout="wide"
)

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    h1, h2, h3 { color: #3b0764 !important; font-family: 'Sarabun', 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #1e1b4b; color: #f1f5f9; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] span { color: #f1f5f9 !important; }
    div.stButton > button[kind="primary"] {
        background-color: #6366f1 !important; color: #ffffff !important;
        border-radius: 8px !important; border: none !important;
        font-weight: 600 !important; box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.3);
    }
    div.stButton > button[kind="primary"]:hover { background-color: #4f46e5 !important; }
    div.stButton > button[kind="secondary"] {
        background-color: #0284c7 !important; color: #ffffff !important;
        border-radius: 8px !important; border: none !important; font-weight: 500 !important;
    }
    div.stButton > button[kind="secondary"]:hover { background-color: #0369a1 !important; }
    .streamlit-expanderHeader {
        background-color: #ffffff !important; border-radius: 8px !important;
        border-left: 4px solid #8b5cf6 !important; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    }
    button[data-baseweb="tab"] { color: #475569 !important; font-weight: 600 !important; }
    button[aria-selected="true"] { color: #7c3aed !important; border-bottom-color: #7c3aed !important; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { border-radius: 6px !important; border: 1px solid #cbd5e1 !important; }
    </style>
""", unsafe_allow_html=True)

UPLOAD_DIR = "./uploaded_documents"
DB_FILE = "document_approval.db"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# รายชื่อชนิดเอกสาร
DOC_TYPES_PORTRAIT = ["OM", "PROCESS FLOW", "MATERIAL SPEC"]
DOC_TYPES_LANDSCAPE = ["ACC DWG", "MASTER DWG.", "FMEA"]
ALL_DOC_TYPES = DOC_TYPES_PORTRAIT + DOC_TYPES_LANDSCAPE

# 🌐 ตั้งค่าระบบ LINE Notification & URL แอปพลิเคชัน
LINE_ACCESS_TOKEN = "RBMqGMQq55Qc+ia3TCT/eZbs6Hp/8eyFSRUCy5URtFhopGRzo83Y2m+7K4JZplUgOZi13r/f9JyHm9bLg4VRfuV84l6/zktHMm2hASsDevA0brJNfeTIqhHci5K3vKgIUJ9xnIM5yJftZPD6vReKegdB04t89/1O/w1cDnyilFU="
LINE_GROUP_ID = "C1d74e9b109ef2672511754c17702dab8"

# ⚠️ กรุณาเปลี่ยนเป็น URL ของคุณ (เช่น https://your-app.streamlit.app หรือ IP เครื่องในวง LAN)
APP_URL = "https://statusdocumentpdd-df84ykbbpe9wc8pchnhjpf.streamlit.app/" 

# -------------------------------------------------------------
# 2. ฟังก์ชันส่งแจ้งเตือนเข้า LINE Group (เพิ่มลิงก์ + เช็ค Error)
# -------------------------------------------------------------
def send_line_notify(message):
    if not LINE_ACCESS_TOKEN or LINE_ACCESS_TOKEN == "YOUR_LINE_ACCESS_TOKEN_HERE":
        print("⚠️ LINE_ACCESS_TOKEN ไม่ถูกตั้งค่า")
        return
    if not LINE_GROUP_ID or LINE_GROUP_ID == "YOUR_LINE_GROUP_ID_HERE":
        print("⚠️ LINE_GROUP_ID ไม่ถูกตั้งค่า")
        return

    url = "https://api.line.me/v2/bot/message/push"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"}
    payload = {"to": LINE_GROUP_ID, "messages": [{"type": "text", "text": message}]}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=5)
        if response.status_code == 200:
            print("✅ ส่งข้อความแจ้งเตือน LINE สำเร็จ")
        else:
            print(f"❌ ส่ง LINE ไม่สำเร็จ Status Code: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"Failed to send LINE message: {e}")

# -------------------------------------------------------------
# 3. ฟังก์ชันประทับตรา Stamp ลงบน PDF
# -------------------------------------------------------------
def add_approval_stamp(pdf_path, orientation="Portrait"):
    try:
        if not os.path.exists(pdf_path):
            st.error(f"ไม่พบไฟล์ PDF ในระบบ: {pdf_path}")
            return False

        doc = fitz.open(pdf_path)
        page = doc[0]  # ดึงหน้าแรก
        
        rect = page.rect
        page_w = rect.width
        page_h = rect.height
        rot = page.rotation

        stamp_w = 140
        stamp_h = 42
        margin = 20

        # คำนวณพิกัดกล่อง Stamp ตาม Rotation ของ PDF
        if rot == 270:
            x0 = margin
            x1 = x0 + stamp_h
            y0 = margin
            y1 = y0 + stamp_w
            text_rot = 270
        elif rot == 90:
            x1 = page_w - margin
            x0 = x1 - stamp_h
            y1 = page_h - margin
            y0 = y1 - stamp_w
            text_rot = 90
        elif rot == 180:
            x0 = margin
            x1 = x0 + stamp_w
            y1 = page_h - margin
            y0 = y1 - stamp_h
            text_rot = 180
        else:
            x1 = page_w - margin
            x0 = x1 - stamp_w
            y0 = margin
            y1 = y0 + stamp_h
            text_rot = 0

        stamp_rect = fitz.Rect(x0, y0, x1, y1)

        # ข้อความที่จะปั๊ม
        current_date = datetime.now().strftime("%Y-%m-%d")
        stamp_text = f"APPROVED\n{current_date}"

        # 1. วาดกรอบสี่เหลี่ยมสีแดง
        page.draw_rect(
            stamp_rect, 
            color=(0.8, 0, 0),       # เส้นขอบสีแดง
            fill=(1, 0.9, 0.9),      # พื้นหลังสีชมพูอ่อน
            width=2,
            overlay=True
        )

        # 2. ปั๊มข้อความตัวหนังสือ
        page.insert_textbox(
            stamp_rect, 
            stamp_text, 
            fontsize=11, 
            fontname="helv", 
            color=(0.8, 0, 0), 
            align=fitz.TEXT_ALIGN_CENTER,
            rotate=text_rot,
            overlay=True
        )

        # บันทึกไฟล์ทับไฟล์เดิม
        temp_path = pdf_path + ".tmp"
        doc.save(temp_path, clean=True, deflate=True)
        doc.close()

        os.replace(temp_path, pdf_path)
        return True

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการปั๊มตรา Stamp: {e}")
        return False

# -------------------------------------------------------------
# 4. จัดการฐานข้อมูล SQLite
# -------------------------------------------------------------
def get_db_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id TEXT UNIQUE,
            doc_type TEXT DEFAULT 'OM',
            orientation TEXT DEFAULT 'Portrait',
            official_reg_number TEXT DEFAULT '-',
            title TEXT NOT NULL,
            description TEXT DEFAULT '-',
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            prepared_by TEXT NOT NULL,
            checked_by TEXT DEFAULT '-',
            approved_by TEXT DEFAULT '-',
            registered_by TEXT DEFAULT '-',
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute("PRAGMA table_info(documents)")
    columns = [col[1] for col in cursor.fetchall()]
    if "doc_type" not in columns:
        cursor.execute("ALTER TABLE documents ADD COLUMN doc_type TEXT DEFAULT 'OM'")
    if "orientation" not in columns:
        cursor.execute("ALTER TABLE documents ADD COLUMN orientation TEXT DEFAULT 'Portrait'")
        
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id TEXT NOT NULL,
            action_by TEXT NOT NULL,
            action TEXT NOT NULL,
            comment TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# -------------------------------------------------------------
# 5. User Authentication
# -------------------------------------------------------------
USERS = {
    "user_prepare": {"password": "123", "role": "Prepare", "name": "Thanawat C. (ผู้จัดทำ)"},
    "user_check": {"password": "123", "role": "Check", "name": "Manoch J. (ผู้ตรวจสอบ)"},
    "user_approve": {"password": "123", "role": "Approve", "name": "Geattisak K. (ผู้อนุมัติ)"},
    "user_register": {"password": "123", "role": "Register", "name": "Sudarat S. (ขึ้นทะเบียน/สั่งพิมพ์)"}
}

if "authenticated_user" not in st.session_state:
    st.session_state.authenticated_user = None

def login_screen():
    st.markdown("<h2 style='text-align: center; color: #4c1d95;'>🔐 เข้าสู่ระบบ อนุมัติและขึ้นทะเบียนเอกสาร</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Log In", use_container_width=True, type="primary")
            if submit:
                if username in USERS and USERS[username]["password"] == password:
                    st.session_state.authenticated_user = {
                        "username": username,
                        "role": USERS[username]["role"],
                        "name": USERS[username]["name"]
                    }
                    st.success(f"ยินดีต้อนรับ {USERS[username]['name']}")
                    st.rerun()
                else:
                    st.error("Username หรือ Password ไม่ถูกต้อง")

def add_log(doc_id, action_by, action, comment=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO audit_logs (doc_id, action_by, action, comment) VALUES (?, ?, ?, ?)", (doc_id, action_by, action, comment))
    conn.commit()
    conn.close()

def get_documents_by_status(statuses=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if statuses:
        placeholders = ', '.join(['?'] * len(statuses))
        cursor.execute(f"SELECT * FROM documents WHERE status IN ({placeholders}) ORDER BY id DESC", statuses)
    else:
        cursor.execute("SELECT * FROM documents ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# -------------------------------------------------------------
# 6. Main Application
# -------------------------------------------------------------
def main_app():
    user = st.session_state.authenticated_user
    st.sidebar.title("👤 ผู้ใช้งานปัจจุบัน")
    st.sidebar.write(f"**ชื่อ:** {user['name']}")
    st.sidebar.write(f"**สิทธิ์ (Role):** `{user['role']}`")
    
    if st.sidebar.button("🚪 Logout", type="primary"):
        st.session_state.authenticated_user = None
        st.rerun()

    if user["role"] == "Register":
        st.sidebar.markdown("---")
        st.sidebar.subheader("⚙️ ระบบผู้ดูแล (Admin Tools)")
        if st.sidebar.button("⚠️ ล้างข้อมูลทั้งหมด (Reset System)"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            if os.path.exists(UPLOAD_DIR):
                shutil.rmtree(UPLOAD_DIR)
                os.makedirs(UPLOAD_DIR, exist_ok=True)
            init_db()
            st.sidebar.success("ล้างข้อมูลระบบเรียบร้อยแล้ว!")
            st.rerun()

    st.title("📄 ระบบตรวจสอบ อนุมัติ และขึ้นทะเบียนเอกสาร")
    st.markdown("---")

    # PREPARE
    if user["role"] == "Prepare":
        st.subheader("1. จัดทำและส่งเอกสาร (Prepare)")
        tab1, tab2 = st.tabs(["📤 ส่งเอกสารใหม่", "✏️ แก้ไข/ลบเอกสารที่ถูกตีกลับ"])
        
        with tab1:
            with st.form("upload_form", clear_on_submit=True):
                doc_type = st.selectbox("ชนิดเอกสาร (Document Type)", ALL_DOC_TYPES)
                
                orientation = st.radio(
                    "📐 ทิศทางแนวเอกสาร (Orientation สำหรับปั๊ม Stamp):",
                    options=["Portrait (แนวตั้ง)", "Landscape (แนวนอน/Drawing)"],
                    horizontal=True
                )
                orientation_val = "Portrait" if "Portrait" in orientation else "Landscape"

                doc_title = st.text_input("ชื่อเรื่อง/ชื่อเอกสาร")
                doc_description = st.text_area("รายละเอียดเนื้อหาการขอแก้ไข/จัดทำเอกสาร")
                uploaded_file = st.file_uploader("อัปโหลดไฟล์ PDF", type=["pdf"])
                submit = st.form_submit_button("ส่งเอกสารเข้าระบบ", type="primary")

                if submit and doc_title and uploaded_file:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM documents")
                    count = cursor.fetchone()[0]
                    doc_id = f"TMP-{count + 1:04d}"
                    file_path = os.path.join(UPLOAD_DIR, f"{doc_id}_{uploaded_file.name}")
                    
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    cursor.execute('''
                        INSERT INTO documents (doc_id, doc_type, orientation, title, description, filename, file_path, prepared_by, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (doc_id, doc_type, orientation_val, doc_title, doc_description or "-", uploaded_file.name, file_path, user["name"], "PENDING_CHECK"))
                    conn.commit()
                    conn.close()

                    add_log(doc_id, user["name"], f"สร้างเอกสาร ({doc_type} / {orientation_val}) และส่งเข้าสถานะรอตรวจสอบ")
                    
                    msg = (
                        f"📢 [แจ้งเตือน: เอกสารใหม่รอการตรวจสอบ]\n"
                        f"📌 รหัส: {doc_id} | ชนิด: {doc_type} | แนว: {orientation_val}\n📝 เรื่อง: {doc_title}\n"
                        f"📋 รายละเอียด: {doc_description or '-'}\n👤 ผู้ส่ง: {user['name']}\n"
                        f"-----------------------------------\n"
                        f"🔔 ถึงคุณ: [ผู้ตรวจสอบ / Check]\n"
                        f"🔗 คลิกเพื่อดำเนินการ: {APP_URL}"
                    )
                    send_line_notify(msg)
                    st.success(f"ส่งเอกสารสำเร็จ! รหัสเอกสาร: {doc_id}")
                    st.rerun()

        with tab2:
            editable_docs = get_documents_by_status(["PENDING_CHECK", "REJECTED"])
            if editable_docs:
                for doc in editable_docs:
                    with st.expander(f"⚙️ Manage: {doc['doc_id']} - {doc['title']}"):
                        current_type = doc.get('doc_type', 'OM')
                        type_index = ALL_DOC_TYPES.index(current_type) if current_type in ALL_DOC_TYPES else 0
                        new_doc_type = st.selectbox("แก้ไขชนิดเอกสาร", ALL_DOC_TYPES, index=type_index, key=f"edit_type_{doc['doc_id']}")
                        
                        curr_orient = doc.get('orientation', 'Portrait')
                        orient_index = 0 if curr_orient == "Portrait" else 1
                        new_orient = st.radio(
                            "แก้ไขทิศทางแนวเอกสาร",
                            options=["Portrait (แนวตั้ง)", "Landscape (แนวนอน/Drawing)"],
                            index=orient_index,
                            horizontal=True,
                            key=f"edit_orient_{doc['doc_id']}"
                        )
                        new_orient_val = "Portrait" if "Portrait" in new_orient else "Landscape"

                        new_title = st.text_input("แก้ไขชื่อเอกสาร", value=doc['title'], key=f"edit_title_{doc['doc_id']}")
                        new_description = st.text_area("รายละเอียด/เนื้อหาการแก้ไข", value=doc.get('description', '-'), key=f"edit_desc_{doc['doc_id']}")
                        new_file = st.file_uploader("เปลี่ยนไฟล์ PDF ใหม่ (ถ้ามี)", type=["pdf"], key=f"edit_file_{doc['doc_id']}")
                        col_save, col_del = st.columns([1, 1])
                        
                        if col_save.button("💾 บันทึกการแก้ไข & ส่งใหม่", key=f"btn_save_{doc['doc_id']}", type="primary"):
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            file_path = doc["file_path"]
                            filename = doc["filename"]
                            if new_file:
                                file_path = os.path.join(UPLOAD_DIR, f"{doc['doc_id']}_{new_file.name}")
                                with open(file_path, "wb") as f: f.write(new_file.getbuffer())
                                filename = new_file.name

                            cursor.execute("UPDATE documents SET doc_type = ?, orientation = ?, title = ?, description = ?, filename = ?, file_path = ?, status = 'PENDING_CHECK' WHERE doc_id = ?", (new_doc_type, new_orient_val, new_title, new_description or "-", filename, file_path, doc['doc_id']))
                            conn.commit()
                            conn.close()
                            add_log(doc['doc_id'], user["name"], "แก้ไขข้อมูลเอกสารและส่งใหม่")
                            st.success("แก้ไขข้อมูลเรียบร้อยแล้ว!")
                            st.rerun()

                        if col_del.button("🗑️ ลบเอกสารนี้", key=f"btn_del_{doc['doc_id']}"):
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM documents WHERE doc_id = ?", (doc['doc_id'],))
                            cursor.execute("DELETE FROM audit_logs WHERE doc_id = ?", (doc['doc_id'],))
                            conn.commit()
                            conn.close()
                            if os.path.exists(doc["file_path"]): os.remove(doc["file_path"])
                            st.rerun()

    # CHECK
    elif user["role"] == "Check":
        st.subheader("2. ตรวจสอบความถูกต้องเอกสาร (Check)")
        pending_list = get_documents_by_status(["PENDING_CHECK"])
        if pending_list:
            for doc in pending_list:
                with st.expander(f"📌 {doc['doc_id']} [{doc.get('doc_type', 'OM')}] - {doc['title']} (ผู้จัดทำ: {doc['prepared_by']})"):
                    st.markdown(f"**🏷️ ชนิดเอกสาร:** `{doc.get('doc_type', 'OM')}` | **📐 แนวเอกสาร:** `{doc.get('orientation', 'Portrait')}`")
                    st.markdown(f"**📋 รายละเอียด:** {doc.get('description', '-')}")
                    if os.path.exists(doc["file_path"]):
                        with open(doc["file_path"], "rb") as f:
                            st.download_button("📥 ดาวน์โหลด/ดูไฟล์ PDF", f, file_name=doc["filename"], key=f"dl_{doc['doc_id']}")
                    
                    comment = st.text_area("ความเห็น / หมายเหตุ", key=f"c_com_{doc['doc_id']}")
                    col1, col2 = st.columns(2)
                    if col1.button("✅ ตรวจสอบผ่าน", key=f"c_pass_{doc['doc_id']}", type="primary"):
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("UPDATE documents SET status = 'PENDING_APPROVE', checked_by = ? WHERE doc_id = ?", (user["name"], doc['doc_id']))
                        conn.commit()
                        conn.close()
                        add_log(doc['doc_id'], user["name"], "ตรวจสอบผ่าน (Check Pass)", comment)
                        
                        msg = (
                            f"✅ [แจ้งเตือน: ผ่านการตรวจสอบแล้ว]\n"
                            f"📌 รหัส: {doc['doc_id']}\n📝 เรื่อง: {doc['title']}\n🔍 ผู้ตรวจสอบ: {user['name']}\n"
                            f"-----------------------------------\n"
                            f"🔔 ถึงคุณ: [ผู้อนุมัติ / Approve]\n"
                            f"🔗 คลิกเพื่ออนุมัติเอกสาร: {APP_URL}"
                        )
                        send_line_notify(msg)
                        st.rerun()
                        
                    if col2.button("❌ ตีกลับแก้ไข", key=f"c_rej_{doc['doc_id']}"):
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("UPDATE documents SET status = 'REJECTED' WHERE doc_id = ?", (doc['doc_id'],))
                        conn.commit()
                        conn.close()
                        add_log(doc['doc_id'], user["name"], "ตีกลับแก้ไข (Rejected)", comment)
                        st.rerun()
        else:
            st.info("ไม่มีรายการเอกสารที่รอการตรวจสอบ")

    # APPROVE
    elif user["role"] == "Approve":
        st.subheader("3. อนุมัติเอกสาร (Approve)")
        pending_list = get_documents_by_status(["PENDING_APPROVE"])
        if pending_list:
            for doc in pending_list:
                doc_type = doc.get('doc_type', 'OM')
                doc_orient = doc.get('orientation', 'Portrait')
                
                with st.expander(f"📌 {doc['doc_id']} [{doc_type}] - {doc['title']} (ผู้ตรวจสอบ: {doc['checked_by']})"):
                    st.markdown(f"**🏷️ ชนิดเอกสาร:** `{doc_type}` | **📐 แนวเอกสาร:** `{doc_orient}`")
                    st.markdown(f"**📋 รายละเอียด:** {doc.get('description', '-')}")
                    if os.path.exists(doc["file_path"]):
                        with open(doc["file_path"], "rb") as f:
                            st.download_button("📥 ดาวน์โหลด/ดูไฟล์ PDF ต้นฉบับ", f, file_name=doc["filename"], key=f"dl_a_{doc['doc_id']}")
                            
                    comment = st.text_area("ความเห็นผู้อนุมัติ", key=f"a_com_{doc['doc_id']}")
                    col1, col2 = st.columns(2)
                    
                    if col1.button("✅ อนุมัติเอกสาร (พร้อมปั๊มตรา Stamp)", key=f"a_pass_{doc['doc_id']}", type="primary"):
                        stamp_success = add_approval_stamp(doc["file_path"], orientation=doc_orient)
                        
                        if stamp_success:
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute("UPDATE documents SET status = 'PENDING_REGISTER', approved_by = ? WHERE doc_id = ?", (user["name"], doc['doc_id']))
                            conn.commit()
                            conn.close()
                            
                            add_log(doc['doc_id'], user["name"], "อนุมัติเอกสาร และประทับตรา Stamp เรียบร้อยแล้ว", comment)
                            
                            msg = (
                                f"🎉 [แจ้งเตือน: เอกสารได้รับการอนุมัติแล้ว (ประทับตรา Stamp แล้ว)]\n"
                                f"📌 รหัส: {doc['doc_id']} | ชนิด: {doc_type}\n📝 เรื่อง: {doc['title']}\n"
                                f"✍️ ผู้อนุมัติ: {user['name']}\n💬 ความเห็น: {comment or '-'}\n"
                                f"-----------------------------------\n"
                                f"🔔 ถึงคุณ: [เจ้าหน้าที่ขึ้นทะเบียน / Register & Print]\n"
                                f"🔗 คลิกเพื่อขึ้นทะเบียนและดาวน์โหลด: {APP_URL}"
                            )
                            send_line_notify(msg)
                            st.success("อนุมัติเอกสารและประทับตรา Stamp เรียบร้อยแล้ว!")
                            st.rerun()
                        
                    if col2.button("❌ ไม่อนุมัติ", key=f"a_rej_{doc['doc_id']}"):
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("UPDATE documents SET status = 'REJECTED' WHERE doc_id = ?", (doc['doc_id'],))
                        conn.commit()
                        conn.close()
                        add_log(doc['doc_id'], user["name"], "ไม่อนุมัติ (Approved Reject)", comment)
                        st.rerun()
        else:
            st.info("ไม่มีรายการเอกสารที่รอการอนุมัติ")

    # REGISTER & PRINT
    elif user["role"] == "Register":
        st.subheader("4. ขึ้นทะเบียนและสั่งพิมพ์เอกสาร (Register & Print)")
        pending_list = get_documents_by_status(["PENDING_REGISTER"])
        if pending_list:
            for doc in pending_list:
                with st.expander(f"📌 {doc['doc_id']} [{doc.get('doc_type', 'OM')}] - {doc['title']} (อนุมัติโดย: {doc['approved_by']})"):
                    st.markdown(f"**🏷️ ชนิดเอกสาร:** `{doc.get('doc_type', 'OM')}` | **📐 แนวเอกสาร:** `{doc.get('orientation', 'Portrait')}`")
                    st.markdown(f"**📋 รายละเอียด:** {doc.get('description', '-')}")
                    reg_no = st.text_input("กำหนดเลขทะเบียนเอกสาร (เช่น DAR-2026-001)", key=f"r_num_{doc['doc_id']}")
                    
                    if os.path.exists(doc["file_path"]):
                        with open(doc["file_path"], "rb") as f:
                            pdf_bytes = f.read()
                            st.download_button(
                                label="📥 ดาวน์โหลดไฟล์ PDF (ที่มีตรา Stamp อนุมัติแล้ว)", 
                                data=pdf_bytes, 
                                file_name=f"APPROVED_{doc['filename']}", 
                                mime="application/pdf",
                                key=f"dl_r_{doc['doc_id']}"
                            )

                    if st.button("🖨️ บันทึกขึ้นทะเบียน & ยืนยันการพิมพ์", key=f"r_btn_{doc['doc_id']}", type="primary"):
                        if reg_no:
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute("UPDATE documents SET status = 'REGISTERED_AND_PRINTED', official_reg_number = ?, registered_by = ? WHERE doc_id = ?", (reg_no, user["name"], doc['doc_id']))
                            conn.commit()
                            conn.close()
                            
                            add_log(doc['doc_id'], user["name"], f"ขึ้นทะเบียนเลข {reg_no} และสั่งพิมพ์เรียบร้อยแล้ว")
                            
                            msg = (
                                f"🖨️ [แจ้งเตือน: ขึ้นทะเบียนสำเร็จ]\n"
                                f"🏷️ เลขทะเบียน: {reg_no}\n📝 เรื่อง: {doc['title']}\n"
                                f"-----------------------------------\n"
                                f"🔗 ดูตารางติดตามสถานะ: {APP_URL}"
                            )
                            send_line_notify(msg)
                            st.success("ขึ้นทะเบียนและบันทึกเรียบร้อยแล้ว")
                            st.rerun()
                        else:
                            st.warning("กรุณาระบุเลขทะเบียนเอกสาร")
        else:
            st.info("ไม่มีรายการเอกสารรอการขึ้นทะเบียน")

    # Dashboard Table
    st.markdown("---")
    st.subheader("📊 ตารางติดตามสถานะเอกสารทั้งหมด (DB View)")
    all_docs = get_documents_by_status()
    if all_docs:
        st.dataframe(all_docs, use_container_width=True)
        with st.expander("📜 ดูประวัติการดำเนินการอย่างรายละเอียด (Audit Logs)"):
            doc_ids = [d["doc_id"] for d in all_docs]
            selected_doc_id = st.selectbox("เลือกเอกสารเพื่อดูประวัติ", doc_ids)
            if selected_doc_id:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM audit_logs WHERE doc_id = ? ORDER BY id ASC", (selected_doc_id,))
                logs = cursor.fetchall()
                conn.close()
                for log in logs:
                    st.write(f"- **[{log['timestamp']}] {log['action_by']}**: {log['action']} *(หมายเหตุ: {log['comment'] or '-'})*")
    else:
        st.caption("ยังไม่มีข้อมูลเอกสารในระบบ")

if st.session_state.authenticated_user is None:
    login_screen()
else:
    main_app()