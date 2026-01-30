import streamlit as st
from supabase import create_client

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="False Parking Earnings",
    layout="centered"
)

# ---------------- SUPABASE ----------------
supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

# ---------------- SESSION STATES ----------------
if "confirm_add" not in st.session_state:
    st.session_state.confirm_add = False

if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = None

# ---------------- HEADER ----------------
st.title("💶 Earnings Tracker")

st.divider()

# ---------------- SUMMARY ----------------
data = supabase.table("earnings").select("amount").execute()
rows = data.data if data.data else []

total_entries = len(rows)
total_amount = sum(row["amount"] for row in rows)

col1, col2 = st.columns(2)
col1.metric("Total Tasks", total_entries)
col2.metric("Total Earned", f"€{total_amount}")

st.divider()

# ---------------- ADD ENTRY ----------------
st.subheader("➕ Add New Task")

amount = st.radio(
    "Earnings",
    [10, 5],
    format_func=lambda x: f"€{x}",
    horizontal=True
)

remarks = st.text_input("Remarks (optional)")

if st.button("Save Entry", use_container_width=True):
    st.session_state.confirm_add = True

if st.session_state.confirm_add:
    st.warning(f"Are you sure you want to add €{amount}?")

    col_yes, col_no = st.columns(2)

    if col_yes.button("✅ Yes"):
        supabase.table("earnings").insert({
            "amount": amount,
            "remarks": remarks
        }).execute()

        st.session_state.confirm_add = False
        st.success("Entry saved permanently ✅")
        st.rerun()

    if col_no.button("❌ Cancel"):
        st.session_state.confirm_add = False
        st.info("Cancelled")

st.divider()

# ---------------- HISTORY ----------------
st.subheader("📋 Earnings History")

history = supabase.table("earnings") \
    .select("*") \
    .order("created_at", desc=True) \
    .execute()

records = history.data

if records:
    for row in records:
        st.markdown(f"**💰 €{row['amount']}**")
        st.caption(row["remarks"] if row["remarks"] else "No remarks")
        st.caption(row["created_at"])

        if st.session_state.confirm_delete == row["id"]:
            col1, col2 = st.columns(2)

            if col1.button("✅ Yes, delete", key=f"yes_{row['id']}"):
                supabase.table("earnings") \
                    .delete() \
                    .eq("id", row["id"]) \
                    .execute()

                st.session_state.confirm_delete = None
                st.warning("Entry deleted")
                st.rerun()

            if col2.button("❌ No", key=f"no_{row['id']}"):
                st.session_state.confirm_delete = None
                st.info("Deletion cancelled")
                st.rerun()
        else:
            if st.button("🗑 Delete", key=f"del_{row['id']}"):
                st.session_state.confirm_delete = row["id"]
                st.rerun()

        st.divider()
else:
    st.info("No earnings recorded yet.")

