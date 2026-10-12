"""
AI Customer Support Assistant
Streamlit interface with ticket history and analytics.

Run:
python -m streamlit run web_app.py
"""

from datetime import datetime
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

from app import analyze_customer_issue

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "tickets.db"

from app import analyze_customer_issue


APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "tickets.db"

URGENCY_ORDER = ["High", "Medium", "Low"]


# --------------------------------------------------
# DATABASE FUNCTIONS
# --------------------------------------------------

def get_connection():
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                customer_name TEXT NOT NULL,
                issue TEXT NOT NULL,
                customer_reply TEXT NOT NULL,
                troubleshooting_steps TEXT NOT NULL,
                urgency TEXT NOT NULL,
                category TEXT NOT NULL,
                sentiment TEXT NOT NULL,
                urgency_reason TEXT NOT NULL,
                reviewed INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        connection.commit()


def save_ticket(customer_name, issue, result):
    steps = result.get("troubleshooting_steps", [])

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO tickets (
                created_at,
                customer_name,
                issue,
                customer_reply,
                troubleshooting_steps,
                urgency,
                category,
                sentiment,
                urgency_reason,
                reviewed
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (
                datetime.now().astimezone().isoformat(
                    timespec="seconds"
                ),
                customer_name.strip() or "Unknown",
                issue.strip(),
                result.get("customer_reply", ""),
                "\n".join(
                    f"{i + 1}. {step}"
                    for i, step in enumerate(steps)
                ),
                result.get("urgency", "Medium"),
                result.get("category", "Other"),
                result.get("sentiment", "Neutral"),
                result.get("urgency_reason", ""),
            ),
        )

        connection.commit()
        return cursor.lastrowid


def load_tickets():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM tickets ORDER BY id DESC"
        ).fetchall()

    return pd.DataFrame([dict(row) for row in rows])


def mark_reviewed(ticket_id, reviewed=True):
    with get_connection() as connection:
        connection.execute(
            "UPDATE tickets SET reviewed = ? WHERE id = ?",
            (1 if reviewed else 0, int(ticket_id)),
        )
        connection.commit()


def clear_all_tickets():
    with get_connection() as connection:
        connection.execute("DELETE FROM tickets")
        connection.commit()


def urgency_icon(urgency):
    return {
        "High": "🔴",
        "Medium": "🟠",
        "Low": "🟢",
    }.get(urgency, "⚪")


# --------------------------------------------------
# PAGE SETUP
# --------------------------------------------------

st.set_page_config(
    page_title="AI Customer Support Assistant",
    page_icon="🎧",
    layout="wide",
)

initialize_database()

st.title("🎧 AI Customer Support Assistant")

st.caption(
    "Local AI • Ollama • Llama 3.2 1B • Python • Streamlit • SQLite"
)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.header("About this project")

    st.write("AI model: llama3.2:1b")
    st.write("Runs locally using Ollama.")
    st.write("No OpenAI API key is required.")

    st.divider()

    st.subheader("Responsible use")

    st.warning(
        "AI suggestions can be wrong. Review every response "
        "before using it. Do not enter real customer secrets "
        "or confidential information."
    )

    st.caption(f"Local database: {DB_PATH.name}")

    if st.button("Clear all ticket history"):
        st.session_state["confirm_clear"] = True

    if st.session_state.get("confirm_clear"):
        st.error(
            "This permanently deletes every saved ticket "
            "from this local database."
        )

        left, right = st.columns(2)

        if left.button("Yes, delete all", type="primary"):
            clear_all_tickets()
            st.session_state.pop("confirm_clear", None)
            st.success("Ticket history cleared.")
            st.rerun()

        if right.button("Cancel"):
            st.session_state.pop("confirm_clear", None)
            st.rerun()


# --------------------------------------------------
# TABS
# --------------------------------------------------

tab_new, tab_dashboard, tab_history = st.tabs(
    [
        "📝 Analyze issue",
        "📊 Dashboard",
        "🎫 Ticket history",
    ]
)


