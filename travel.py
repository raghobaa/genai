import streamlit as st
import google.generativeai as genai

# Configure Gemini API (Replace with your actual API key)
genai.configure(api_key="AIzaSyCHGvCV_UsrQLx8EZrb58IQ9qqQEyRNcYI")

gemini_model = genai.GenerativeModel(model_name="models/gemini-2.0-pro-exp-02-05")

st.title("AI-Powered Travel Planner")

# User Inputs
source = st.text_input("Enter Source Location", placeholder="E.g., New York")
destination = st.text_input("Enter Destination Location", placeholder="E.g., Los Angeles")
date = st.date_input("Select Travel Date")
mode_of_travel = st.selectbox("Preferred Mode of Travel", ["Flight", "Train", "Bus", "Car", "Any"])

if st.button("Plan My Trip"):
    if source and destination:
        travel_query = f"Plan a trip from {source} to {destination} on {date}. Preferred mode: {mode_of_travel}. Include estimated costs, best time to travel, and must-visit places."
        response = gemini_model.generate_content(travel_query)
        
        if response:
            st.subheader("Your Travel Plan:")
            st.write(response.text)
        else:
            st.error("Could not generate a travel plan. Please try again.")
    else:
        st.warning("Please enter both source and destination.")