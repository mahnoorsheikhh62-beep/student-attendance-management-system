
import streamlit as st
import sqlite3
from datetime import date

# --------------------------------
# PAGE SETTINGS
# --------------------------------

st.set_page_config(
    page_title="Student Attendance System",
    page_icon="🎓",
    layout="wide"
)

# --------------------------------
# CUSTOM CSS - DARK BLUE THEME
# --------------------------------

st.markdown("""
<style>

.stApp {
    background-color: #e8edf5;
}

[data-testid="stSidebar"] {
    background-color: #0b1f3a;
}

[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: white !important;
}

h1, h2, h3 {
    color: #0b1f3a !important;
}

.stApp p,
.stApp label {
    color: #172554;
}

.stButton button {
    background-color: #123d70;
    color: white;
    border-radius: 8px;
    border: none;
    padding: 8px 20px;
}

.stButton button:hover {
    background-color: #1e528e;
    color: white;
}

.stTextInput input {
    border-radius: 8px;
}

.stSelectbox div[data-baseweb="select"] {
    border-radius: 8px;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------
# DATABASE CONNECTION
# --------------------------------

conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    roll_no TEXT UNIQUE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    attendance_date TEXT,
    status TEXT,
    UNIQUE(student_id, attendance_date),
    FOREIGN KEY(student_id) REFERENCES students(id)
)
""")

conn.commit()


# --------------------------------
# ADMIN LOGIN SYSTEM
# --------------------------------

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


if not st.session_state.logged_in:

    st.title("🎓 Student Attendance System")
    st.subheader("Admin Sign In")

    with st.form("login_form"):

        username = st.text_input("Username")
        password = st.text_input(
            "Password",
            type="password"
        )

        login_button = st.form_submit_button("Sign In")

        if login_button:

            if (
                username == ADMIN_USERNAME
                and password == ADMIN_PASSWORD
            ):

                st.session_state.logged_in = True
                st.rerun()

            else:
                st.error("Incorrect username or password!")

    conn.close()
    st.stop()


# --------------------------------
# APPLICATION TITLE
# --------------------------------

st.title("🎓 Student Attendance Management System")
st.write("Manage students and daily attendance easily.")


# --------------------------------
# SIDEBAR NAVIGATION
# --------------------------------

st.sidebar.title("🎓 Navigation")

menu = st.sidebar.radio(
    "Select a section",
    [
        "Dashboard",
        "Add Student",
        "Manage Students",
        "Mark Attendance",
        "Attendance History",
        "Attendance Percentage"
    ]
)

st.sidebar.divider()

if st.sidebar.button("Sign Out"):

    st.session_state.logged_in = False
    st.rerun()


# --------------------------------
# GET ALL STUDENTS
# --------------------------------

cursor.execute("SELECT * FROM students ORDER BY id")
students = cursor.fetchall()


# --------------------------------
# SECTION 1: DASHBOARD
# --------------------------------

