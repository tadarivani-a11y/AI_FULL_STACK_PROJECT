import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI Smart Traffic Management",
    page_icon="🚦",
    layout="wide"
)

st.title("🚦 AI Smart Traffic Management")

st.write(
    "AI-powered traffic prediction, congestion analysis "
    "and adaptive traffic signal management."
)

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select Page",
    [
        "Dashboard",
        "Traffic Prediction",
        "Traffic History",
        "AI Traffic Assistant",
        "PDF Knowledge"
    ]
)


def api_request(method, endpoint, **kwargs):

    try:

        response = requests.request(
            method,
            API_URL + endpoint,
            timeout=120,
            **kwargs
        )

        response.raise_for_status()

        return response.json()

    except Exception as error:

        st.error(
            f"Backend Error: {error}"
        )

        return None


if page == "Dashboard":

    st.header("📊 Traffic Dashboard")

    history = api_request(
        "GET",
        "/api/history"
    )

    if history:

        data = pd.DataFrame(history)

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Predictions",
            len(data)
        )

        col2.metric(
            "Average Traffic",
            f"{data['traffic'].mean():.1f}%"
        )

        col3.metric(
            "High Congestion",
            int(
                (data["congestion"] == "High").sum()
            )
        )

        col4.metric(
            "Average Vehicles",
            f"{data['vehicles'].mean():.0f}"
        )

        st.subheader("Traffic Trend")

        chart = data[
            ["created_at", "traffic"]
        ].set_index("created_at")

        st.line_chart(chart)

        st.subheader(
            "Recent Predictions"
        )

        st.dataframe(
            data,
            use_container_width=True
        )

    else:

        st.info(
            "No predictions yet."
        )


elif page == "Traffic Prediction":

    st.header(
        "🔮 AI Traffic Prediction"
    )

    col1, col2 = st.columns(2)

    with col1:

        vehicles = st.number_input(
            "Number of Vehicles",
            min_value=0,
            max_value=1000,
            value=50
        )

        hour = st.slider(
            "Hour",
            0,
            23,
            8
        )

    with col2:

        day = st.slider(
            "Day of Week",
            1,
            7,
            1
        )

        weather = st.selectbox(
            "Weather",
            [
                "Normal",
                "Rain / Bad Weather"
            ]
        )

    if st.button(
        "🔮 Predict Traffic",
        type="primary",
        use_container_width=True
    ):

        result = api_request(
            "POST",
            "/api/predict",
            json={
                "vehicles": vehicles,
                "hour": hour,
                "day": day,
                "weather":
                    1 if weather.startswith(
                        "Rain"
                    ) else 0
            }
        )

        if result:

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Traffic Level",
                f"{result['traffic']}%"
            )

            c2.metric(
                "Congestion",
                result["congestion"]
            )

            c3.metric(
                "Green Signal",
                f"{result['signal_time']} sec"
            )

            if result["congestion"] == "High":

                st.error(
                    "High congestion detected."
                )

            elif result["congestion"] == "Medium":

                st.warning(
                    "Moderate congestion detected."
                )

            else:

                st.success(
                    "Traffic is low."
                )


elif page == "Traffic History":

    st.header(
        "📜 Traffic History"
    )

    history = api_request(
        "GET",
        "/api/history"
    )

    if history:

        data = pd.DataFrame(history)

        st.dataframe(
            data,
            use_container_width=True
        )

        st.download_button(
            "Download CSV",
            data.to_csv(index=False),
            "traffic_history.csv",
            "text/csv"
        )

    else:

        st.info(
            "No history available."
        )


elif page == "AI Traffic Assistant":

    st.header(
        "🤖 AI Traffic Assistant"
    )

    question = st.text_input(
        "Ask your traffic question"
    )

    if st.button("Ask AI"):

        if question.strip():

            with st.spinner(
                "AI is thinking..."
            ):

                result = api_request(
                    "POST",
                    "/api/chat",
                    json={
                        "question": question
                    }
                )

            if result:

                st.subheader(
                    "AI Answer"
                )

                st.write(
                    result["answer"]
                )

        else:

            st.warning(
                "Please enter a question."
            )


elif page == "PDF Knowledge":

    st.header(
        "📄 Traffic PDF Knowledge"
    )

    uploaded_file = st.file_uploader(
        "Upload Traffic Management PDF",
        type=["pdf"]
    )

    if uploaded_file:

        if st.button(
            "Add PDF to AI Knowledge"
        ):

            result = api_request(
                "POST",
                "/api/pdf",
                files={
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        "application/pdf"
                    )
                }
            )

            if result:

                st.success(
                    f"PDF added successfully. "
                    f"Pages: {result['pages']}, "
                    f"Knowledge chunks: {result['chunks']}"
                )