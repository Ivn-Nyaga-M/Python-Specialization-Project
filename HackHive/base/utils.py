from dotenv import load_dotenv
import os
import google.generativeai as genai

# Load API key dynamically from .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Configure the Gemini API SDK
genai.configure(api_key=api_key)

def query_gemini_api(prompt):
    """
    Queries the Gemini API and returns the generated content.
    """
    try:
        # Initialize the model
        model = genai.GenerativeModel("gemini-1.5-flash")  # Update model name if needed
        
        # Generate content (Adjust based on correct method signature)
        response = model.generate_content(prompt)  # Pass only the prompt if required
        
        # Return the generated content
        return response.text if hasattr(response, 'text') else "No response text found."

    except Exception as e:  # Handle generic exceptions
        print(f"Unexpected error: {e}")
        return "Error: Unable to process your request. Please try again later."