if menu == "Dashboard":

    st.header("Dashboard")

    total_students = len(students)
    today = str(date.today())

    cursor.execute("""
        SELECT COUNT(*) FROM attendance
        WHERE attendance_date = ?
        AND status = 'Present'
    """, (today,))

    present_today = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*) FROM attendance
        WHERE attendance_date = ?
        AND status = 'Absent'
    """, (today,))

    absent_today = cursor.fetchone()[0]

    if total_students > 0:
        attendance_percentage = (
            present_today / total_students
        ) * 100
    else:
        attendance_percentage = 0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Students", total_students)
    col2.metric("Present Today", present_today)
    col3.metric("Absent Today", absent_today)
    col4.metric(
        "Attendance %",
        f"{attendance_percentage:.1f}%"
    )

    st.header("Student Records")

    if students:

        st.dataframe(
            [
                {
                    "ID": s[0],
                    "Student Name": s[1],
                    "Roll Number": s[2]
                }
                for s in students
            ],
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No students added yet.")


# --------------------------------
# SECTION 2: ADD STUDENT
# --------------------------------

elif menu == "Add Student":

    st.header("Add New Student")

    name = st.text_input("Enter Student Name")
    roll_no = st.text_input("Enter Roll Number")

    if st.button("Add Student"):

        if name.strip() and roll_no.strip():

            try:

                cursor.execute("""
                    INSERT INTO students (name, roll_no)
                    VALUES (?, ?)
                """, (
                    name.strip(),
                    roll_no.strip()
                ))

                conn.commit()

                st.success("Student added successfully!")
                st.rerun()

            except sqlite3.IntegrityError:

                st.error("This roll number already exists!")

        else:

            st.warning("Please enter both name and roll number.")


# --------------------------------
# SECTION 3: MANAGE STUDENTS
# --------------------------------

elif menu == "Manage Students":

    st.header("Manage Students")

    if students:

        search = st.text_input(
            "Search by name or roll number"
        )

        filtered_students = [
            student for student in students
            if search.lower() in student[1].lower()
            or search.lower() in student[2].lower()
        ]

        st.subheader("Search Results")

        if filtered_students:

            st.dataframe(
                [
                    {
                        "ID": s[0],
                        "Student Name": s[1],
                        "Roll Number": s[2]
                    }
                    for s in filtered_students
                ],
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info("No matching student found.")

        selected_student = st.selectbox(
            "Select a student to manage",
            students,
            format_func=lambda s: f"{s[1]} - {s[2]}"
        )

        st.subheader("Edit Student Details")

        new_name = st.text_input(
            "Update Student Name",
            value=selected_student[1],
            key=f"edit_name_{selected_student[0]}"
        )

        new_roll = st.text_input(
            "Update Roll Number",
            value=selected_student[2],
            key=f"edit_roll_{selected_student[0]}"
        )

        if st.button("Update Student"):

            if new_name.strip() and new_roll.strip():

                try:

                    cursor.execute("""
                        UPDATE students
                        SET name = ?, roll_no = ?
                        WHERE id = ?
                    """, (
                        new_name.strip(),
                        new_roll.strip(),
                        selected_student[0]
                    ))

                    conn.commit()

                    st.success("Student updated successfully!")
                    st.rerun()

                except sqlite3.IntegrityError:

                    st.error("This roll number is already in use.")

            else:

                st.warning("Please enter both fields.")

        st.subheader("Delete Student")

        confirm_delete = st.checkbox(
            "I confirm that I want to delete this student."
        )

        if st.button("Delete Student"):

            if confirm_delete:

                cursor.execute("""
                    DELETE FROM attendance
                    WHERE student_id = ?
                """, (selected_student[0],))

                cursor.execute("""
                    DELETE FROM students
                    WHERE id = ?
                """, (selected_student[0],))

                conn.commit()

                st.success("Student and attendance records deleted.")
                st.rerun()

            else:

                st.warning("Please confirm before deleting.")

    else:

        st.info("Add a student first.")


# --------------------------------
# SECTION 4: MARK ATTENDANCE
# --------------------------------

elif menu == "Mark Attendance":

    st.header("Daily Class Attendance")

    if students:

        attendance_date = st.date_input(
            "Select Attendance Date",
            value=date.today()
        )

        with st.form("attendance_form"):

            st.subheader("Mark Students Present or Absent")

            attendance_data = {}

            for student in students:

                student_id = student[0]
                student_name = student[1]
                roll_number = student[2]

                status = st.selectbox(
                    f"{student_name} (Roll No: {roll_number})",
                    ["Present", "Absent"],
                    key=f"attendance_{student_id}"
                )

                attendance_data[student_id] = status

            submit = st.form_submit_button("Save Attendance")

            if submit:

                for student_id, status in attendance_data.items():

                    cursor.execute("""
                        SELECT id FROM attendance
                        WHERE student_id = ?
                        AND attendance_date = ?
                    """, (
                        student_id,
                        str(attendance_date)
                    ))

                    existing_record = cursor.fetchone()

                    if existing_record:

                        cursor.execute("""
                            UPDATE attendance
                            SET status = ?
                            WHERE student_id = ?
                            AND attendance_date = ?
                        """, (
                            status,
                            student_id,
                            str(attendance_date)
                        ))

                    else:

                        cursor.execute("""
                            INSERT INTO attendance
                            (student_id, attendance_date, status)
                            VALUES (?, ?, ?)
                        """, (
                            student_id,
                            str(attendance_date),
                            status
                        ))

                conn.commit()

                st.success("Class attendance saved successfully!")

    else:

        st.warning("Please add students before marking attendance.")


# --------------------------------
# SECTION 5: ATTENDANCE HISTORY
# --------------------------------

elif menu == "Attendance History":

    st.header("Attendance History")

    cursor.execute("""
        SELECT students.name,
               students.roll_no,
               attendance.attendance_date,
               attendance.status
        FROM attendance
        JOIN students
        ON students.id = attendance.student_id
        ORDER BY attendance.attendance_date DESC
    """)

    history = cursor.fetchall()

    if history:

        st.dataframe(
            [
                {
                    "Student Name": record[0],
                    "Roll Number": record[1],
                    "Date": record[2],
                    "Status": record[3]
                }
                for record in history
            ],
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No attendance history available yet.")


# --------------------------------
# SECTION 6: ATTENDANCE PERCENTAGE
# --------------------------------

elif menu == "Attendance Percentage":

    st.header("Student Attendance Percentage")

    cursor.execute("""
        SELECT students.name,
               students.roll_no,
               COUNT(attendance.id),
               SUM(
                   CASE
                       WHEN attendance.status = 'Present'
                       THEN 1
                       ELSE 0
                   END
               )
        FROM students
        LEFT JOIN attendance
        ON students.id = attendance.student_id
        GROUP BY students.id
    """)

    results = cursor.fetchall()

    if results:

        attendance_records = []

        for student in results:

            name = student[0]
            roll_no = student[1]
            total_classes = student[2]
            present_classes = student[3] or 0

            if total_classes > 0:

                percentage = (
                    present_classes / total_classes
                ) * 100

            else:

                percentage = 0

            attendance_records.append({
                "Student Name": name,
                "Roll Number": roll_no,
                "Total Classes": total_classes,
                "Present Classes": present_classes,
                "Attendance %": f"{percentage:.1f}%"
            })

        st.dataframe(
            attendance_records,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("Add students to view attendance percentages.")


# --------------------------------
# CLOSE DATABASE
# --------------------------------

conn.close()