# --------------------------------------------------
# TAB 1: ANALYZE A CUSTOMER ISSUE
# --------------------------------------------------

with tab_new:
    st.subheader("Analyze a customer issue")

    st.write(
        "Enter a fictional or anonymized issue. The local AI "
        "will draft a customer reply and classify the ticket."
    )

    with st.form("ticket_form"):
        customer_name = st.text_input(
            "Customer name (optional)",
            placeholder="e.g. Test Customer",
        )

        issue = st.text_area(
            "Describe the customer's problem",
            placeholder=(
                "Example: The production application is unavailable "
                "for several users. The issue began at 10:30 AM."
            ),
            height=150,
        )

        submitted = st.form_submit_button(
            "Analyze issue",
            type="primary",
        )

    if submitted:
        if not issue.strip():
            st.error(
                "Please describe the customer's problem first."
            )
        else:
            with st.spinner(
                "Asking the local AI model to analyze the issue..."
            ):
                try:
                    result = analyze_customer_issue(
                        issue
                        
                    )

                    ticket_id = save_ticket(
                        customer_name,
                        issue,
                        result,
                    )

                    st.session_state["latest_result"] = result
                    st.session_state["latest_ticket_id"] = ticket_id

                    st.success(
                        f"Analysis complete. Saved as ticket #{ticket_id}."
                    )

                except Exception as error:
                    st.error(str(error))

    result = st.session_state.get("latest_result")

    if result:
        ticket_id = st.session_state.get(
            "latest_ticket_id",
            "—",
        )

        st.divider()
        st.subheader(f"Latest analysis — Ticket #{ticket_id}")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Urgency",
            f"{urgency_icon(result.get('urgency'))} "
            f"{result.get('urgency', 'Medium')}",
        )

        col2.metric(
            "Category",
            result.get("category", "Other"),
        )

        col3.metric(
            "Customer sentiment",
            result.get("sentiment", "Neutral"),
        )

        if result.get("needs_human_review", True):
            st.info(
                "Human review is required before sending "
                "advice to a customer."
            )

        if result.get("parse_warning"):
            st.warning(result["parse_warning"])

        st.markdown("### Reply to customer")

        st.text_area(
            "Draft customer reply — edit before sending",
            value=result.get("customer_reply", ""),
            height=220,
            key=f"reply_{ticket_id}",
        )

        st.markdown("### Troubleshooting steps")

        for number, step in enumerate(
            result.get("troubleshooting_steps", []),
            start=1,
        ):
            st.write(f"{number}. {step}")

        st.markdown("### Why this urgency?")

        st.write(
            result.get(
                "urgency_reason",
                "Please validate this assessment.",
            )
        )

        st.caption(
            "This is an AI-generated suggestion, not a confirmed diagnosis. "
            "Follow your organization's incident and change-management "
            "procedures."
        )


# --------------------------------------------------
# TAB 2: DASHBOARD
# --------------------------------------------------

with tab_dashboard:
    st.subheader("Ticket analytics")

    tickets = load_tickets()

    if tickets.empty:
        st.info(
            "No tickets saved yet. Analyze an issue to populate "
            "the dashboard."
        )

    else:
        total = len(tickets)

        high = int(
            (tickets["urgency"] == "High").sum()
        )

        unreviewed = int(
            (tickets["reviewed"] == 0).sum()
        )

        negative = int(
            (tickets["sentiment"] == "Negative").sum()
        )

        metric1, metric2, metric3, metric4 = st.columns(4)

        metric1.metric("Total tickets", total)
        metric2.metric("High urgency", high)
        metric3.metric("Awaiting review", unreviewed)
        metric4.metric("Negative sentiment", negative)

        left, right = st.columns(2)

        with left:
            st.markdown("#### Tickets by urgency")

            urgency_counts = (
                tickets["urgency"]
                .value_counts()
                .reindex(URGENCY_ORDER, fill_value=0)
            )

            st.bar_chart(urgency_counts)

        with right:
            st.markdown("#### Tickets by category")

            st.bar_chart(
                tickets["category"].value_counts()
            )

        st.markdown("#### Recent tickets")

        display = tickets[
            [
                "id",
                "created_at",
                "customer_name",
                "urgency",
                "category",
                "sentiment",
                "reviewed",
            ]
        ].copy()

        display["reviewed"] = display["reviewed"].map(
            {0: "No", 1: "Yes"}
        )

        st.dataframe(
            display.head(20),
            use_container_width=True,
            hide_index=True,
        )

        csv_data = tickets.to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            "Download all tickets as CSV",
            data=csv_data,
            file_name="customer_support_tickets.csv",
            mime="text/csv",
        )


