import streamlit as st
from supabase import create_client

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Parking Entry",
    layout="centered"
)

# ---------------- SUPABASE ----------------
supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

# ---------------- SESSION STATE ----------------
if "confirm_add" not in st.session_state:
    st.session_state.confirm_add = False

if "vehicle_temp" not in st.session_state:
    st.session_state.vehicle_temp = ""

# ---------------- UI ----------------
st.title("🚗 Parking Entry System")

vehicle = st.text_input(
    "Vehicle Number",
    placeholder="e.g. BA-2-PA-1234"
)

# ---------------- ADD BUTTON ----------------
if st.button("➕ Add Entry", use_container_width=True):
    if vehicle.strip() == "":
        st.warning("Please enter a vehicle number")
    else:
        st.session_state.confirm_add = True
        st.session_state.vehicle_temp = vehicle

# ---------------- CONFIRMATION ----------------
if st.session_state.confirm_add:
    st.warning(f"Are you sure you want to add **{st.session_state.vehicle_temp}**?")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Yes", use_container_width=True):
            supabase.table("parking_entries").insert({
                "vehicle_number": st.session_state.vehicle_temp
            }).execute()

            st.success("Entry saved successfully")
            st.session_state.confirm_add = False
            st.session_state.vehicle_temp = ""
            st.rerun()

    with col2:
        if st.button("❌ No", use_container_width=True):
            st.session_state.confirm_add = False
            st.session_state.vehicle_temp = ""
            st.info("Entry cancelled")

# ---------------- DATA ----------------
st.divider()
st.subheader("📋 Current Entries")

response = supabase.table("parking_entries") \
    .select("*") \
    .order("created_at", desc=True) \
    .execute()

rows = response.data

if rows:
    st.markdown(f"### 🔢 Total Vehicles: **{len(rows)}**")

    for row in rows:
        with st.container():
            col1, col2 = st.columns([4, 1])

            col1.markdown(
                f"**{row['vehicle_number']}**  \n"
                f"🕒 {row['created_at']}"
            )

            if col2.button("🗑", key=row["id"]):
                supabase.table("parking_entries") \
                    .delete() \
                    .eq("id", row["id"]) \
                    .execute()
                st.rerun()
else:
    st.info("No entries yet")

