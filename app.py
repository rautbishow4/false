import streamlit as st
import sqlite3
from datetime import datetime
import os

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="Earnings Tracker",
    layout="centered"
)

# ---------------- Google Drive Persistent DB ----------------
DB_PATH = r"G:\My Drive\false\data\earnings.db"

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount INTEGER NOT NULL,
    remarks TEXT,
    created_at TEXT NOT NULL
)
""")
conn.commit()

# ---------------- Header ----------------
st.title("💶 Earnings Tracker")
st.caption("Personal • Mobile friendly • Auto-synced to Google Drive")

st.divider()

# ---------------- Summary ----------------
total_entries = cursor.execute(
    "SELECT COUNT(*) FROM entries"
).fetchone()[0]

total_amount = cursor.execute(
    "SELECT COALESCE(SUM(amount), 0) FROM entries"
).fetchone()[0]

col1, col2 = st.columns(2)
col1.metric("Total Entries", total_entries)
col2.metric("Total € Earned", f"€{total_amount}")

st.divider()

# ---------------- Add Entry ----------------
st.subheader("➕ Add Entry")

amount = st.radio(
    "Amount earned",
    [10, 5],
    format_func=lambda x: f"€{x}",
    horizontal=True
)

remarks = st.text_input("Remarks (optional)")

if st.button("Save Entry", use_container_width=True):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO entries (amount, remarks, created_at) VALUES (?, ?, ?)",
        (amount, remarks, timestamp)
    )
    conn.commit()
    st.success("Entry saved & synced ✅")
    st.rerun()

st.divider()

# ---------------- Delete Confirmation State ----------------
if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = None

# ---------------- History ----------------
st.subheader("📋 History")

rows = cursor.execute(
    "SELECT id, amount, remarks, created_at FROM entries ORDER BY created_at DESC"
).fetchall()

if rows:
    for entry_id, amount, remarks, ts in rows:
        st.write(f"💰 **€{amount}**")
        st.caption(remarks if remarks else "No remarks")
        st.caption(ts)

        if st.session_state.confirm_delete == entry_id:
            col_yes, col_no = st.columns(2)

            if col_yes.button("✅ Yes, delete", key=f"yes_{entry_id}"):
                cursor.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
                conn.commit()
                st.session_state.confirm_delete = None
                st.warning("Entry deleted")
                st.rerun()

            if col_no.button("❌ No, keep", key=f"no_{entry_id}"):
                st.session_state.confirm_delete = None
                st.info("Deletion cancelled")
                st.rerun()
        else:
            if st.button("❌ Delete", key=f"del_{entry_id}"):
                st.session_state.confirm_delete = entry_id
                st.rerun()

        st.divider()
else:
    st.info("No entries yet.")


