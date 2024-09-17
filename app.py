import datetime
import random
import altair as alt
import numpy as np
import pandas as pd
import streamlit as st


st.set_page_config(page_title="Support tickets", page_icon="🎫")
st.title("🎫 AUTOSherpa Support Ticket System")
st.write(
    """
    This app is dedicated to allowing clients to raise tickets through the AUTOSherpa Support Ticket System. The user can create a ticket, edit 
    existing tickets, and view some statistics.
    """
)


issue_types = ["Bug", "Request", "Requirement"]
issue_descriptions = [
    "Issue with login", "Feature request for new functionality", "Requirement for performance improvement",
    "Bug in the user interface", "Request for additional documentation", "Requirement for security enhancement",
    "Bug in data processing", "Request for a new report", "Requirement for system integration",
]

if "df" not in st.session_state:
    np.random.seed(42)

    data = {
        "ID": [f"TICKET-{i}" for i in range(1100, 1000, -1)],
        "Issue Type": np.random.choice(issue_types, size=100),
        "Issue": np.random.choice(issue_descriptions, size=100),
        "Status": np.random.choice(["Open", "In Progress", "Closed"], size=100),
        "Priority": np.random.choice(["High", "Medium", "Low"], size=100),
        "Date Submitted": [
            datetime.date(2023, 6, 1) + datetime.timedelta(days=random.randint(0, 182))
            for _ in range(100)
        ],
    }
    df = pd.DataFrame(data)
    st.session_state.df = df

st.header("Add a ticket")

with st.form("add_ticket_form"):
    issue_type = st.selectbox("Issue Type", issue_types)
    issue = st.text_area("Describe the issue")
    priority = st.selectbox("Priority", ["High", "Medium", "Low"])
    attachment = st.file_uploader("Upload an attachment (optional)", type=["pdf", "docx", "png", "jpg", "jpeg"])
    submitted = st.form_submit_button("Submit")

if submitted:
    recent_ticket_number = int(max(st.session_state.df.ID).split("-")[1])
    today = datetime.datetime.now().strftime("%m-%d-%Y")
    attachment_path = attachment.name if attachment else "No attachment"
    
    df_new = pd.DataFrame(
        [
            {
                "ID": f"TICKET-{recent_ticket_number+1}",
                "Issue Type": issue_type,
                "Issue": issue,
                "Status": "Open",
                "Priority": priority,
                "Date Submitted": today,
                "Attachment": attachment_path
            }
        ]
    )

    st.write("Ticket submitted! Here are the ticket details:")
    st.dataframe(df_new, use_container_width=True, hide_index=True)
    st.session_state.df = pd.concat([df_new, st.session_state.df], axis=0)

st.header("Existing tickets")
st.write(f"Number of tickets: `{len(st.session_state.df)}`")

st.info(
    "You can edit the tickets by double clicking on a cell. Note how the plots below "
    "update automatically! You can also sort the table by clicking on the column headers.",
    icon="✍️",
)

edited_df = st.data_editor(
    st.session_state.df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Status": st.column_config.SelectboxColumn(
            "Status",
            help="Ticket status",
            options=["Open", "In Progress", "Closed"],
            required=True,
        ),
        "Priority": st.column_config.SelectboxColumn(
            "Priority",
            help="Priority",
            options=["High", "Medium", "Low"],
            required=True,
        ),
    },
    # Disable editing the ID, Date Submitted, and Attachment columns.
    disabled=["ID", "Date Submitted", "Attachment"],
)

st.header("Statistics")

col1, col2, col3 = st.columns(3)
num_open_tickets = len(st.session_state.df[st.session_state.df.Status == "Open"])
col1.metric(label="Number of open tickets", value=num_open_tickets, delta=10)
col2.metric(label="First response time (hours)", value=5.2, delta=-1.5)
col3.metric(label="Average resolution time (hours)", value=16, delta=2)

st.write("")
st.write("##### Ticket status per month")
status_plot = (
    alt.Chart(edited_df)
    .mark_bar()
    .encode(
        x="month(Date Submitted):O",
        y="count():Q",
        xOffset="Status:N",
        color="Status:N",
    )
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(status_plot, use_container_width=True, theme="streamlit")

st.write("##### Current ticket priorities")
priority_plot = (
    alt.Chart(edited_df)
    .mark_arc()
    .encode(theta="count():Q", color="Priority:N")
    .properties(height=300)
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(priority_plot, use_container_width=True, theme="streamlit")
