import streamlit as st
import sqlite3
import os
import shutil
from datetime import datetime
import fitz  # PyMuPDF สำหรับปั๊ม ตรา Stamp ลงบน PDF
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# -------------------------------------------------------------
# 1. การตั้งค่าหน้าตา Web App & Custom CSS
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

DOC_TYPES_PORTRAIT = ["OM", "PROCESS FLOW", "MATERIAL SPEC"]
DOC_TYPES_LANDSCAPE = ["ACC DWG", "MASTER DWG.", "FMEA"]
ALL_DOC_TYPES = DOC_TYPES_PORTRAIT + DOC_TYPES_LANDSCAPE

# -------------------------------------------------------------
# 2. ดึงข้อมูล Configuration และ USERS จาก st.secrets
# -------------------------------------------------------------
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

try:
    SENDER_EMAIL = st.secrets["email"]["SENDER_EMAIL"]
    SENDER_PASSWORD = st.secrets["email"]["SENDER_PASSWORD"]
    USERS = dict(st.secrets["users"])
except Exception as e:
    st.error("⚠️ ไม่สามารถโหลดค่าจาก st.secrets ได้ กรุณาตรวจสอบไฟล์ .streamlit/secrets.toml")
    st.stop()

APP_URL = "https://statusdocumentpdd-df84ykbbpe9wc8pchnhjpf.streamlit.app/"

