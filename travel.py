import os
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from datetime import date

# Secure API Key Storage
GOOGLE_API_KEY = "AIzaSyCHGvCV_UsrQLx8EZrb58IQ9qqQEyRNcYI"
if not GOOGLE_API_KEY:
    st.error("❌ Google API Key missing. Set 'GOOGLE_API_KEY' as an environment variable.")

# Streamlit Config
st.set_page_config(page_title="AI-Powered Travel Planner", layout="wide")

# Custom Styling
st.markdown("<h1 style='text-align: center; color: #2a4a7d;'>AI-Powered Travel Planner</h1>", unsafe_allow_html=True)

# User Inputs
with st.expander("✈️ Enter Trip Details", expanded=True):
    col1, col2, col3 = st.columns(3)
    source = col1.text_input("From:", placeholder="Enter departure city")
    destination = col2.text_input("To:", placeholder="Enter destination city")
    trip_duration = col3.slider("Trip Duration (days):", 1, 30, 3)

    col4, col5 = st.columns(2)
    date_of_travel = col4.date_input("Travel Date:", min_value=date.today())
    travel_mode = col5.selectbox("Preferred Mode:", ["Any", "Flight", "Train", "Bus", "Cab"])

    add_prefs = st.checkbox("Add Advanced Preferences")
    interests = "general"
    dietary_prefs = "none"
    if add_prefs:
        col6, col7 = st.columns(2)
        interests = col6.multiselect("Interests:", ["Historical", "Adventure", "Cultural", "Nature", "Food"])
        dietary_prefs = col7.selectbox("Dietary Preferences:", ["None", "Vegetarian", "Vegan", "Gluten-Free"])

# AI Call
@st.cache_data(ttl=3600, show_spinner=False)
def get_travel_plan(_chain, inputs):
    try:
        return _chain.invoke(inputs)
    except Exception as e:
        return "⚠️ Unable to generate itinerary at the moment. Please try again later."

if st.button("Generate Travel Plan", use_container_width=True):
    if source and destination:
        with st.spinner("🧠 Generating your perfect itinerary..."):
            chat_template = ChatPromptTemplate.from_messages([
                ("system", "You are an expert travel planner. Provide a detailed itinerary with transport, accommodation, and food suggestions."),
                ("human", f"Plan {trip_duration}-day trip from {source} to {destination} on {date_of_travel}. Mode: {travel_mode}. Interests: {interests}. Diet: {dietary_prefs}.")
            ])

            llm = ChatGoogleGenerativeAI(api_key=GOOGLE_API_KEY, model="gemini-1.5-pro-latest")
            chain = chat_template | llm | StrOutputParser()
            response = get_travel_plan(chain, {
                "source": source,
                "destination": destination,
                "date": date_of_travel.strftime('%d %b %Y'),
                "duration": trip_duration,
                "mode": travel_mode,
                "interests": interests,
                "diet": dietary_prefs
            })

            if response:
                st.subheader(f"🗺️ Your {trip_duration}-Day {destination} Itinerary")
                st.markdown(response, unsafe_allow_html=True)

                itinerary_markdown = f"""
                # 🌍 Travel Itinerary for {destination}
                ### ✈️ Trip Details:
                - **From:** {source}
                - **To:** {destination}
                - **Date:** {date_of_travel.strftime('%d %b %Y')}
                - **Duration:** {trip_duration} days
                - **Preferred Mode:** {travel_mode}
                - **Interests:** {', '.join(interests) if add_prefs else 'General'}
                - **Dietary Preferences:** {dietary_prefs if add_prefs else 'None'}

                ## 📌 Itinerary Plan:
                {response}
                """
                st.download_button("📥 Download Itinerary", data=itinerary_markdown.encode('utf-8'), file_name=f"{destination}_itinerary.md", mime="text/markdown")
    else:
        st.warning("⚠️ Please fill in all required fields.")

