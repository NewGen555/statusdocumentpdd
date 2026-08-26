import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime
import json
import base64

# --- 1. CONFIGURATION & DATABASE SETUP ---
st.set_page_config(page_title="ระบบเสนออนุมัติเอกสาร (Flow Approve)", layout="wide")

DB_FILE = "document_approval.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # สร้างตารางเอกสาร (ตัด amount ออกแล้ว)
    c.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            doc_id TEXT PRIMARY KEY,
            title TEXT,
            doc_type TEXT,
            prepared_by TEXT,
            status TEXT,
            current_step INTEGER,
            flow_json TEXT,
            pdf_data BLOB,
            pdf_name TEXT,
            created_at TEXT
        )
    ''')
    # สร้างตารางประวัติการอนุมัติ (Audit Log)
    c.execute('''
        CREATE TABLE IF NOT EXISTS approval_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id TEXT,
            action_by TEXT,
            role TEXT,
            action TEXT,
            comment TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- 2. USER SYSTEM (MOCKUP) ---
USERS = {
    "user_prepare": {"name": "สมชาย (ผู้จัดทำ)", "role": "Prepare"},
    "user_check": {"name": "สมศรี (ผู้ตรวจสอบ)", "role": "Check"},
    "user_approve": {"name": "ผอ.วิชัย (ผู้อนุมัติ)", "role": "Approve"},
    "user_register": {"name": "สมศักดิ์ (สารบรรณ/ลงรับ)", "role": "Register"}
}

def login_sidebar():
    st.sidebar.title("👤 เข้าสู่ระบบ (ผู้ใช้งาน)")
    selected_user_key = st.sidebar.selectbox(
        "เลือกผู้ใช้งานปัจจุบัน:",
        options=list(USERS.keys()),
        format_func=lambda x: f"{USERS[x]['name']} [{USERS[x]['role']}]"
    )
    return USERS[selected_user_key]

current_user = login_sidebar()
st.sidebar.divider()
st.sidebar.info(f"ผู้ใช้งาน: **{current_user['name']}**\n\nสิทธิ์: **{current_user['role']}**")

