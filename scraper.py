import requests
from bs4 import BeautifulSoup

def fetch_and_clean_content(url):
    """
    Fetches the HTML content from a given URL and attempts to extract
    only the main, visible text content, removing boilerplate elements.

    Args:
        url (str): The public website URL to scrape.

    Returns:
        dict: A dictionary containing the 'full_text' and 'hook_text', or an 'error'.
    """
    try:
        # Use a common User-Agent to mimic a browser and avoid simple blocks
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Fetch the content with a timeout for reliability (15 seconds should be enough)
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # --- 1. Clean the HTML (Removing clutter like nav bars, scripts, styles) ---
        # Remove all non-essential elements like scripts, ads, and navigation to get clean text.
        for element in soup(["script", "style", "nav", "footer", "header", "aside", "form", "meta"]):
            element.decompose()

        # Find the main content container (body is used as the safest fallback)
        main_content = soup.find('body')
        if not main_content:
            return {"error": "Could not find main content (body tag)."}

        # Extract all visible text for the AI model's full analysis.
        raw_text = main_content.get_text(separator=' ', strip=True)

        # --- 2. Extract Hook Content (H1 + First Paragraph) ---
        # Get the 'hook' content (H1 + first paragraph) for the Hook Score.
        hook_text = ""
        
        # Get the main headline
        h1 = soup.find('h1')
        if h1:
            hook_text += h1.get_text(strip=True) + " "

        # Get the very first clean paragraph
        first_p = soup.find('p')
        if first_p:
            hook_text += first_p.get_text(strip=True)

        return {
            "full_text": raw_text,
            "hook_text": hook_text.strip()
        }

    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed (Connection/Timeout/HTTP Error): {e}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred during scraping: {e}"}

# --- Testing Block ---
if __name__ == '__main__':
    # Simple test to check if the scraper works when run directly.
    test_url = "https://www.example.com" 
    print(f"--- Running Scraper Test for: {test_url} ---")
    
    results = fetch_and_clean_content(test_url)

    if "error" in results:
        print(f"\n--- ERROR ---\n{results['error']}")
    else:
        print("\n--- SCRAPING SUCCESSFUL ---")
        print(f"Hook Content (for Hook Score): {results['hook_text'][:150]}...")
        print(f"Total Content Length: {len(results['full_text'])} characters")
        print("\nFull Text Preview (first 500 chars):")
        print("-----------------------------------")
        print(results['full_text'][:500] + "...")
