import streamlit as st
from utils import analyze_sentiment, detect_topics, analyze_travel_intent, extract_travel_objects
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="MyTravelHelper", page_icon="✈️")

st.title("✈️ MyTravelHelper")
st.markdown("Your AI-powered travel assistant for analyzing reviews and planning trips.")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&family=Playfair+Display:wght@700&display=swap');

    .stMarkdown, .stText {
        font-family: 'Montserrat', sans-serif;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Playfair Display', serif;
    }

    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: translateY(-2px);
        box-shadow: 3px 3px 8px rgba(0,0,0,0.3);
    }

    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea {
        border-radius: 8px;
        border: 1px solid #ccc;
        padding: 10px;
    }

    html[data-theme="light"] .stTextInput>div>div>input,
    html[data-theme="light"] .stTextArea>div>div>textarea {
        background-color: #ffffff !important;
        color: #31333F !important;
    }

    html[data-theme="dark"] .stTextInput>div>div>input,
    html[data-theme="dark"] .stTextArea>div>div>textarea {
        background-color: #2b2b2b !important;
        color: #e0e0e0 !important;
        border-color: #555 !important;
    }

    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.2rem;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: nowrap;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        padding-left: 20px;
        padding-right: 20px;
    }

    .sentiment-positive {
        background-color: #d4edda;
        color: #155724;
        padding: 8px 12px;
        border-radius: 5px;
        font-weight: bold;
    }
    .sentiment-negative {
        background-color: #f8d7da;
        color: #721c24;
        padding: 8px 12px;
        border-radius: 5px;
        font-weight: bold;
    }
    .topic-tag {
        display: inline-block;
        background-color: #e3f2fd;
        color: #1e88e5;
        padding: 5px 10px;
        border-radius: 15px;
        margin: 4px;
        font-size: 0.9em;
    }

    @media (prefers-color-scheme: dark) {
        .topic-tag {
            background-color: #1a237e;
            color: #90caf9;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

@st.cache_data(ttl=300)
def cached_analyze_sentiment(text: str):
    return analyze_sentiment(text)

@st.cache_data(ttl=300)
def cached_detect_topics(text: str, candidate_topics: tuple):
    return detect_topics(text, list(candidate_topics))

@st.cache_data(ttl=300)
def cached_analyze_travel_intent(text: str):
    return analyze_travel_intent(text)

@st.cache_data(ttl=300)
def cached_extract_travel_objects(text: str):
    return extract_travel_objects(text)

tab1, tab2, tab3 = st.tabs(["Review Analysis", "Trip Analyzer", "Sentiment Distribution"])

with tab1:
    st.header("Analyze Your Travel Reviews")
    review_text = st.text_area("Enter your travel review here:", height=150, placeholder="e.g., The hotel service was excellent, but the food was a bit disappointing.")

    if st.button("Analyze Review", key="analyze_review_btn"):
        if review_text:
            st.subheader("Analysis Results:")

            with st.spinner("Analyzing sentiment..."):
                sentiment_results = cached_analyze_sentiment(review_text)
            if "error" not in sentiment_results:
                st.markdown("### Sentiment:")
                if sentiment_results:
                    sorted_scores = sorted(sentiment_results.items(), key=lambda x: x[1], reverse=True)
                    dominant_sentiment, top_score = sorted_scores[0]
                    second_score = sorted_scores[1][1]
                    score = top_score * 100

                    threshold = 0.15
                    is_mixed = (top_score - second_score) < threshold

                    if is_mixed:
                        all_scores = " | ".join(
                            f"{label.capitalize()}: {s*100:.1f}%"
                            for label, s in sorted_scores
                        )
                        st.markdown(
                            f"<span style='display:inline-block;background-color:#f0f0f0;color:#555;"
                            f"padding:8px 12px;border-radius:5px;font-weight:bold'>"
                            f"⚖️ Mixed Sentiment ({all_scores})</span>",
                            unsafe_allow_html=True
                        )
                    elif dominant_sentiment.lower() == "positive":
                        st.markdown(f"<span class='sentiment-positive'>😊 Positive ({score:.2f}%)</span>", unsafe_allow_html=True)
                    elif dominant_sentiment.lower() == "negative":
                        st.markdown(f"<span class='sentiment-negative'>😞 Negative ({score:.2f}%)</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span style='display:inline-block;background-color:#fff3cd;color:#856404;padding:8px 12px;border-radius:5px;font-weight:bold'>😐 Neutral ({score:.2f}%)</span>", unsafe_allow_html=True)
                else:
                    st.info("Could not determine sentiment.")
            else:
                st.error(f"Sentiment analysis error: {sentiment_results['error']}")

            st.markdown("---")

            st.markdown("### Detected Topics:")
            candidate_topics = ["cleanliness", "food & dining", "customer service", "pricing", "location"]
            with st.spinner("Detecting topics..."):
                topic_results = cached_detect_topics(review_text, tuple(candidate_topics))
            if "error" not in topic_results:
                if topic_results:
                    sorted_topics = sorted(topic_results.items(), key=lambda item: item[1], reverse=True)
                    st.write("Keywords identified in your review:")
                    topic_tags = ""
                    for topic, score in sorted_topics:
                        if score > 0.5:
                            topic_tags += f"<span class='topic-tag'>{topic.capitalize()} ({score:.2f})</span>"
                    if topic_tags:
                        st.markdown(topic_tags, unsafe_allow_html=True)
                    else:
                        st.info("No significant topics detected.")
                else:
                    st.info("No topics detected.")
            else:
                st.error(f"Topic detection error: {topic_results['error']}")
        else:
            st.warning("Please enter a review to analyze.")

with tab2:
    st.header("Plan Your Next Adventure")
    travel_query = st.text_input("Tell me about your travel goals:", placeholder="e.g., I want to visit Paris in June for a romantic getaway.")

    if st.button("Plan My Trip", key="plan_trip_btn"):
        if travel_query:
            st.subheader("Trip Planning Insights:")

            st.markdown("### Travel Intention:")
            with st.spinner("Analyzing travel intent..."):
                intent = cached_analyze_travel_intent(travel_query)
            if not intent.startswith("Error:"):
                st.success(f"Intent: **{intent.capitalize()}**")
            else:
                st.error(f"Travel intention analysis error: {intent}")

            st.markdown("---")

            st.markdown("### Extracted Travel Details:")
            with st.spinner("Extracting entities..."):
                entities = cached_extract_travel_objects(travel_query)
            if "error" not in entities:
                if entities:
                    for entity_type, entity_list in entities.items():
                        st.markdown(f"**{entity_type.replace('_', ' ').title()}:** {', '.join(set(entity_list))}")
                else:
                    st.info("No specific travel details extracted.")
            else:
                st.error(f"Entity extraction error: {entities['error']}")
        else:
            st.warning("Please enter your travel goals to plan your trip.")

with tab3:
    st.header("Overall Sentiment Dashboard")
    multi_reviews = st.text_area(
        "Enter multiple travel reviews (one per line):",
        height=200,
        placeholder=(
            "e.g.\n"
            "The flight was delayed but the crew was amazing.\n"
            "Terrible hotel, never again.\n"
            "Fantastic food and great location."
        )
    )

    if st.button("Analyze All Reviews", key="analyze_all_btn"):
        if multi_reviews:
            reviews_list = [r.strip() for r in multi_reviews.split('\n') if r.strip()]

            if reviews_list:
                sentiments = []
                for review in reviews_list:
                    with st.spinner(f"Analyzing review {len(sentiments) + 1} of {len(reviews_list)}..."):
                        sentiment_results = cached_analyze_sentiment(review)
                    if "error" not in sentiment_results and sentiment_results:
                        sorted_scores = sorted(sentiment_results.items(), key=lambda x: x[1], reverse=True)
                        top_score = sorted_scores[0][1]
                        second_score = sorted_scores[1][1]
                        if (top_score - second_score) < 0.15:
                            sentiments.append("MIXED")
                        else:
                            sentiments.append(sorted_scores[0][0].capitalize())
                    else:
                        sentiments.append("UNKNOWN")

                if sentiments:
                    sentiment_counts = pd.Series(sentiments).value_counts().reset_index()
                    sentiment_counts.columns = ['Sentiment', 'Count']

                    fig = px.pie(sentiment_counts,
                                 values='Count',
                                 names='Sentiment',
                                 title='Overall Sentiment Distribution',
                                 color='Sentiment',
                     color_discrete_map={'Positive':'#4CAF50',
                                         'Negative':'#f44336',
                                         'Neutral':'#ffc107',
                                         'MIXED':'#9c27b0',
                                         'UNKNOWN':'#cccccc'})
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No sentiments could be analyzed from the provided reviews.")
            else:
                st.warning("Please enter some reviews to analyze.")
        else:
            st.warning("Please enter reviews to analyze.")
