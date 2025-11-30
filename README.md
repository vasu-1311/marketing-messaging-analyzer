 Marketing Messaging Analyzer (Gemini API + Streamlit)

This project is a web-based tool built using Streamlit and the Google Gemini API. Its purpose is to scrape content from any public website URL and then analyze its marketing messaging to provide critical, structured insights.

 Features

Content Scraping: Efficiently fetches HTML content from a given URL and extracts clean, main body text by removing boilerplate elements like navigation, scripts, and styles.

AI-Powered Analysis: Performs a deep marketing analysis of the content using the Google Gemini API.

Structured Output: The analysis is guaranteed to be delivered in a specific, structured JSON format (schema) which includes:

Hook Score (0-100%): A numerical score indicating how compelling the headline and first paragraph are at grabbing the visitor's attention.

Audience Persona: A concise, single-sentence prediction of the page's specific target audience.

Conversion Killers: A list of 3 specific, confusing, or jargon-heavy phrases found in the content that could cause friction or lose a customer.

Interactive UI: A simple and engaging user interface provided by Streamlit.

 Setup and Installation

Follow these steps to set up and run the application locally.

1. Prerequisites

Python (3.8+)

Gemini API Key

2. Clone the Repository

git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
cd your-repo-name


3. Set up Virtual Environment

It is highly recommended to use a virtual environment to manage dependencies.

python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows


4. Install Dependencies

Install all necessary Python libraries from the requirements.txt file:

pip install -r requirements.txt


5. Configure API Key

You need to create a file named .env in the root of your project folder and add your Gemini API key to it.

.env file:

GEMINI_API_KEY='YOUR_GEMINI_API_KEY_HERE'


 Running the Application

Once the setup is complete, you can start the application using Streamlit:

streamlit run app.py


This command will open the application in your default web browser (usually at http://localhost:8501/).

 File Structure

File

Description

app.py

The main entry point of the Streamlit application. Handles the UI, loads the key from .env, and calls the scraping and AI analysis functions.

scraper.py

Contains the web scraping logic. Uses requests and beautifulsoup4 to fetch the URL and extract the clean text content.

analyzer.py

Contains the core AI analysis logic. Calls the Gemini API, sets the system prompt, and ensures structured JSON output using a response_schema. Includes robust exponential backoff for API failure handling.

requirements.txt

Lists all the Python dependencies required for the project.

.env

Securely stores environment variables, specifically the GEMINI_API_KEY. This file should be excluded from Git commits.