# --- 3. HELPER FUNCTIONS ---
def get_documents_by_status(status_list=None):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if status_list:
        placeholders = ','.join('?' for _ in status_list)
        query = f"SELECT * FROM documents WHERE status IN ({placeholders}) ORDER BY created_at DESC"
        c.execute(query, status_list)
    else:
        c.execute("SELECT * FROM documents ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_logs(doc_id):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM approval_logs WHERE doc_id = ? ORDER BY timestamp ASC", (doc_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_log(doc_id, user_name, role, action, comment):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        INSERT INTO approval_logs (doc_id, action_by, role, action, comment, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (doc_id, user_name, role, action, comment, timestamp))
    conn.commit()
    conn.close()

def display_pdf(pdf_data):
    base64_pdf = base64.b64encode(pdf_data).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="500" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# --- 4. MAIN APPLICATION LOGIC ---
st.title("📄 ระบบเสนออนุมัติเอกสาร (Flow Approval System)")

DEFAULT_FLOW = ["Prepare", "Check", "Approve", "Register"]

# ---------------------------------------------------------
# ROLE: PREPARE (ผู้จัดทำ)
# ---------------------------------------------------------
if current_user["role"] == "Prepare":
    st.subheader("1. จัดทำและเสนอเอกสาร (Prepare)")
    tab1, tab2, tab3 = st.tabs(["📤 เสนอเอกสารใหม่", "✏️ แก้ไข/ลบเอกสารที่ถูกตีกลับ", "🔍 ติดตามสถานะเอกสารของฉัน"])

    with tab1:
        with st.form("create_doc_form", clear_on_submit=True):
            doc_id = f"DOC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            title = st.text_input("ชื่อเรื่อง / หัวข้อเอกสาร")
            doc_type = st.selectbox("ประเภทเอกสาร", ["บันทึกข้อความ", "ใบเบิกจ่าย", "สัญญาจ้าง", "อื่นๆ"])
            uploaded_file = st.file_uploader("แนบไฟล์เอกสาร (PDF เท่านั้น)", type=["pdf"])

            submit = st.form_submit_button("ส่งเอกสารเพื่อเสนออนุมัติ")

            if submit:
                if not title or not uploaded_file:
                    st.error("กรุณากรอกชื่อเรื่องและแนบไฟล์ PDF")
                else:
                    pdf_bytes = uploaded_file.read()
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    c.execute('''
                        INSERT INTO documents (doc_id, title, doc_type, prepared_by, status, current_step, flow_json, pdf_data, pdf_name, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        doc_id, title, doc_type, current_user["name"],
                        "PENDING_CHECK", 1, json.dumps(DEFAULT_FLOW),
                        pdf_bytes, uploaded_file.name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ))
                    conn.commit()
                    conn.close()

                    add_log(doc_id, current_user["name"], current_user["role"], "Submitted", "สร้างและส่งเอกสารเข้าสู่ระบบ")
                    st.success(f"บันทึกและส่งเอกสารรหัส {doc_id} เรียบร้อยแล้ว!")
                    st.rerun()

    with tab2:
        all_editable = get_documents_by_status(["PENDING_CHECK", "REJECTED"])
        editable_docs = [doc for doc in all_editable if doc['prepared_by'] == current_user['name']]

        if editable_docs:
            for doc in editable_docs:
                status_color = "red" if doc['status'] == 'REJECTED' else "orange"
                with st.expander(f"⚙️ {doc['doc_id']} - {doc['title']} (สถานะ: :{status_color}[{doc['status']}])"):
                    st.write(f"**ประเภท:** {doc['doc_type']} | **วันที่สร้าง:** {doc['created_at']}")
                    
                    logs = get_logs(doc['doc_id'])
                    if logs:
                        last_log = logs[-1]
                        if last_log['action'] == 'Rejected':
                            st.warning(f"⚠️ **เหตุผลที่ถูกตีกลับโดย {last_log['action_by']}:** {last_log['comment']}")

                    if doc['pdf_data']:
                        st.download_button("📥 ดาวน์โหลด PDF เดิม", doc['pdf_data'], file_name=doc['pdf_name'], mime="application/pdf", key=f"dl_{doc['doc_id']}")

                    col_edit, col_del = st.columns(2)
                    with col_edit:
                        with st.form(f"edit_form_{doc['doc_id']}"):
                            st.markdown("##### ✏️ แก้ไขและส่งใหม่")
                            new_title = st.text_input("ชื่อเรื่อง", value=doc['title'])
                            new_file = st.file_uploader("แนบไฟล์ PDF ใหม่ (ถ้าต้องการเปลี่ยน)", type=["pdf"], key=f"file_{doc['doc_id']}")
                            resubmit = st.form_submit_button("ส่งเอกสารอีกครั้ง")

                            if resubmit:
                                conn = sqlite3.connect(DB_FILE)
                                c = conn.cursor()
                                if new_file:
                                    pdf_bytes = new_file.read()
                                    pdf_name = new_file.name
                                    c.execute('''
                                        UPDATE documents 
                                        SET title=?, pdf_data=?, pdf_name=?, status='PENDING_CHECK', current_step=1
                                        WHERE doc_id=?
                                    ''', (new_title, pdf_bytes, pdf_name, doc['doc_id']))
                                else:
                                    c.execute('''
                                        UPDATE documents 
                                        SET title=?, status='PENDING_CHECK', current_step=1
                                        WHERE doc_id=?
                                    ''', (new_title, doc['doc_id']))
                                conn.commit()
                                conn.close()
                                add_log(doc['doc_id'], current_user["name"], current_user["role"], "Resubmitted", "แก้ไขเอกสารและส่งเข้าสู่ระบบอีกครั้ง")
                                st.success("ส่งเอกสารใหม่เรียบร้อยแล้ว!")
                                st.rerun()

                    with col_del:
                        st.markdown("##### 🗑️ ยกเลิก/ลบเอกสาร")
                        if st.button("ยืนยันการลบเอกสาร", key=f"del_{doc['doc_id']}", type="primary"):
                            conn = sqlite3.connect(DB_FILE)
                            c = conn.cursor()
                            c.execute("DELETE FROM documents WHERE doc_id=?", (doc['doc_id'],))
                            c.execute("DELETE FROM approval_logs WHERE doc_id=?", (doc['doc_id'],))
                            conn.commit()
                            conn.close()
                            st.success(f"ลบเอกสาร {doc['doc_id']} เรียบร้อยแล้ว")
                            st.rerun()
        else:
            st.info("ไม่พบเอกสารที่ถูกตีกลับหรือรอตรวจสอบของคุณ")

    with tab3:
        all_docs = get_documents_by_status()
        my_docs = [doc for doc in all_docs if doc['prepared_by'] == current_user['name']]
        if my_docs:
            df_my_docs = pd.DataFrame(my_docs)[['doc_id', 'title', 'doc_type', 'status', 'created_at']]
            st.dataframe(df_my_docs, use_container_width=True)
        else:
            st.caption("ยังไม่มีประวัติการส่งเอกสาร")

# ---------------------------------------------------------
# ROLE: CHECK (ผู้ตรวจสอบ)
# ---------------------------------------------------------
elif current_user["role"] == "Check":
    st.subheader("2. ตรวจสอบเอกสาร (Check)")
    pending_docs = get_documents_by_status(["PENDING_CHECK"])

    if pending_docs:
        for doc in pending_docs:
            with st.expander(f"📋 รอตรวจสอบ: {doc['doc_id']} - {doc['title']}"):
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.write(f"**ผู้จัดทำ:** {doc['prepared_by']}")
                    st.write(f"**ประเภท:** {doc['doc_type']}")
                    st.write(f"**วันที่สร้าง:** {doc['created_at']}")
                    if doc['pdf_data']:
                        display_pdf(doc['pdf_data'])

                with col2:
                    st.markdown("### ดำเนินการ")
                    comment = st.text_area("ความเห็น/ข้อเสนอแนะ", key=f"com_{doc['doc_id']}")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("✅ ตรวจสอบผ่าน (ส่งต่อ)", key=f"pass_{doc['doc_id']}", type="primary"):
                            conn = sqlite3.connect(DB_FILE)
                            c = conn.cursor()
                            c.execute("UPDATE documents SET status='PENDING_APPROVE', current_step=2 WHERE doc_id=?", (doc['doc_id'],))
                            conn.commit()
                            conn.close()
                            add_log(doc['doc_id'], current_user["name"], current_user["role"], "Checked & Passed", comment)
                            st.success("ส่งต่อให้ผู้อนุมัติเรียบร้อยแล้ว")
                            st.rerun()
                    with c2:
                        if st.button("❌ ตีกลับแก้ไข", key=f"reject_{doc['doc_id']}"):
                            if not comment:
                                st.error("กรุณาระบุเหตุผลในการตีกลับ")
                            else:
                                conn = sqlite3.connect(DB_FILE)
                                c = conn.cursor()
                                c.execute("UPDATE documents SET status='REJECTED' WHERE doc_id=?", (doc['doc_id'],))
                                conn.commit()
                                conn.close()
                                add_log(doc['doc_id'], current_user["name"], current_user["role"], "Rejected", comment)
                                st.warning("ตีกลับเอกสารเรียบร้อยแล้ว")
                                st.rerun()
    else:
        st.info("ไม่มีเอกสารค้างตรวจสอบในขณะนี้")

# ---------------------------------------------------------
# ROLE: APPROVE (ผู้อนุมัติ)
# ---------------------------------------------------------
elif current_user["role"] == "Approve":
    st.subheader("3. พิจารณาอนุมัติเอกสาร (Approve)")
    pending_docs = get_documents_by_status(["PENDING_APPROVE"])

    if pending_docs:
        for doc in pending_docs:
            with st.expander(f"⚖️ รออนุมัติ: {doc['doc_id']} - {doc['title']}"):
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.write(f"**ผู้จัดทำ:** {doc['prepared_by']}")
                    st.write(f"**ประเภท:** {doc['doc_type']}")
                    if doc['pdf_data']:
                        display_pdf(doc['pdf_data'])

                with col2:
                    st.markdown("### ประวัติก่อนหน้า")
                    logs = get_logs(doc['doc_id'])
                    for l in logs:
                        st.text(f"[{l['timestamp']}] {l['role']} ({l['action_by']}): {l['action']} - {l['comment']}")

                    st.markdown("---")
                    comment = st.text_area("ความเห็นผู้อนุมัติ", key=f"app_com_{doc['doc_id']}")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("👍 อนุมัติ", key=f"app_{doc['doc_id']}", type="primary"):
                            conn = sqlite3.connect(DB_FILE)
                            c = conn.cursor()
                            c.execute("UPDATE documents SET status='APPROVED', current_step=3 WHERE doc_id=?", (doc['doc_id'],))
                            conn.commit()
                            conn.close()
                            add_log(doc['doc_id'], current_user["name"], current_user["role"], "Approved", comment)
                            st.success("อนุมัติเอกสารเรียบร้อยแล้ว")
                            st.rerun()
                    with c2:
                        if st.button("❌ ตีกลับ", key=f"rej_app_{doc['doc_id']}"):
                            if not comment:
                                st.error("กรุณาระบุเหตุผลในการตีกลับ")
                            else:
                                conn = sqlite3.connect(DB_FILE)
                                c = conn.cursor()
                                c.execute("UPDATE documents SET status='REJECTED' WHERE doc_id=?", (doc['doc_id'],))
                                conn.commit()
                                conn.close()
                                add_log(doc['doc_id'], current_user["name"], current_user["role"], "Rejected", comment)
                                st.warning("ตีกลับเอกสารเรียบร้อยแล้ว")
                                st.rerun()
    else:
        st.info("ไม่มีเอกสารรออนุมัติในขณะนี้")

# ---------------------------------------------------------
# ROLE: REGISTER (งานสารบรรณ/ลงรับ)
# ---------------------------------------------------------
elif current_user["role"] == "Register":
    st.subheader("4. ลงรับเอกสารและจัดเก็บ (Register / Archive)")
    approved_docs = get_documents_by_status(["APPROVED"])

    if approved_docs:
        for doc in approved_docs:
            with st.expander(f"📦 รอลงรับ: {doc['doc_id']} - {doc['title']}"):
                st.write(f"**ผู้จัดทำ:** {doc['prepared_by']} | **ประเภท:** {doc['doc_type']}")
                if st.button("📥 ลงรับและจัดเก็บสำเร็จ", key=f"reg_{doc['doc_id']}", type="primary"):
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    c.execute("UPDATE documents SET status='REGISTERED', current_step=4 WHERE doc_id=?", (doc['doc_id'],))
                    conn.commit()
                    conn.close()
                    add_log(doc['doc_id'], current_user["name"], current_user["role"], "Registered", "ลงรับและเสร็จสิ้นกระบวนการ")
                    st.success("ลงรับเอกสารเสร็จสมบูรณ์")
                    st.rerun()
    else:
        st.info("ไม่มีเอกสารที่อนุมัติแล้วรอลงรับ")

# --- 5. AUDIT LOG & ALL DOCUMENTS TRACKER (FOR ALL USERS) ---
st.divider()
st.subheader("📊 ติดตามสถานะและประวัติเอกสารทั้งหมดในระบบ")
all_docs = get_documents_by_status()

if all_docs:
    df_all = pd.DataFrame(all_docs)[['doc_id', 'title', 'doc_type', 'prepared_by', 'status', 'created_at']]
    st.dataframe(df_all, use_container_width=True)

    selected_doc_id = st.selectbox("เลือกเอกสารเพื่อดูประวัติการดำเนินการ (Audit Trail):", [d['doc_id'] for d in all_docs])
    if selected_doc_id:
        logs = get_logs(selected_doc_id)
        if logs:
            st.write(f"**ประวัติการดำเนินการของ {selected_doc_id}:**")
            st.table(pd.DataFrame(logs)[['timestamp', 'role', 'action_by', 'action', 'comment']])
else:
    st.write("ยังไม่มีข้อมูลเอกสารในระบบ")