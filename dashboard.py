import streamlit as st
import pandas as pd
import os
from PIL import Image

# =========================
# CONFIGURATION
# =========================
CSV_FILE = "face_time_report.csv"
KNOWN_FACES_DIR = "known_faces"
CLASS_DURATION_MINUTES = 300   # 5 hours

# =========================
# PAGE SETUP
# =========================
st.set_page_config(
    page_title="Class Attendance Dashboard",
    layout="wide"
)

st.title("📚 Class Attendance Dashboard")

# =========================
# LOAD ALL STUDENTS FROM known_faces
# =========================
all_students = []

if os.path.isdir(KNOWN_FACES_DIR):
    for name in os.listdir(KNOWN_FACES_DIR):
        if os.path.isdir(os.path.join(KNOWN_FACES_DIR, name)):
            all_students.append(name)

if not all_students:
    st.error("No students found in known_faces folder.")
    st.stop()

# =========================
# LOAD CSV (TRACKED DATA)
# =========================
if os.path.exists(CSV_FILE):
    df_csv = pd.read_csv(CSV_FILE)
else:
    df_csv = pd.DataFrame(columns=["Name", "Total Time (Seconds)", "Total Time (Minutes)"])

# =========================
# MERGE ALL STUDENTS WITH CSV
# =========================
df_all = pd.DataFrame({"Name": all_students})

df = df_all.merge(df_csv, on="Name", how="left")

df["Total Time (Seconds)"] = df["Total Time (Seconds)"].fillna(0)
df["Total Time (Minutes)"] = df["Total Time (Minutes)"].fillna(0)

# =========================
# CALCULATIONS
# =========================
df["Status"] = df["Total Time (Minutes)"].apply(
    lambda x: "Present ✅" if x > 0 else "Absent ❌"
)

df["Missing (Minutes)"] = (
    CLASS_DURATION_MINUTES - df["Total Time (Minutes)"]
).clip(lower=0).round(1)

# =========================
# SUMMARY
# =========================
st.subheader("📊 Class Summary")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Class Duration", "5 hours")
c2.metric("Total Students", len(df))
c3.metric("Present", (df["Status"] == "Present ✅").sum())
c4.metric("Absent", (df["Status"] == "Absent ❌").sum())

st.divider()

# =========================
# ATTENDANCE TABLE
# =========================
st.subheader("👤 Attendance Table")

headers = st.columns([1.2, 2, 2, 2, 2])
headers[0].markdown("**Photo**")
headers[1].markdown("**Student**")
headers[2].markdown("**Time (min)**")
headers[3].markdown("**Status**")
headers[4].markdown("**Missing (min)**")

for _, row in df.iterrows():
    cols = st.columns([1.2, 2, 2, 2, 2])

    name = row["Name"]

    # -------------------------
    # LOAD IMAGE
    # -------------------------
    img_path = None
    person_dir = os.path.join(KNOWN_FACES_DIR, name)

    if os.path.isdir(person_dir):
        for f in os.listdir(person_dir):
            if f.lower().endswith((".jpg", ".jpeg", ".png")):
                img_path = os.path.join(person_dir, f)
                break

    if img_path and os.path.exists(img_path):
        cols[0].image(Image.open(img_path), width=70)
    else:
        cols[0].write("—")

    cols[1].write(name)
    cols[2].write(round(row["Total Time (Minutes)"], 1))
    cols[3].write(row["Status"])
    cols[4].write(row["Missing (Minutes)"])

st.divider()

# =========================
# CHART
# =========================
st.subheader("📈 Time Spent in Class (Minutes)")
st.bar_chart(df.set_index("Name")["Total Time (Minutes)"])

# =========================
# DOWNLOAD
# =========================
st.subheader("⬇ Export Attendance Data")

st.download_button(
    label="Download CSV",
    data=df.to_csv(index=False),
    file_name="class_attendance_report.csv",
    mime="text/csv"
)