# --------------------------------------------------
# TAB 3: TICKET HISTORY
# --------------------------------------------------

with tab_history:
    st.subheader("Saved ticket history")

    tickets = load_tickets()

    if tickets.empty:
        st.info(
            "Your saved tickets will appear here after analysis."
        )

    else:
        filter1, filter2, filter3 = st.columns(3)

        urgency_options = ["All"] + URGENCY_ORDER

        category_options = (
            ["All"]
            + sorted(
                tickets["category"]
                .dropna()
                .unique()
                .tolist()
            )
        )

        review_options = [
            "All",
            "Needs review",
            "Reviewed",
        ]

        urgency_filter = filter1.selectbox(
            "Urgency",
            urgency_options,
        )

        category_filter = filter2.selectbox(
            "Category",
            category_options,
        )

        review_filter = filter3.selectbox(
            "Review status",
            review_options,
        )

        filtered = tickets.copy()

        if urgency_filter != "All":
            filtered = filtered[
                filtered["urgency"] == urgency_filter
            ]

        if category_filter != "All":
            filtered = filtered[
                filtered["category"] == category_filter
            ]

        if review_filter == "Needs review":
            filtered = filtered[
                filtered["reviewed"] == 0
            ]

        elif review_filter == "Reviewed":
            filtered = filtered[
                filtered["reviewed"] == 1
            ]

        st.dataframe(
            filtered[
                [
                    "id",
                    "created_at",
                    "customer_name",
                    "issue",
                    "urgency",
                    "category",
                    "sentiment",
                    "reviewed",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

        selected_ids = filtered["id"].astype(int).tolist()

        if selected_ids:
            selected_id = st.selectbox(
                "Open ticket",
                selected_ids,
                format_func=lambda value: f"Ticket #{value}",
            )

            selected = tickets[
                tickets["id"] == selected_id
            ].iloc[0]

            st.markdown(f"#### Ticket #{selected_id}")

            st.write(
                f"*Customer:* {selected['customer_name']}"
            )

            st.write(
                f"*Issue:* {selected['issue']}"
            )

            st.write(
                f"*Urgency:* {selected['urgency']} | "
                f"*Category:* {selected['category']} | "
                f"*Sentiment:* {selected['sentiment']}"
            )

            st.markdown("*Customer reply*")

            st.text_area(
                "Saved reply",
                value=selected["customer_reply"],
                height=180,
                key=f"saved_reply_{selected_id}",
            )

            st.markdown("*Troubleshooting steps*")
            st.text(selected["troubleshooting_steps"])

            st.write(
                f"*Urgency reason:* {selected['urgency_reason']}"
            )

            new_reviewed = st.checkbox(
                "I have reviewed this ticket",
                value=bool(selected["reviewed"]),
                key=f"reviewed_{selected_id}",
            )

            if st.button(
                "Save review status",
                key=f"save_review_{selected_id}",
            ):
                mark_reviewed(
                    selected_id,
                    new_reviewed,
                )

                st.success("Review status updated.")
                st.rerun()

        st.download_button(
            "Export filtered tickets as CSV",
            data=filtered.to_csv(
                index=False
            ).encode("utf-8-sig"),
            file_name="filtered_customer_support_tickets.csv",
            mime="text/csv",
        )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Learning project only. Validate AI output, protect customer data, "
    "and follow your organization's security, privacy, and "
    "change-management requirements."
)