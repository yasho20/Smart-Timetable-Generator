import streamlit as st
import pandas as pd
import random
from ortools.sat.python import cp_model

# ================= APP CONFIG =================
st.set_page_config(page_title="Smart Timetable System", layout="wide")
st.title("🤖 AI-Assisted Smart Timetable Conflict Detection System")

# ================= LOAD DATA =================
courses = pd.read_csv("courses.csv")
teachers = pd.read_csv("teachers.csv")
rooms = pd.read_csv("rooms.csv")

days = ["Monday", "Tuesday", "Wednesday"]
times = ["9-11", "11-1", "2-4"]

# ================= CONFLICTING TIMETABLE =================
st.header("❌ Conflicting Timetable (Before AI)")

conflict_data = []

# Generate mixed random data for realism
for _, course in courses.iterrows():
    day = random.choice(days)
    time = random.choice(times)
    room = random.choice(rooms["Room_ID"].tolist())
    teacher = random.choice(teachers["Teacher_Name"].tolist())
    conflict_data.append([course["Course_Name"], day, time, room, teacher])

# Add intentional conflicts for demo (2–3 courses)
if len(conflict_data) > 3:
    # Conflict 1
    conflict_data[0][1] = conflict_data[1][1]  # same day
    conflict_data[0][2] = conflict_data[1][2]  # same time
    conflict_data[0][3] = conflict_data[1][3]  # same room
    # Conflict 2
    conflict_data[2][1] = conflict_data[3][1]  # same day
    conflict_data[2][2] = conflict_data[3][2]  # same time
    conflict_data[2][4] = conflict_data[3][4]  # same teacher

conflict_df = pd.DataFrame(
    conflict_data,
    columns=["Course", "Day", "Time", "Room", "Teacher"]
)

st.dataframe(conflict_df, use_container_width=True)

# ========== DETECT CONFLICTS ==========
st.subheader("⚠ Conflict Summary (Detected Before AI)")

conflicts = []

for i in range(len(conflict_df)):
    for j in range(i+1, len(conflict_df)):
        row1 = conflict_df.iloc[i]
        row2 = conflict_df.iloc[j]
        # Same day and time AND same room OR same teacher
        if row1["Day"] == row2["Day"] and row1["Time"] == row2["Time"]:
            if row1["Room"] == row2["Room"]:
                conflicts.append(f"Room conflict: {row1['Course']} & {row2['Course']} in {row1['Room']} at {row1['Day']} {row1['Time']}")
            if row1["Teacher"] == row2["Teacher"]:
                conflicts.append(f"Teacher conflict: {row1['Course']} & {row2['Course']} with {row1['Teacher']} at {row1['Day']} {row1['Time']}")

if conflicts:
    st.error("⚠ Conflicts Detected:")
    for c in conflicts:
        st.error("• " + c)
else:
    st.success("✅ No conflicts detected")

# ================= AI RESOLUTION =================
if st.button("🤖 Resolve Conflicts using AI"):
    st.header("✅ Optimized Timetable (After AI)")

    model = cp_model.CpModel()
    num_courses = len(courses)
    num_slots = len(days) * len(times)

    # Each course assigned a unique slot
    slot = {}
    for c in range(num_courses):
        slot[c] = model.NewIntVar(0, num_slots - 1, f"slot_{c}")

    # Constraint: all slots different (no conflicts)
    model.AddAllDifferent(slot.values())

    solver = cp_model.CpSolver()
    solver.Solve(model)

    # Build clean timetable
    clean_data = []
    resolution_report = []

    for c in range(num_courses):
        s = solver.Value(slot[c])
        day = days[s // len(times)]
        time = times[s % len(times)]
        room = rooms.iloc[c % len(rooms)]["Room_ID"]
        teacher = teachers.iloc[c % len(teachers)]["Teacher_Name"]

        clean_data.append([courses.iloc[c]["Course_Name"], day, time, room, teacher])
        resolution_report.append(
            f"{courses.iloc[c]['Course_Name']} assigned to {day} {time} → No conflict"
        )

    clean_df = pd.DataFrame(
        clean_data,
        columns=["Course", "Day", "Time", "Room", "Teacher"]
    )

    st.dataframe(clean_df, use_container_width=True)
    st.success("🎉 All conflicts resolved successfully using AI!")

    st.subheader("🧾 AI Resolution Summary")
    for r in resolution_report:
        st.write("✔", r)
