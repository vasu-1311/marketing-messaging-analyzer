import streamlit as st
import os
from dotenv import load_dotenv 
from scraper import fetch_and_clean_content
from analyzer import analyze_marketing_insights

# --- Load Environment Variables from .env file ---

load_dotenv()

# --- Configuration (Streamlit UI Setup) ---
st.set_page_config(
    page_title="Messaging Insight Analyzer",
    layout="centered",
    initial_sidebar_state="auto"
)

# --- Check API Key ---
if not os.getenv("GEMINI_API_KEY"):
    st.error("🚨 GEMINI_API_KEY environment variable not found.")
    st.warning("Please create a file named `.env` in your project folder with the content: `GEMINI_API_KEY='YOUR_KEY_HERE'`")

# --- UI Layout ---
st.title("💡 Marketing Messaging Analyzer")
st.markdown("Enter a public website URL below to extract core content and generate marketing insights using AI.")

# Input field
url_input = st.text_input(
    "Website URL (e.g., https://www.google.com)",
    placeholder="https://www.yourcompanyblog.com/post-title"
)

# Analysis Button
if st.button("Analyze Messaging", type="primary"):
    if not os.getenv("GEMINI_API_KEY"):
        st.error("API Key is missing. Please check your .env file.")
    elif not url_input:
        st.error("Please enter a valid URL.")
    else:
        # 1. Fetching and Cleaning Content (from scraper.py)
        with st.spinner(f"Step 1/2: Fetching and cleaning content from {url_input}..."):
            #fetch_and_clean_content 
            scrape_results = fetch_and_clean_content(url_input) 

        if "error" in scrape_results:
            st.error(f"Scraping Error: {scrape_results['error']}")
            st.warning("Could not proceed with AI analysis due to scraping failure.")
        else:
            full_text = scrape_results["full_text"]
            hook_text = scrape_results["hook_text"]

            st.success("Content extracted successfully!")
            with st.expander("View Cleaned Text Sample"):
                 st.write(full_text[:500] + "...")
                 st.caption(f"Total characters: {len(full_text)}")
            
            # 2. AI Analysis (from analyzer.py)
            with st.spinner("Step 2/2: Analyzing content and generating insights (this may take a moment)..."):
                analysis_results = analyze_marketing_insights(hook_text, full_text)

            if "error" in analysis_results:
                st.error(f"AI Analysis Error: {analysis_results['error']}")
            else:
                st.success("Analysis Complete!")
                
                # --- Display Results (The 3 Mandatory Outputs) ---
                
                st.header("🎯 Key Messaging Insights")

                # 1. Hook Score (0-100%)
                hook_score = analysis_results.get('hook_score', 0)
                st.subheader("1. Hook Score")
                st.metric(
                    label="Opening Compellingness (Headline + First Paragraph)",
                    value=f"{hook_score}%",
                    delta_color="off"
                )
                if hook_score < 50:
                    st.info("The opening hook needs significant work to grab visitor attention quickly.")
                elif hook_score < 80:
                    st.info("The hook is decent but could be punchier or clearer.")
                else:
                    st.info("Excellent hook! The opening is highly compelling.")


                # 2. Audience Persona
                persona = analysis_results.get('audience_persona', 'N/A')
                st.subheader("2. Target Audience Persona")
                st.markdown(f"**Prediction:** *{persona}*")
                st.caption("This prediction helps verify if the tone matches the intended reader.")


                # 3. Conversion Killers
                killers = analysis_results.get('conversion_killers', [])
                st.subheader("3. Conversion Killers (Friction Points)")
                if killers:
                    st.warning("⚠️ These phrases might confuse or lose customers:")
                    for i, killer in enumerate(killers):
                        st.markdown(f"**{i+1}.** `{killer}`")
                else:
                    st.info("No obvious jargon or confusing phrases were found.")