# -------------------------------------------------------------
# 3. ฟังก์ชันส่งแจ้งเตือนทาง Email
# -------------------------------------------------------------
def send_email_notification(receiver_email, subject, body_text):
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        st.warning("⚠️ ไม่พบคอนฟิก SENDER_EMAIL หรือ SENDER_PASSWORD ใน secrets")
        return

    try:
        if isinstance(receiver_email, list):
            recipients = receiver_email
            to_header = ", ".join(receiver_email)
        else:
            recipients = [receiver_email]
            to_header = receiver_email

        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_header
        msg['Subject'] = subject
        msg.attach(MIMEText(body_text, 'plain', 'utf-8'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, recipients, msg.as_string())
        server.quit()
        print(f"✅ ส่งอีเมลแจ้งเตือนไปยัง {to_header} สำเร็จ")
    except Exception as e:
        print(f"❌ ส่งอีเมลไม่สำเร็จ: {e}")

# -------------------------------------------------------------
# 4. ฟังก์ชันประทับตรา Stamp ลงบน PDF
# -------------------------------------------------------------
def add_approval_stamp(pdf_path, orientation="Portrait"):
    try:
        if not os.path.exists(pdf_path):
            st.error(f"ไม่พบไฟล์ PDF ในระบบ: {pdf_path}")
            return False

        doc = fitz.open(pdf_path)
        page = doc[0]
        
        rect = page.rect
        page_w = rect.width
        page_h = rect.height
        rot = page.rotation

        stamp_w = 140
        stamp_h = 42
        margin = 20

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
        current_date = datetime.now().strftime("%Y-%m-%d")
        stamp_text = f"APPROVED\n{current_date}"

        page.draw_rect(
            stamp_rect, 
            color=(0.8, 0, 0),
            fill=(1, 0.9, 0.9),
            width=2,
            overlay=True
        )

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

        temp_path = pdf_path + ".tmp"
        doc.save(temp_path, clean=True, deflate=True)
        doc.close()

        os.replace(temp_path, pdf_path)
        return True

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการปั๊มตรา Stamp: {e}")
        return False

# -------------------------------------------------------------
# 5. จัดการฐานข้อมูล SQLite
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
# 6. User Authentication & Session State
# -------------------------------------------------------------
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

def get_documents_by_status(statuses=None, prepared_by=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM documents"
    params = []
    conditions = []

    if statuses:
        placeholders = ', '.join(['?'] * len(statuses))
        conditions.append(f"status IN ({placeholders})")
        params.extend(statuses)

    if prepared_by:
        conditions.append("prepared_by = ?")
        params.append(prepared_by)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# -------------------------------------------------------------
# 7. Main Application Logic
# -------------------------------------------------------------
def main_app():
    user = st.session_state.authenticated_user
    st.sidebar.title("👤 ผู้ใช้งานปัจจุบัน")
    st.sidebar.write(f"**ชื่อ:** {user['name']}")
    st.sidebar.write(f"**สิทธิ์ (Role):** `{user['role']}`")
    
    if st.sidebar.button("🚪 Logout", type="primary"):
        st.session_state.authenticated_user = None
        st.rerun()

    # Admin Reset System
    if user["role"] == "Register":
        st.sidebar.markdown("---")
        st.sidebar.subheader("⚙️ ระบบผู้ดูแล (Admin Tools)")
        if st.sidebar.button("⚠️ ล้างข้อมูลทั้งหมด (Reset System)"):
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS documents")
            cursor.execute("DROP TABLE IF EXISTS audit_logs")
            conn.commit()
            conn.close()
            
            if os.path.exists(UPLOAD_DIR):
                for filename in os.listdir(UPLOAD_DIR):
                    file_path = os.path.join(UPLOAD_DIR, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        print(f"Failed to delete {file_path}. Reason: {e}")

            init_db()
            st.sidebar.success("ล้างข้อมูลระบบเรียบร้อยแล้ว!")
            st.rerun()

    st.title("📄 ระบบตรวจสอบ อนุมัติ และขึ้นทะเบียนเอกสาร")
    st.markdown("---")

    # ---------------------------------------------------------
    # ROLE: PREPARE (ผู้จัดทำ)
    # ---------------------------------------------------------
    if user["role"] == "Prepare":
        st.subheader("1. จัดทำและส่งเอกสาร (Prepare)")
        tab1, tab2, tab3 = st.tabs(["📤 ส่งเอกสารใหม่", "❌ เอกสารที่ถูกตีกลับ (Rejected)", "✏️ จัดการ/แก้ไขเอกสารรอตรวจ"])
        
        # TAB 1: ส่งเอกสารใหม่
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
                    
                    subject = f"[แจ้งเตือน] เอกสารใหม่รอการตรวจสอบ: {doc_id}"
                    body = (
                        f"เรียน คุณผู้ตรวจสอบ (Check)\n\n"
                        f"มีเอกสารใหม่ส่งเข้าระบบรอการตรวจสอบ:\n"
                        f"📌 รหัสเอกสาร: {doc_id}\n"
                        f"🏷️ ชนิดเอกสาร: {doc_type}\n"
                        f"📐 แนววางเอกสาร: {orientation_val}\n"
                        f"📝 ชื่อเรื่อง: {doc_title}\n"
                        f"📋 รายละเอียด: {doc_description or '-'}\n"
                        f"👤 ผู้ส่ง: {user['name']}\n\n"
                        f"🔗 คลิกเพื่อดำเนินการ: {APP_URL}"
                    )
                    send_email_notification(USERS["Manoch"]["email"], subject, body)
                    st.success(f"ส่งเอกสารสำเร็จ! รหัสเอกสาร: {doc_id}")
                    st.rerun()

        # TAB 2: แสดงเฉพาะเอกสารที่ถูกตีกลับ (REJECTED)
        with tab2:
            rejected_docs = get_documents_by_status(["REJECTED"])
            if rejected_docs:
                st.warning(f"⚠️ มีเอกสารที่ถูกตีกลับจำนวน {len(rejected_docs)} รายการ")
                for doc in rejected_docs:
                    with st.expander(f"🔴 [{doc['doc_id']}] {doc['title']} (ชนิด: {doc['doc_type']})", expanded=True):
                        st.error(f"**สถานะ:** เอกสารถูกตีกลับ (REJECTED)")
                        st.write(f"**รายละเอียดเดิม:** {doc.get('description', '-')}")
                        
                        # ดึง Log สาเหตุการตีกลับล่าสุด
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("SELECT action_by, comment, timestamp FROM audit_logs WHERE doc_id = ? AND action LIKE '%ตีกลับ%' OR action LIKE '%ไม่อนุมัติ%' ORDER BY id DESC LIMIT 1", (doc['doc_id'],))
                        last_log = cursor.fetchone()
                        conn.close()
                        if last_log:
                            st.info(f"💬 **เหตุผลที่ตีกลับโดย {last_log['action_by']} ({last_log['timestamp']}):** {last_log['comment'] or 'ไม่ได้ระบุเหตุผล'}")

                        st.markdown("---")
                        st.subheader("📝 แก้ไขและส่งเอกสารใหม่")
                        
                        current_type = doc.get('doc_type', 'OM')
                        type_index = ALL_DOC_TYPES.index(current_type) if current_type in ALL_DOC_TYPES else 0
                        new_doc_type = st.selectbox("แก้ไขชนิดเอกสาร", ALL_DOC_TYPES, index=type_index, key=f"rej_edit_type_{doc['doc_id']}")
                        
                        curr_orient = doc.get('orientation', 'Portrait')
                        orient_index = 0 if curr_orient == "Portrait" else 1
                        new_orient = st.radio(
                            "แก้ไขทิศทางแนวเอกสาร",
                            options=["Portrait (แนวตั้ง)", "Landscape (แนวนอน/Drawing)"],
                            index=orient_index,
                            horizontal=True,
                            key=f"rej_edit_orient_{doc['doc_id']}"
                        )
                        new_orient_val = "Portrait" if "Portrait" in new_orient else "Landscape"

                        new_title = st.text_input("แก้ไขชื่อเอกสาร", value=doc['title'], key=f"rej_edit_title_{doc['doc_id']}")
                        new_description = st.text_area("รายละเอียด/เนื้อหาที่แก้ไขเพิ่มเติม", value=doc.get('description', '-'), key=f"rej_edit_desc_{doc['doc_id']}")
                        new_file = st.file_uploader("อัปโหลดไฟล์ PDF ใหม่ (เพื่อแก้ไข)", type=["pdf"], key=f"rej_edit_file_{doc['doc_id']}")
                        
                        col_save, col_del = st.columns([1, 1])
                        if col_save.button("🔄 บันทึกแก้ไข & ส่งกลับไปตรวจสอบอีกครั้ง", key=f"rej_btn_save_{doc['doc_id']}", type="primary"):
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            file_path = doc["file_path"]
                            filename = doc["filename"]
                            if new_file:
                                file_path = os.path.join(UPLOAD_DIR, f"{doc['doc_id']}_{new_file.name}")
                                with open(file_path, "wb") as f: 
                                    f.write(new_file.getbuffer())
                                filename = new_file.name

                            cursor.execute("UPDATE documents SET doc_type = ?, orientation = ?, title = ?, description = ?, filename = ?, file_path = ?, status = 'PENDING_CHECK' WHERE doc_id = ?", (new_doc_type, new_orient_val, new_title, new_description or "-", filename, file_path, doc['doc_id']))
                            conn.commit()
                            conn.close()
                            
                            add_log(doc['doc_id'], user["name"], "แก้ไขเอกสารตีกลับ และส่งกลับไปรอตรวจสอบใหม่")
                            
                            # แจ้งเตือนทาง Mail หาผู้ตรวจซ้ำ
                            subject = f"[แจ้งเตือน] เอกสารแก้ไขส่งกลับมาตรวจสอบ: {doc['doc_id']}"
                            body = f"เอกสารรหัส {doc['doc_id']} ({new_title}) ได้รับการแก้ไขและส่งกลับเข้าสู่ขั้นตอนการตรวจสอบเรียบร้อยแล้ว\n\n🔗 คลิก: {APP_URL}"
                            send_email_notification(USERS["Manoch"]["email"], subject, body)
                            
                            st.success("ส่งเอกสารแก้ไขเรียบร้อยแล้ว!")
                            st.rerun()

                        if col_del.button("🗑️ ยกเลิก/ลบเอกสารนี้", key=f"rej_btn_del_{doc['doc_id']}"):
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM documents WHERE doc_id = ?", (doc['doc_id'],))
                            cursor.execute("DELETE FROM audit_logs WHERE doc_id = ?", (doc['doc_id'],))
                            conn.commit()
                            conn.close()
                            if os.path.exists(doc["file_path"]): 
                                os.remove(doc["file_path"])
                            st.rerun()
            else:
                st.info("🎉 ไม่มีรายการเอกสารที่ถูกตีกลับ")

        # TAB 3: เอกสารที่อยู่ระหว่างรอตรวจสอบ (PENDING_CHECK)
        with tab3:
            pending_docs = get_documents_by_status(["PENDING_CHECK"])
            if pending_docs:
                for doc in pending_docs:
                    with st.expander(f"⚙️ [{doc['doc_id']}] {doc['title']} (สถานะ: รอตรวจสอบ)"):
                        new_title = st.text_input("แก้ไขชื่อเอกสาร", value=doc['title'], key=f"p_edit_title_{doc['doc_id']}")
                        new_description = st.text_area("แก้ไขรายละเอียด", value=doc.get('description', '-'), key=f"p_edit_desc_{doc['doc_id']}")
                        
                        col_save, col_del = st.columns([1, 1])
                        if col_save.button("💾 บันทึกการแก้ไข", key=f"p_btn_save_{doc['doc_id']}", type="primary"):
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute("UPDATE documents SET title = ?, description = ? WHERE doc_id = ?", (new_title, new_description or "-", doc['doc_id']))
                            conn.commit()
                            conn.close()
                            add_log(doc['doc_id'], user["name"], "แก้ไขข้อมูลเอกสารระหว่างรอตรวจ")
                            st.success("บันทึกการแก้ไขเรียบร้อย!")
                            st.rerun()

                        if col_del.button("🗑️ ลบเอกสาร", key=f"p_btn_del_{doc['doc_id']}"):
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM documents WHERE doc_id = ?", (doc['doc_id'],))
                            cursor.execute("DELETE FROM audit_logs WHERE doc_id = ?", (doc['doc_id'],))
                            conn.commit()
                            conn.close()
                            if os.path.exists(doc["file_path"]): os.remove(doc["file_path"])
                            st.rerun()
            else:
                st.info("ไม่มีเอกสารที่รอตรวจสอบอยู่ในขณะนี้")

    # ---------------------------------------------------------
    # ROLE: CHECK (ผู้ตรวจสอบ)
    # ---------------------------------------------------------
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
                        
                        subject = f"[แจ้งเตือน] เอกสารผ่านการตรวจสอบแล้ว: {doc['doc_id']}"
                        body = (
                            f"เรียน คุณผู้อนุมัติ (Approve)\n\n"
                            f"เอกสารได้รับการตรวจสอบเรียบร้อยแล้ว และรอการอนุมัติ:\n"
                            f"📌 รหัสเอกสาร: {doc['doc_id']}\n"
                            f"📝 เรื่อง: {doc['title']}\n"
                            f"🔍 ผู้ตรวจสอบ: {user['name']}\n"
                            f"💬 หมายเหตุ: {comment or '-'}\n\n"
                            f"🔗 คลิกเพื่ออนุมัติเอกสาร: {APP_URL}"
                        )
                        send_email_notification(USERS["Geattisak"]["email"], subject, body)
                        st.rerun()
                        
                    if col2.button("❌ ตีกลับแก้ไข", key=f"c_rej_{doc['doc_id']}"):
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("UPDATE documents SET status = 'REJECTED' WHERE doc_id = ?", (doc['doc_id'],))
                        conn.commit()
                        conn.close()
                        add_log(doc['doc_id'], user["name"], "ตีกลับแก้ไข (Rejected)", comment)
                        
                        subject = f"[แจ้งเตือน] เอกสารของคุณถูกตีกลับให้แก้ไข: {doc['doc_id']}"
                        body = (
                            f"เรียน คุณผู้จัดทำ (Prepare)\n\n"
                            f"เอกสารของคุณไม่ผ่านการตรวจสอบ และถูกตีกลับเพื่อแก้ไข:\n"
                            f"📌 รหัสเอกสาร: {doc['doc_id']}\n"
                            f"📝 เรื่อง: {doc['title']}\n"
                            f"❌ ผู้ตรวจสอบ: {user['name']}\n"
                            f"💬 สาเหตุ/ข้อเสนอแนะ: {comment or '-'}\n\n"
                            f"🔗 คลิกเพื่อแก้ไขเอกสาร: {APP_URL}"
                        )
                        send_email_notification(USERS["Thanawat"]["email"], subject, body)
                        st.rerun()
        else:
            st.info("ไม่มีรายการเอกสารที่รอการตรวจสอบ")

    # ---------------------------------------------------------
    # ROLE: APPROVE (ผู้อนุมัติ)
    # ---------------------------------------------------------
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
                            
                            subject = f"[แจ้งเตือน] เอกสารได้รับการอนุมัติเรียบร้อยแล้ว: {doc['doc_id']}"
                            body = (
                                f"เรียน คุณเจ้าหน้าที่ขึ้นทะเบียน (Register & Print)\n\n"
                                f"เอกสารได้รับการอนุมัติและประทับตรา Stamp เรียบร้อยแล้ว พร้อมขึ้นทะเบียน:\n"
                                f"📌 รหัสเอกสาร: {doc['doc_id']}\n"
                                f"🏷️ ชนิดเอกสาร: {doc_type}\n"
                                f"📝 เรื่อง: {doc['title']}\n"
                                f"✍️ ผู้อนุมัติ: {user['name']}\n"
                                f"💬 ความเห็น: {comment or '-'}\n\n"
                                f"🔗 คลิกเพื่อดำเนินการขึ้นทะเบียน: {APP_URL}"
                            )
                            send_email_notification(USERS["Sudarat"]["email"], subject, body)
                            st.success("อนุมัติเอกสารและประทับตรา Stamp เรียบร้อยแล้ว!")
                            st.rerun()
                        
                    if col2.button("❌ ไม่อนุมัติ", key=f"a_rej_{doc['doc_id']}"):
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("UPDATE documents SET status = 'REJECTED' WHERE doc_id = ?", (doc['doc_id'],))
                        conn.commit()
                        conn.close()
                        add_log(doc['doc_id'], user["name"], "ไม่อนุมัติ (Approved Reject)", comment)
                        
                        subject = f"[แจ้งเตือน] เอกสารไม่ได้รับการอนุมัติ: {doc['doc_id']}"
                        body = (
                            f"เรียน คุณผู้จัดทำ (Prepare)\n\n"
                            f"เอกสารของคุณไม่ได้รับการอนุมัติ:\n"
                            f"📌 รหัสเอกสาร: {doc['doc_id']}\n"
                            f"📝 เรื่อง: {doc['title']}\n"
                            f"❌ ผู้อนุมัติ: {user['name']}\n"
                            f"💬 เหตุผล: {comment or '-'}\n\n"
                            f"🔗 คลิกเพื่อเข้าระบบ: {APP_URL}"
                        )
                        send_email_notification(USERS["Thanawat"]["email"], subject, body)
                        st.rerun()
        else:
            st.info("ไม่มีรายการเอกสารที่รอการอนุมัติ")

    # ---------------------------------------------------------
    # ROLE: REGISTER (ขึ้นทะเบียน & สั่งพิมพ์)
    # ---------------------------------------------------------
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
                            
                            subject = f"[แจ้งเตือน] ขึ้นทะเบียนเอกสารสำเร็จ: {reg_no}"
                            body = (
                                f"เรียน คุณผู้จัดทำ (Prepare)\n\n"
                                f"เอกสารของคุณได้รับการขึ้นทะเบียนและสั่งพิมพ์เรียบร้อยแล้ว:\n"
                                f"🏷️ เลขทะเบียนเอกสาร: {reg_no}\n"
                                f"📌 รหัสอ้างอิง: {doc['doc_id']}\n"
                                f"📝 เรื่อง: {doc['title']}\n"
                                f"👤 ผู้ขึ้นทะเบียน: {user['name']}\n\n"
                                f"🔗 ตรวจสอบสถานะในระบบ: {APP_URL}"
                            )
                            send_email_notification(USERS["Thanawat"]["email"], subject, body)
                            st.success("ขึ้นทะเบียนและบันทึกเรียบร้อยแล้ว")
                            st.rerun()
                        else:
                            st.warning("กรุณาระบุเลขทะเบียนเอกสาร")
        else:
            st.info("ไม่มีรายการเอกสารรอการขึ้นทะเบียน")

    # ---------------------------------------------------------
    # Dashboard & Audit Logs Viewer (สำหรับติดตามสถานะ)
    # ---------------------------------------------------------
    st.markdown("---")
    st.subheader("📊 ตารางติดตามสถานะเอกสารทั้งหมด (DB View)")
    all_docs = get_documents_by_status()
    if all_docs:
        st.dataframe(all_docs, use_container_width=True)
        with st.expander("📜 ดูประวัติการดำเนินการอย่างละเอียด (Audit Logs)"):
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

# -------------------------------------------------------------
# 8. Entry Point
# -------------------------------------------------------------
if st.session_state.authenticated_user is None:
    login_screen()
else:
    main_app()