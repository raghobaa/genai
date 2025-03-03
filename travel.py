import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from datetime import date, timedelta
import os

# Streamlit configuration
st.set_page_config(
    page_title="AI-Powered Travel Planner",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stSlider > div > div > div > div {
        background: black!important;
    }
    .st-bw {
        background-color: black;
    }
    .travel-card {
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        background: black;
    }
</style>
""", unsafe_allow_html=True)

# Main title
st.markdown("<h1 style='text-align: center; color: #2a4a7d;'>AI-Powered Travel Planner</h1>",
            unsafe_allow_html=True)

# User inputs
with st.expander("✈️ Enter Trip Details", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        source = st.text_input("From:", placeholder="Enter departure city")
    with col2:
        destination = st.text_input("To:", placeholder="Enter destination city")
    with col3:
        trip_duration = st.slider("Trip Duration (days):", 1, 30, 3)

    col4, col5 = st.columns(2)
    with col4:
        date_of_travel = st.date_input("Travel Date:", min_value=date.today())
    with col5:
        travel_mode = st.selectbox("Preferred Mode:", ["Any", "Flight", "Train", "Bus", "Cab"])

    add_prefs = st.checkbox("Add Advanced Preferences")
    if add_prefs:
        col6, col7 = st.columns(2)
        with col6:
            interests = st.multiselect("Interests:", ["Historical", "Adventure", "Cultural", "Nature", "Food"])
        with col7:
            dietary_prefs = st.selectbox("Dietary Preferences:", ["None", "Vegetarian", "Vegan", "Gluten-Free"])

# Cached LLM response
@st.cache_data(ttl=3600, show_spinner=False)
def get_travel_plan(_chain, inputs):
    try:
        return _chain.invoke(inputs)
    except Exception as e:
        st.error(f"AI Service error: {str(e)}")
        return None

if st.button("Generate Travel Plan", use_container_width=True):
    if source and destination:
        with st.spinner("🧠 Analyzing best options..."):
            # Initialize components
            chat_template = ChatPromptTemplate.from_messages([
                ("system", """You are an expert travel planner. Create detailed itineraries with:
                - Transport options (cost, duration, pros/cons)
                - Accommodation suggestions
                Format using markdown with emojis and clear sections"""),
                ("human", """Plan {duration}-day trip from {source} to {destination} starting {date}.
                Preferred transport: {mode}. Interests: {interests}. Dietary: {diet}.""")
            ])

            llm = ChatGoogleGenerativeAI(api_key="AIzaSyCHGvCV_UsrQLx8EZrb58IQ9qqQEyRNcYI", model="gemini-1.5-pro-latest")
            chain = chat_template | llm | StrOutputParser()

            # Generate plan
            response = get_travel_plan(chain, {
                "source": source,
                "destination": destination,
                "date": date_of_travel.strftime('%d %b %Y'),
                "duration": trip_duration,
                "mode": travel_mode,
                "interests": interests if add_prefs else "general",
                "diet": dietary_prefs if add_prefs else "none"
            })

            if response:
                # Display results
                st.subheader(f"🗺️ Your {trip_duration}-Day {destination} Itinerary")

                # AI Response
                with st.expander("📝 Full Travel Plan", expanded=True):
                    st.markdown(response)

                # Additional Features
                with st.container():
                    st.subheader("🔗 Helpful Resources")
                    cols = st.columns(4)

                    # Navigation
                    with cols[0]:
                        st.markdown(f"""
                        <div class="travel-card">
                            <h4>🗺️ Navigation</h4>
                            <a href="{get_navigation_link(source, destination, travel_mode)}" target="_blank">
                                Directions to {destination}
                            </a>
                        </div>
                        """, unsafe_allow_html=True)

                    # Local Services
                    services = {
                        "Hotels": "hotels",
                        "Restaurants": "restaurants",
                        "Attractions": "tourist+attractions",
                        "Hospitals": "hospitals"
                    }
                    for col, (service, query) in zip(cols[1:], services.items()):
                        with col:
                            st.markdown(f"""
                            <div class="travel-card">
                                <h4>🏨 {service}</h4>
                                <a href="{get_google_places_link(destination, query)}" target="_blank">
                                    Find {service} in {destination}
                                </a>
                            </div>
                            """, unsafe_allow_html=True)

                # Export Options
                st.download_button(
                    label="📥 Download PDF Itinerary",
                    data=response.encode('utf-8'),
                    file_name=f"{destination}_itinerary.md",
                    mime="text/markdown"
                )
    else:
        st.warning("Please fill in all required fields")

# Helper functions
def get_navigation_link(source, destination, mode):
    mode_mapping = {"Flight": "d", "Train": "r", "Bus": "b", "Cab": "d"}
    return f"https://www.google.com/maps/dir/?api=1&origin={source}&destination={destination}"

def get_google_places_link(location, place_type):
    return f"https://www.google.com/maps/search/{place_type}+near+{location}"
