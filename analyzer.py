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
You are a highly skilled Marketing Messaging Analyst.
Your task is to analyze website content and provide three mandatory metrics in the requested JSON structure.
You MUST derive the insights based ONLY on the provided text.
The 'Hook Score' must be a percentage between 0 and 100.
The 'Audience Persona' must be a single, concise sentence.
The 'Conversion Killers' MUST be a list of exactly 3 specific phrases, jargon terms, or unclear statements.
"""

def analyze_marketing_insights(hook_text: str, full_text: str) -> dict:
    """
    Calls the Gemini API to analyze the website content and return structured insights.

    Args:
        hook_text (str): The main headline and first paragraph (for Hook Score).
        full_text (str): The entire clean content of the page (for Persona and Killers).

    Returns:
        dict: A dictionary containing the structured analysis results or an error message.
    """
    # The client relies on the GEMINI_API_KEY environment variable,
    # which is loaded from the .env file by app.py.
    try:
        client = genai.Client()
    except Exception as e:
        return {"error": f"Failed to initialize Gemini client. Is API Key configured? Error: {e}"}

    # The main user prompt combining the specific requirements and the data.
    user_prompt = f"""
    Analyze the following website content.

    1. HOOK CONTENT (For Hook Score only):
    ---
    {hook_text}
    ---

    2. FULL PAGE CONTENT (For Persona and Conversion Killers):
    ---
    {full_text}
    ---
    """

    # --- Exponential Backoff Logic ---
    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash-preview-09-2025',
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    response_schema=ANALYSIS_SCHEMA,
                ),
            )

            # Parse the JSON string response into a Python dictionary
            return json.loads(response.text)

        except APIError as e:
            # Handle transient API issues with exponential backoff
            if attempt < MAX_RETRIES - 1:
                wait_time = 2 ** attempt  # 1s, 2s, 4s, 8s...
                print(f"API Error: {e}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                return {"error": f"API call failed after {MAX_RETRIES} attempts: {e}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred during AI analysis: {e}"}

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
        print(json.dumps(results, indent=4))