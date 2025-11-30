import os
import json
import time
from google import genai
from google.genai import types
from google.genai.errors import APIError

# The maximum number of retries for API calls
MAX_RETRIES = 5

# --- API Configuration and Structured Response Schema ---

# This schema is CRITICAL. It ensures the AI returns the three specific outputs
# (Hook Score, Persona, Killers) in a clean JSON format every time.
# This demonstrates required Prompt Engineering skills.
ANALYSIS_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "hook_score": types.Schema(
            type=types.Type.INTEGER,
            description="A numerical score (0-100) indicating how compelling the opening headline and first paragraph are."
        ),
        "audience_persona": types.Schema(
            type=types.Type.STRING,
            description="A single, concise sentence predicting the specific target audience of the page (e.g., 'Enterprise CTOs')."
        ),
        "conversion_killers": types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(type=types.Type.STRING),
            description="A list of 3 specific confusing, jargon-heavy, or vague phrases found in the content."
        ),
    },
    required=["hook_score", "audience_persona", "conversion_killers"]
)

# This system instruction sets the persona and rules for the AI.
SYSTEM_PROMPT = """
You are a world-class marketing messaging analyst. Your task is to evaluate a webpage's content, focusing on the clarity and effectiveness of its opening statement (the Hook).

Instructions:
1.  **SCORE:** Assign a 'hook_score' from 0 to 100 based on how compelling, clear, and audience-focused the 'hook_text' is.
2.  **PERSONA:** Predict the most specific 'audience_persona' the *entire* 'full_text' seems to target.
3.  **KILLERS:** Identify 3 specific phrases from the 'full_text' that are vague, overly jargon-heavy, or act as 'conversion killers' (friction points that confuse a customer).
4.  **FORMAT:** You MUST return a single, valid JSON object that strictly adheres to the provided schema. Do not include any external markdown, code blocks, or explanations outside the JSON object.
"""

def analyze_marketing_insights(hook_text, full_text):
    """
    Calls the Gemini API to analyze the content and returns structured marketing insights.

    यह फ़ंक्शन Gemini API को कॉल करता है, कंटेंट का विश्लेषण करता है, और संरचित JSON डेटा लौटाता है।
    """
    
    # CRITICAL FIX: Explicitly pass the API Key from the environment to the client
    # This ensures the client uses the key loaded by dotenv in app.py
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"error": "GEMINI_API_KEY not found in environment for analyzer client."}
        
    try:
        # Initialize the client with the explicitly provided API key
        client = genai.Client(api_key=api_key)
    except Exception as e:
        # This handles initialization errors, often related to the key format
        return {"error": f"Failed to initialize Gemini Client: {e}"}

    # The main prompt for the model
    user_prompt = f"""
    HOOK TEXT (for scoring):
    ---
    {hook_text}
    ---

    FULL CONTENT TEXT (for context/persona):
    ---
    {full_text}
    ---
    
    Analyze the above content based on your instructions.
    """

    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[user_prompt],
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    response_schema=ANALYSIS_SCHEMA,
                ),
            )
            # If successful, parse the JSON text and return the Python object
            return json.loads(response.text)

        except APIError as e:
            # Handle transient API issues with exponential backoff
            if attempt < MAX_RETRIES - 1:
                wait_time = 2 ** attempt  # 1s, 2s, 4s, 8s...
                print(f"API Error: {e}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                # After max retries, check for the specific 403 issue
                if "403 PERMISSION_DENIED" in str(e) or "leaked" in str(e):
                     # Simplified, actionable error message for the Streamlit UI
                     return {"error": "API Authorization Error: The Gemini service denied the request. Please ensure your API Key is correct, has not been revoked, and that **Billing is enabled** on your Google Cloud project."}
                
                # Simplified generic error message for other persistent API issues
                return {"error": f"The AI analysis failed after {MAX_RETRIES} attempts. The service may be temporarily unavailable. Please try again. Detailed error: {e}"}
        except Exception as e:
            # Handle non-API related exceptions (e.g., malformed JSON response)
            return {"error": f"An unexpected error occurred during AI analysis or JSON parsing: {e}"}

# --- Testing Block ---
if __name__ == '__main__':
    # NOTE: This test requires GEMINI_API_KEY to be set in your environment or .env file.
    mock_hook = "Introducing the revolutionary synergy matrix. Drive your pipeline forward with disruptive solutions."
    mock_full = "Our team of dedicated thought leaders is focused on providing unparalleled B2B SaaS solutions. We empower Enterprise CTOs to pivot to cloud-native infrastructures. We are platform-agnostic, delivering maximum shareholder value by leveraging our proprietary ecosystem. Introducing the revolutionary synergy matrix. Drive your pipeline forward with disruptive solutions."

    print("--- Running AI Analysis Test ---")
    
    results = analyze_marketing_insights(mock_hook, mock_full)
    
    if "error" in results:
        print(f"\nAI Analysis Error: {results['error']}")
    else:
        print("\n--- AI Analysis Success! ---")
        print(json.dumps(results, indent=2))
