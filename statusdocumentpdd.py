from datetime import datetime
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import fitz   # PyMuPDF
import sqlite3
import streamlit as st

# -------------------------------------------------------------
# 1. การตั้งค่า Web App และ URL ระบบ
# -------------------------------------------------------------
st.set_page_config(
    page_title="Document Approval System", page_icon="📄", layout="wide"
)

APP_URL = "https://statusdocumentpdd-df84ykbbpe9wc8pchnhjpf.streamlit.app/"
UPLOAD_DIR = "./uploaded_documents"
DB_FILE = "document_approval.db"
os.makedirs(UPLOAD_DIR, exist_ok=True)

DOC_TYPES_PORTRAIT = ["OM", "PROCESS FLOW", "MATERIAL SPEC"]
DOC_TYPES_LANDSCAPE = ["ACC DWG", "MASTER DWG.", "FMEA"]
ALL_DOC_TYPES = DOC_TYPES_PORTRAIT + DOC_TYPES_LANDSCAPE

# -------------------------------------------------------------
# 2. โหลด Secrets และระบบส่งอีเมล HTML พร้อมแนบไฟล์ PDF
# -------------------------------------------------------------
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

try:
    SENDER_EMAIL = st.secrets["email"]["SENDER_EMAIL"]
    SENDER_PASSWORD = st.secrets["email"]["SENDER_PASSWORD"]
    USERS = dict(st.secrets["users"])
except Exception as e:
    st.error(
        f"⚠️ ไม่สามารถโหลดค่าจาก st.secrets ได้: {e}\nกรุณาตรวจสอบไฟล์"
        " .streamlit/secrets.toml"
    )
    st.stop()


def format_email_str(email_data):
    if isinstance(email_data, list):
        return ", ".join(email_data)
    return str(email_data) if email_data else ""


def send_email_notification(receiver_email, subject, body_html, file_path=None):
    if not SENDER_EMAIL or not SENDER_PASSWORD or not receiver_email:
        return

    try:
        if isinstance(receiver_email, str):
            recipients = [
                e.strip() for e in receiver_email.split(",") if e.strip()
            ]
        else:
            recipients = receiver_email

        # ใช้ 'mixed' เพื่อให้สามารถส่งข้อความ HTML และแนบไฟล์ไปพร้อมกันได้
        msg = MIMEMultipart("mixed")
        msg["From"] = SENDER_EMAIL
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject

        # แนบเนื้อหา HTML
        msg_body = MIMEMultipart("alternative")
        msg_body.attach(MIMEText(body_html, "html", "utf-8"))
        msg.attach(msg_body)

        # แนบไฟล์ PDF (ถ้ามีระบุ path ของไฟล์มาด้วย)
        if file_path and os.path.exists(file_path):
            with open(file_path, "rb") as f:
                attach_part = MIMEApplication(f.read(), Name=os.path.basename(file_path))
            attach_part[
                "Content-Disposition"
            ] = f'attachment; filename="{os.path.basename(file_path)}"'
            msg.attach(attach_part)

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, recipients, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"❌ ส่งอีเมลไม่สำเร็จ: {e}")


