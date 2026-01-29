import streamlit as st
import sqlite3
from datetime import datetime

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="Earnings Tracker",
    layout="centered"
)

# ---------------- Database ----------------
conn = sqlite3.connect("earnings.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount INTEGER,
    remarks TEXT,
    created_at TEXT
)
""")
conn.commit()

# ---------------- Header ----------------
st.title("💶 Earnings Tracker")
st.caption("Personal • Offline • Mobile friendly")

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

choice = st.radio(
    "Amount earned",
    [10, 5],
    format_func=lambda x: f"€{x}",
    horizontal=True
)

remarks = st.text_input("Remarks (optional)")

if st.button("Save Entry", use_container_width=True):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO entries (amount, remarks, created_at) VALUES (?, ?, ?)",
        (choice, remarks, now)
    )
    conn.commit()
    st.success("Entry saved ✅")
    st.rerun()

st.divider()

# ---------------- History + Delete ----------------
st.subheader("📋 History")

rows = cursor.execute(
    "SELECT id, amount, remarks, created_at FROM entries ORDER BY created_at DESC"
).fetchall()

if rows:
    for entry_id, amount, remarks, ts in rows:
        st.write(f"💰 **€{amount}**")
        st.caption(remarks if remarks else "No remarks")
        st.caption(ts)

        if st.button("❌ Delete", key=f"del_{entry_id}"):
            cursor.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
            conn.commit()
            st.warning("Entry deleted")
            st.rerun()

        st.divider()
else:
    st.info("No entries yet.")