def send_next_step_email(
    target_email, doc_id, doc_title, role_name, action_hint="ตรวจสอบ/อนุมัติ", file_path=None
):
    if not target_email:
        return
    email_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h3 style="color: #004085;">เรียน ท่านผู้มีสิทธิ์ ({role_name})</h3>
        <p>มีเอกสารที่เกี่ยวข้องกับท่าน รายละเอียดดังนี้:</p>
        <ul>
          <li><b>รหัสเอกสาร:</b> {doc_id}</li>
          <li><b>ชื่อเรื่อง:</b> {doc_title}</li>
          <li><b>สถานะ:</b> {action_hint} ({role_name})</li>
        </ul>
        <p>คุณสามารถตรวจสอบจากไฟล์ PDF ที่แนบมาพร้อมกับอีเมลฉบับนี้ หรือคลิกที่ปุ่มด้านล่างเพื่อเข้าสู่ระบบ:</p>
        <p style="margin-top: 20px;">
          <a href="{APP_URL}" 
             style="background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
             👉 คลิกที่นี่เพื่อเข้าสู่ระบบ PDD System
          </a>
        </p>
      </body>
    </html>
    """
    send_email_notification(
        target_email, f"[PDD System] แจ้งเตือนเอกสาร ({role_name}): {doc_title}", email_body, file_path=file_path
    )


def display_pdf_download_link(file_path, filename, key=None):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            pdf_bytes = f.read()

        st.download_button(
            label=f"📥 ดาวน์โหลด / เปิดดูไฟล์ PDF ({filename})",
            data=pdf_bytes,
            file_name=filename,
            mime="application/pdf",
            type="primary",
            key=key,
        )
    else:
        st.warning("⚠️ ไม่พบไฟล์ PDF ในระบบ")


# -------------------------------------------------------------
# 3. Dynamic Stamp (ตารางลงนาม + ตราประทับ APPROVED สีแดง)
# -------------------------------------------------------------
def add_approval_stamp_dynamic(pdf_path, doc_info):
    try:
        if not os.path.exists(pdf_path):
            return False

        doc = fitz.open(pdf_path)
        page = doc[0]
        rect = page.rect
        page_w, page_h = rect.width, rect.height

        if doc_info["doc_type"] == "FMEA":
            signatures = [
                ("PREPARED", doc_info.get("prepared_by", "-")),
                ("PDD", doc_info.get("chk1_name", "-")),
                ("PCS", doc_info.get("chk2_name", "-")),
                ("QCD", doc_info.get("chk3_name", "-")),
                ("PRD", doc_info.get("chk4_name", "-")),
                ("PCD", doc_info.get("chk5_name", "-")),
            ]
        else:
            signatures = [
                ("PREPARED", doc_info.get("prepared_by", "-")),
                ("CHECKED", doc_info.get("checked_by", "-")),
                ("APPROVED", doc_info.get("approved_by", "-")),
            ]

        num_cols = len(signatures)
        col_w = 55 if num_cols == 6 else 75
        box_h = 42
        total_w = col_w * num_cols

        margin_right = 15
        margin_top = 15
        x0 = page_w - total_w - margin_right
        y0 = margin_top

        current_date = datetime.now().strftime("%Y-%m-%d")

        for idx, (role_title, name) in enumerate(signatures):
            col_x0 = x0 + (idx * col_w)
            col_x1 = col_x0 + col_w

            r_header = fitz.Rect(col_x0, y0, col_x1, y0 + 12)
            page.draw_rect(
                r_header, color=(0.1, 0.1, 0.5), fill=(0.9, 0.95, 1.0), width=0.6
            )
            page.insert_textbox(
                r_header,
                role_title,
                fontsize=5.5,
                fontname="Helvetica",
                color=(0.1, 0.1, 0.5),
                align=fitz.TEXT_ALIGN_CENTER,
            )

            r_body = fitz.Rect(col_x0, y0 + 12, col_x1, y0 + 30)
            page.draw_rect(
                r_body, color=(0.1, 0.1, 0.5), fill=(1, 1, 1), width=0.6
            )

            display_status = f"SIGNED\n{name}" if name != "-" else "-"
            text_color = (0, 0.4, 0) if name != "-" else (0.5, 0.5, 0.5)

            page.insert_textbox(
                r_body,
                display_status,
                fontsize=5.5,
                fontname="Helvetica",
                color=text_color,
                align=fitz.TEXT_ALIGN_CENTER,
            )

            r_footer = fitz.Rect(col_x0, y0 + 30, col_x1, y0 + box_h)
            page.draw_rect(
                r_footer,
                color=(0.1, 0.1, 0.5),
                fill=(0.95, 0.95, 0.95),
                width=0.6,
            )
            page.insert_textbox(
                r_footer,
                current_date if name != "-" else "-",
                fontsize=5,
                fontname="Helvetica",
                color=(0.3, 0.3, 0.3),
                align=fitz.TEXT_ALIGN_CENTER,
            )

        is_fully_approved = (
            doc_info["doc_type"] == "FMEA"
            and all(
                doc_info.get(f"chk{i}_name", "-") != "-" for i in range(1, 6)
            )
        ) or (
            doc_info["doc_type"] != "FMEA"
            and doc_info.get("approved_by", "-") != "-"
        )

        if is_fully_approved:
            stamp_w, stamp_h = 130, 45
            stamp_x0 = page_w - stamp_w - 20
            stamp_y0 = y0 + box_h + 15
            stamp_rect = fitz.Rect(
                stamp_x0, stamp_y0, stamp_x0 + stamp_w, stamp_y0 + stamp_h
            )

            red_color = (0.85, 0.1, 0.1)

            page.draw_rect(stamp_rect, color=red_color, width=2.5)
            inner_rect = fitz.Rect(
                stamp_x0 + 3,
                stamp_y0 + 3,
                stamp_x0 + stamp_w - 3,
                stamp_y0 + stamp_h - 3,
            )
            page.draw_rect(inner_rect, color=red_color, width=1.0)

            text_rect = fitz.Rect(
                stamp_x0, stamp_y0 + 4, stamp_x0 + stamp_w, stamp_y0 + 30
            )
            page.insert_textbox(
                text_rect,
                "APPROVED",
                fontsize=13,
                fontname="Helvetica-Bold",
                color=red_color,
                align=fitz.TEXT_ALIGN_CENTER,
            )

            date_rect = fitz.Rect(
                stamp_x0, stamp_y0 + 30, stamp_x0 + stamp_w, stamp_y0 + 42
            )
            page.insert_textbox(
                date_rect,
                f"DATE: {current_date}",
                fontsize=7,
                fontname="Helvetica-Bold",
                color=red_color,
                align=fitz.TEXT_ALIGN_CENTER,
            )

        temp_path = pdf_path + ".tmp"
        doc.save(temp_path, clean=True, deflate=True)
        doc.close()

        os.replace(temp_path, pdf_path)
        return True
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการสร้าง Stamp: {e}")
        return False


# -------------------------------------------------------------
# 4. Database Initialization
# -------------------------------------------------------------
def get_db_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
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
            chk1_name TEXT DEFAULT '-',
            chk2_name TEXT DEFAULT '-',
            chk3_name TEXT DEFAULT '-',
            chk4_name TEXT DEFAULT '-',
            chk5_name TEXT DEFAULT '-',
            checker_email TEXT DEFAULT '',
            checker1_email TEXT DEFAULT '',
            checker2_email TEXT DEFAULT '',
            checker3_email TEXT DEFAULT '',
            checker4_email TEXT DEFAULT '',
            checker5_email TEXT DEFAULT '',
            approver_email TEXT DEFAULT '',
            register_email TEXT DEFAULT '',
            reject_comment TEXT DEFAULT '-',
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cols_to_check = [
        "chk1_name",
        "chk2_name",
        "chk3_name",
        "chk4_name",
        "chk5_name",
        "checker1_email",
        "checker2_email",
        "checker3_email",
        "checker4_email",
        "checker5_email",
        "reject_comment",
    ]
    for col in cols_to_check:
        try:
            cursor.execute(f"ALTER TABLE documents ADD COLUMN {col} TEXT DEFAULT '-'")
        except sqlite3.OperationalError:
            pass

    conn.commit()
    conn.close()


init_db()

# -------------------------------------------------------------
# 5. Session State & Login Screen
# -------------------------------------------------------------
if "authenticated_user" not in st.session_state:
    st.session_state.authenticated_user = None


def login_screen():
    st.markdown(
        "<h2 style='text-align: center;'>🔐 เข้าสู่ระบบ อนุมัติเอกสาร PDD</h2>",
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button(
                "Log In", use_container_width=True, type="primary"
            )
            if submit:
                if (
                    username in USERS
                    and str(USERS[username]["password"]) == str(password)
                ):
                    st.session_state.authenticated_user = {
                        "username": username,
                        "role": USERS[username]["role"],
                        "name": USERS[username]["name"],
                        "email": USERS[username].get("email", ""),
                    }
                    st.rerun()
                else:
                    st.error("Username หรือ Password ไม่ถูกต้อง")


def get_documents_by_status(statuses=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM documents"
    params = []
    if statuses:
        placeholders = ", ".join(["?"] * len(statuses))
        query += f" WHERE status IN ({placeholders})"
        params.extend(statuses)
    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# -------------------------------------------------------------
# 6. Main App Process
# -------------------------------------------------------------
def main_app():
    user = st.session_state.authenticated_user
    st.sidebar.title("👤 ผู้ใช้งานปัจจุบัน")
    st.sidebar.write(f"**ชื่อ:** {user['name']}")
    st.sidebar.write(f"**ตำแหน่ง:** `{user['role']}`")

    if st.sidebar.button("🚪 Logout", type="primary"):
        st.session_state.authenticated_user = None
        st.rerun()

    st.title("📄 ระบบตรวจสอบ อนุมัติ และขึ้นทะเบียนเอกสาร PDD")
    st.markdown("---")

    # ---------------------------------------------------------
    # PREPARE ROLE
    # ---------------------------------------------------------
    if user["role"] == "Prepare":
        st.subheader("1. จัดทำและส่งเอกสาร (Prepare)")

        rejected_docs = [
            d
            for d in get_documents_by_status(["REJECTED"])
            if d["prepared_by"] == user["name"]
        ]
        if rejected_docs:
            st.error("⚠️ มีเอกสารที่ถูกตีกลับมาแก้ไข กรุณาตรวจสอบคอมเมนต์ด้านล่าง")
            for r_doc in rejected_docs:
                with st.expander(
                    f"❌ เอกสารถูกตีกลับ: [{r_doc['doc_id']}] {r_doc['title']}"
                ):
                    st.write(
                        f"**💬 คอมเมนต์จากผู้ตรวจสอบ/ผู้อนุมัติ:**"
                        f" `{r_doc.get('reject_comment', '-')}`"
                    )
                    st.write(
                        "*(ท่านสามารถส่งเอกสารใหม่โดยใช้รหัสหรือชื่อเรื่องเดิม หรือปรับปรุงไฟล์เพื่อส่งใหม่ได้)*"
                    )
                    if st.button("🗑️ ลบรายการที่ถูกตีกลับนี้ทิ้ง", key=f"del_rej_{r_doc['doc_id']}"):
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM documents WHERE doc_id = ?", (r_doc["doc_id"],))
                        conn.commit()
                        conn.close()
                        st.success("ลบรายการเรียบร้อยแล้ว")
                        st.rerun()

        doc_type = st.selectbox("ชนิดเอกสาร (Document Type)", ALL_DOC_TYPES)
        orientation_val = (
            "Landscape" if doc_type in DOC_TYPES_LANDSCAPE else "Portrait"
        )

        with st.form("upload_form", clear_on_submit=True):
            doc_title = st.text_input("ชื่อเรื่อง/ชื่อเอกสาร")
            doc_description = st.text_area("รายละเอียดการจัดทำ/แก้ไข")
            uploaded_file = st.file_uploader("อัปโหลดไฟล์ PDF", type=["pdf"])

            st.markdown("---")
            if doc_type == "FMEA":
                st.markdown(
                    "##### 📧 กำหนดอีเมลทีมผู้ตรวจสอบ FMEA (ลำดับการส่ง: PDD ➡️ PCS ➡️ QCD"
                    " ➡️ PRD ➡️ PCD)"
                )
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    c1 = st.text_input(
                        "PDD (Manoch)",
                        value=format_email_str(
                            USERS.get("Manoch", {}).get("email", "")
                        ),
                    )
                with col2:
                    c2 = st.text_input(
                        "PCS (Geattisak)",
                        value=format_email_str(
                            USERS.get("Geattisak_Check", {}).get("email", "")
                        ),
                    )
                with col3:
                    c3 = st.text_input(
                        "QCD (Maitree)",
                        value=format_email_str(
                            USERS.get("Maitree", {}).get("email", "")
                        ),
                    )
                with col4:
                    c4 = st.text_input(
                        "PRD (Suriya)",
                        value=format_email_str(
                            USERS.get("Suriya", {}).get("email", "")
                        ),
                    )
                with col5:
                    c5 = st.text_input(
                        "PCD (Umaporn)",
                        value=format_email_str(
                            USERS.get("Umaporn", {}).get("email", "")
                        ),
                    )

                reg_email = st.text_input(
                    "Register Email",
                    value=format_email_str(USERS.get("Sudarat", {}).get("email", "")),
                )
            else:
                st.markdown(
                    "##### 📧 กำหนดอีเมลผู้รับผิดชอบ (ลำดับการส่ง: Checker ➡️ Approver ➡️"
                    " Register)"
                )
                col_c, col_a, col_r = st.columns(3)
                with col_c:
                    chk_email = st.text_input(
                        "Checker Email",
                        value=format_email_str(
                            USERS.get("Manoch", {}).get("email", "")
                        ),
                    )
                with col_a:
                    app_email = st.text_input(
                        "Approver Email",
                        value=format_email_str(
                            USERS.get("Geattisak", {}).get("email", "")
                        ),
                    )
                with col_r:
                    reg_email = st.text_input(
                        "Register Email",
                        value=format_email_str(
                            USERS.get("Sudarat", {}).get("email", "")
                        ),
                    )

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

                if doc_type == "FMEA":
                    cursor.execute(
                        """
                            INSERT INTO documents 
                            (doc_id, doc_type, orientation, title, description, filename, file_path, prepared_by, 
                             checker1_email, checker2_email, checker3_email, checker4_email, checker5_email, register_email, status)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            doc_id,
                            doc_type,
                            orientation_val,
                            doc_title,
                            doc_description or "-",
                            uploaded_file.name,
                            file_path,
                            user["name"],
                            c1,
                            c2,
                            c3,
                            c4,
                            c5,
                            reg_email,
                            "PENDING_CHK1",
                        ),
                    )

                    conn.commit()
                    conn.close()

                    # แนบไฟล์ PDF ไปกับอีเมลแจ้งเตือน
                    send_next_step_email(c1, doc_id, doc_title, "PDD (Manoch)", file_path=file_path)
                else:
                    cursor.execute(
                        """
                            INSERT INTO documents 
                            (doc_id, doc_type, orientation, title, description, filename, file_path, prepared_by, 
                             checker_email, approver_email, register_email, status)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            doc_id,
                            doc_type,
                            orientation_val,
                            doc_title,
                            doc_description or "-",
                            uploaded_file.name,
                            file_path,
                            user["name"],
                            chk_email,
                            app_email,
                            reg_email,
                            "PENDING_CHECK",
                        ),
                    )

                    conn.commit()
                    conn.close()

                    # แนบไฟล์ PDF ไปกับอีเมลแจ้งเตือน
                    send_next_step_email(chk_email, doc_id, doc_title, "Checker", file_path=file_path)

                st.success(f"ส่งเอกสารสำเร็จ! รหัสเอกสาร: {doc_id}")
                st.rerun()

    # ---------------------------------------------------------
    # CHECK ROLE
    # ---------------------------------------------------------
    elif user["role"] == "Check":
        st.subheader("2. ตรวจสอบเอกสาร (Check)")

        pending_list = get_documents_by_status([
            "PENDING_CHECK",
            "PENDING_CHK1",
            "PENDING_CHK2",
            "PENDING_CHK3",
            "PENDING_CHK4",
            "PENDING_CHK5",
        ])

        if not pending_list:
            st.info("ไม่มีเอกสารที่รอการตรวจสอบในขณะนี้")

        for doc in pending_list:
            with st.expander(
                f"📌 [{doc['doc_type']}] {doc['doc_id']} - {doc['title']} (สถานะ:"
                f" {doc['status']})"
            ):
                st.write(f"**ผู้จัดทำ:** {doc['prepared_by']}")
                st.write(f"**รายละเอียด:** {doc['description']}")

                st.markdown("---")
                display_pdf_download_link(
                    doc["file_path"], doc["filename"], key=f"dl_check_{doc['doc_id']}"
                )
                st.markdown("---")

                if doc["doc_type"] == "FMEA":
                    st.markdown("##### 👥 สถานะผู้ตรวจสอบ FMEA:")
                    c1_s = (
                        "✅ " + doc["chk1_name"]
                        if doc["chk1_name"] != "-"
                        else "⏳ รอการตรวจสอบ"
                    )
                    c2_s = (
                        "✅ " + doc["chk2_name"]
                        if doc["chk2_name"] != "-"
                        else "⏳ รอการตรวจสอบ"
                    )
                    c3_s = (
                        "✅ " + doc["chk3_name"]
                        if doc["chk3_name"] != "-"
                        else "⏳ รอการตรวจสอบ"
                    )
                    c4_s = (
                        "✅ " + doc["chk4_name"]
                        if doc["chk4_name"] != "-"
                        else "⏳ รอการตรวจสอบ"
                    )
                    c5_s = (
                        "✅ " + doc["chk5_name"]
                        if doc["chk5_name"] != "-"
                        else "⏳ รอการตรวจสอบ"
                    )

                    st.write(
                        f"1. PDD (Manoch): {c1_s} | 2. PCS (Geattisak): {c2_s} | 3. QCD"
                        f" (Maitree): {c3_s}"
                    )
                    st.write(f"4. PRD (Suriya): {c4_s} | 5. PCD (Umaporn): {c5_s}")

                    status = doc["status"]
                    can_approve = False
                    next_status = ""
                    next_email = ""
                    next_role = ""
                    chk_field = ""

                    if status == "PENDING_CHK1" and user["name"] == "Manoch T.":
                        can_approve = True
                        chk_field = "chk1_name"
                        next_status = "PENDING_CHK2"
                        next_email = doc["checker2_email"]
                        next_role = "PCS (Geattisak)"
                    elif status == "PENDING_CHK2" and user["name"] == "Geattisak S.":
                        can_approve = True
                        chk_field = "chk2_name"
                        next_status = "PENDING_CHK3"
                        next_email = doc["checker3_email"]
                        next_role = "QCD (Maitree)"
                    elif status == "PENDING_CHK3" and user["name"] == "Maitree":
                        can_approve = True
                        chk_field = "chk3_name"
                        next_status = "PENDING_CHK4"
                        next_email = doc["checker4_email"]
                        next_role = "PRD (Suriya)"
                    elif status == "PENDING_CHK4" and user["name"] == "Suriya":
                        can_approve = True
                        chk_field = "chk4_name"
                        next_status = "PENDING_CHK5"
                        next_email = doc["checker5_email"]
                        next_role = "PCD (Umaporn)"
                    elif status == "PENDING_CHK5" and user["name"] == "Umaporn":
                        can_approve = True
                        chk_field = "chk5_name"
                        next_status = "PENDING_REGISTER"
                        next_email = doc["register_email"]
                        next_role = "Register"

                    if can_approve:
                        col_b1, col_b2 = st.columns(2)
                        with col_b1:
                            if st.button(
                                f"✅ ผ่านการตรวจสอบ ({user['name']})",
                                key=f"c_fmea_{doc['doc_id']}",
                                type="primary",
                            ):
                                conn = get_db_connection()
                                cursor = conn.cursor()

                                if next_status == "PENDING_REGISTER":
                                    cursor.execute(
                                        f"""UPDATE documents 
                                            SET {chk_field} = ?, 
                                                status = ?, 
                                                checked_by = 'FMEA Team Checked', 
                                                approved_by = 'AUTO_APPROVED' 
                                            WHERE doc_id = ?""",
                                        (user["name"], next_status, doc["doc_id"]),
                                    )
                                else:
                                    cursor.execute(
                                        f"UPDATE documents SET {chk_field} = ?, status = ? WHERE doc_id = ?",
                                        (user["name"], next_status, doc["doc_id"]),
                                    )

                                conn.commit()

                                cursor.execute(
                                    "SELECT * FROM documents WHERE doc_id = ?", (doc["doc_id"],)
                                )
                                updated_row = cursor.fetchone()
                                if updated_row:
                                    updated_doc = dict(updated_row)
                                    add_approval_stamp_dynamic(updated_doc["file_path"], updated_doc)

                                conn.close()

                                if next_email and next_email.strip():
                                    action_text = (
                                        "ขึ้นทะเบียนเอกสาร"
                                        if next_status == "PENDING_REGISTER"
                                        else "ตรวจสอบ"
                                    )
                                    # แนบไฟล์ PDF ล่าสุดไปกับอีเมลแจ้งเตือน
                                    send_next_step_email(
                                        next_email,
                                        doc["doc_id"],
                                        doc["title"],
                                        next_role,
                                        action_text,
                                        file_path=doc["file_path"],
                                    )

                                st.success("บันทึกการลงนามเรียบร้อย")
                                st.rerun()

                        with col_b2:
                            reject_reason = st.text_input(
                                "ระบุเหตุผลที่ตีกลับ", key=f"rej_reason_fmea_{doc['doc_id']}"
                            )
                            if st.button(
                                "❌ ตีกลับให้แก้ไข",
                                key=f"btn_rej_fmea_{doc['doc_id']}",
                                type="secondary",
                            ):
                                conn = get_db_connection()
                                cursor = conn.cursor()
                                cursor.execute(
                                    """UPDATE documents 
                                       SET status = 'REJECTED', reject_comment = ? 
                                       WHERE doc_id = ?""",
                                    (f"{user['name']} (Reject): {reject_reason}", doc["doc_id"]),
                                )
                                conn.commit()
                                conn.close()
                                st.warning("ตีกลับเอกสารไปยังผู้จัดทำเรียบร้อยแล้ว")
                                st.rerun()
                    else:
                        st.info("ℹ️ ยังไม่ถึงลำดับการอนุมัติของคุณ หรือคุณไม่มีสิทธิ์ในขั้นตอนนี้")

                else:
                    if doc["status"] == "PENDING_CHECK":
                        col_b1, col_b2 = st.columns(2)
                        with col_b1:
                            if st.button(
                                "✅ ผ่านการตรวจสอบ",
                                key=f"c_pass_{doc['doc_id']}",
                                type="primary",
                            ):
                                conn = get_db_connection()
                                cursor = conn.cursor()
                                cursor.execute(
                                    "UPDATE documents SET status = 'PENDING_APPROVE', checked_by"
                                    " = ? WHERE doc_id = ?",
                                    (user["name"], doc["doc_id"]),
                                )
                                conn.commit()
                                conn.close()

                                # แนบไฟล์ PDF ไปกับอีเมลแจ้งเตือนไปยัง Approver
                                send_next_step_email(
                                    doc["approver_email"],
                                    doc["doc_id"],
                                    doc["title"],
                                    "Approver",
                                    "อนุมัติเอกสาร",
                                    file_path=doc["file_path"],
                                )
                                st.success("ตรวจสอบผ่านเรียบร้อย! ส่งอีเมลต่อไปยังผู้อนุมัติแล้ว")
                                st.rerun()

                        with col_b2:
                            reject_reason = st.text_input(
                                "ระบุเหตุผลที่ตีกลับ", key=f"rej_reason_gen_{doc['doc_id']}"
                            )
                            if st.button(
                                "❌ ตีกลับให้แก้ไข",
                                key=f"btn_rej_gen_{doc['doc_id']}",
                                type="secondary",
                            ):
                                conn = get_db_connection()
                                cursor = conn.cursor()
                                cursor.execute(
                                    """UPDATE documents 
                                       SET status = 'REJECTED', reject_comment = ? 
                                       WHERE doc_id = ?""",
                                    (f"{user['name']} (Reject): {reject_reason}", doc["doc_id"]),
                                )
                                conn.commit()
                                conn.close()
                                st.warning("ตีกลับเอกสารไปยังผู้จัดทำเรียบร้อยแล้ว")
                                st.rerun()

    # ---------------------------------------------------------
    # APPROVE ROLE (สำหรับเอกสารทั่วไป)
    # ---------------------------------------------------------
    elif user["role"] == "Approve":
        st.subheader("3. อนุมัติเอกสารและประทับตรา Stamp (Approve)")
        pending_list = get_documents_by_status(["PENDING_APPROVE"])
        if not pending_list:
            st.info("ไม่มีเอกสารที่รอการอนุมัติในขณะนี้")
        for doc in pending_list:
            with st.expander(f"📌 [{doc['doc_type']}] {doc['doc_id']} - {doc['title']}"):
                st.write(f"**ผู้จัดทำ:** {doc['prepared_by']}")
                st.write(f"**ผู้ตรวจสอบ:** {doc['checked_by']}")

                st.markdown("---")
                display_pdf_download_link(
                    doc["file_path"], doc["filename"], key=f"dl_approve_{doc['doc_id']}"
                )
                st.markdown("---")

                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    if st.button(
                        "✅ อนุมัติและประทับตรา Stamp",
                        key=f"a_btn_{doc['doc_id']}",
                        type="primary",
                    ):
                        doc["approved_by"] = user["name"]
                        stamp_ok = add_approval_stamp_dynamic(doc["file_path"], doc)
                        if stamp_ok:
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute(
                                "UPDATE documents SET status = 'PENDING_REGISTER', approved_by ="
                                " ? WHERE doc_id = ?",
                                (user["name"], doc["doc_id"]),
                            )
                            conn.commit()
                            conn.close()

                            # แนบไฟล์ PDF ที่ประทับตราแล้วไปกับอีเมลแจ้งเตือน Register
                            send_next_step_email(
                                doc["register_email"],
                                doc["doc_id"],
                                doc["title"],
                                "Register",
                                "ขึ้นทะเบียนเอกสาร",
                                file_path=doc["file_path"],
                            )
                            st.success("อนุมัติและประทับตรา Stamp สีแดงเรียบร้อยแล้ว!")
                            st.rerun()

                with col_b2:
                    reject_reason = st.text_input(
                        "ระบุเหตุผลที่ตีกลับ", key=f"rej_reason_app_{doc['doc_id']}"
                    )
                    if st.button(
                        "❌ ตีกลับให้แก้ไข",
                        key=f"btn_rej_app_{doc['doc_id']}",
                        type="secondary",
                    ):
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute(
                            """UPDATE documents 
                               SET status = 'REJECTED', reject_comment = ? 
                               WHERE doc_id = ?""",
                            (f"{user['name']} (Reject): {reject_reason}", doc["doc_id"]),
                        )
                        conn.commit()
                        conn.close()
                        st.warning("ตีกลับเอกสารไปยังผู้จัดทำเรียบร้อยแล้ว")
                        st.rerun()

    # ---------------------------------------------------------
    # REGISTER ROLE
    # ---------------------------------------------------------
    elif user["role"] == "Register":
        st.subheader("4. ขึ้นทะเบียนและออกเลขเอกสาร (Register)")
        pending_list = get_documents_by_status(["PENDING_REGISTER"])
        if not pending_list:
            st.info("ไม่มีเอกสารที่รอการขึ้นทะเบียนในขณะนี้")
        for doc in pending_list:
            with st.expander(f"📌 [{doc['doc_type']}] {doc['doc_id']} - {doc['title']}"):
                st.markdown("---")
                display_pdf_download_link(
                    doc["file_path"],
                    doc["filename"],
                    key=f"dl_register_{doc['doc_id']}",
                )
                st.markdown("---")

                reg_num = st.text_input(
                    "กำหนดเลขทะเบียนเอกสารทางการ", key=f"reg_num_{doc['doc_id']}"
                )
                if st.button(
                    "💾 บันทึกการขึ้นทะเบียน",
                    key=f"r_btn_{doc['doc_id']}",
                    type="primary",
                ):
                    if reg_num:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        cursor.execute(
                            "UPDATE documents SET status = 'COMPLETED', official_reg_number"
                            " = ?, registered_by = ? WHERE doc_id = ?",
                            (reg_num, user["name"], doc["doc_id"]),
                        )
                        conn.commit()
                        conn.close()
                        st.success("ขึ้นทะเบียนเอกสารสมบูรณ์!")
                        st.rerun()

    st.markdown("---")
    st.subheader("📊 ตารางติดตามสถานะเอกสารทั้งหมด")
    st.dataframe(get_documents_by_status(), use_container_width=True)


# รันหน้าจอหลักหรือหน้าล็อกอิน
if st.session_state.authenticated_user is None:
    login_screen()
else:
    main_app()