# File: cli_chat.py
# CLI Chat Application using Google Gemini API with Function Calling for Feedback

import google.generativeai as genai
import os
import json
from datetime import datetime
from dotenv import load_dotenv
import traceback # For detailed error reporting if issues arise

# --- Configuration & Initialization ---

# Load API Key from .env file for security
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file.")

# Configure the Gemini SDK
genai.configure(api_key=API_KEY)

# --- Function Declaration for Gemini API ---
# Defines the structure of the 'submit_review_rating' function for the Gemini model
# This allows the model to call it with the correct arguments.
submit_review_rating_func = genai.protos.FunctionDeclaration(
    name="submit_review_rating",
    description="Submits the user's chat session review and rating (1-5) upon exit intent.",
    parameters=genai.protos.Schema(
        type=genai.protos.Type.OBJECT,
        properties={
            "review": genai.protos.Schema(
                type=genai.protos.Type.STRING,
                description="User's textual feedback."
            ),
            "rating": genai.protos.Schema(
                type=genai.protos.Type.INTEGER,
                description="User's 1-5 rating."
            )
        },
        required=["review", "rating"]
    )
)

# --- Tool Configuration ---
# Bundles the function declaration into a Tool for the model
feedback_tool = genai.protos.Tool(
    function_declarations=[submit_review_rating_func]
)

# --- Model Configuration ---
# Sets up the specific Gemini model and makes the feedback tool available to it
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash', # Model must support function calling
    tools=[feedback_tool]
)

# --- File Paths ---
FEEDBACK_FILE = "feedback.txt"
HISTORY_FILE = "chat_history.txt" # Optional: For logging conversations

# --- Helper Functions ---

def save_feedback(review: str, rating: any):
    """
    Saves the provided review and rating to the feedback file.
    Validates the rating to ensure it's an integer between 1 and 5.
    Handles potential float inputs (e.g., 5.0) from the LLM.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rating_to_save = "Invalid" # Default assumes invalid rating
    try:
        if rating is not None:
            try:
                rating_float = float(rating) # Handle int/float conversion
                if 1 <= rating_float <= 5 and rating_float == int(rating_float):
                    rating_to_save = int(rating_float) # Valid integer rating
                else:
                    # Log warnings for out-of-range or non-integer ratings
                    if not (1 <= rating_float <= 5):
                         print(f"\n[System] Warning: Rating '{rating}' out of range (1-5). Saving as 'Invalid'.")
                    else: # Must be non-integer (e.g., 4.5)
                         print(f"\n[System] Warning: Non-integer rating '{rating}' received. Saving as 'Invalid'.")
            except (ValueError, TypeError):
                 print(f"\n[System] Warning: Invalid rating format '{rating}'. Saving as 'Invalid'.")
        else:
            print(f"\n[System] Warning: No rating value received. Saving as 'Invalid'.")

        # Append validated data to the feedback file
        with open(FEEDBACK_FILE, "a", encoding="utf-8") as f:
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Rating: {rating_to_save}\n")
            f.write(f"Review: {review}\n")
            f.write("---\n")
        print(f"\n[System] Feedback saved to {FEEDBACK_FILE}")

    except Exception as e:
        print(f"\n[System] Error saving feedback: {e}")
        # traceback.print_exc() # Keep commented unless needed for evaluator debugging


def log_conversation(user_message: str, bot_response: str):
    """Appends a single turn of conversation to the history file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] User: {str(user_message)}\n")
            f.write(f"[{timestamp}] Bot: {str(bot_response)}\n")
            f.write("---\n")
    except Exception as e:
        print(f"\n[System] Error logging conversation: {e}")
        # traceback.print_exc() # Keep commented unless needed for evaluator debugging

# --- Main Chat Logic ---

def main():
    """Initiates and manages the main chat session loop."""
    print("Welcome to the Gemini Chat App!")
    print("Type your message or say 'bye', 'exit', etc. to finish.")

    # Start chat with automatic function calling enabled
    chat = model.start_chat(enable_automatic_function_calling=True)

    while True:
        try:
            user_input = input("\nYou: ")
            if not user_input:
                continue

            # Send message and get response (handles function call cycle implicitly)
            response = chat.send_message(user_input)

            exit_requested = False
            bot_response_text = ""
            function_call_processed = False

            # Process all parts of the response (text and/or function calls)
            if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                 for part in response.candidates[0].content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        function_call_processed = True
                        if part.function_call.name == "submit_review_rating":
                            args = part.function_call.args
                            review = args.get('review', 'N/A')
                            rating = args.get('rating', None)
                            print("\n[System] Gemini extracted feedback.")
                            save_feedback(review, rating)
                            exit_requested = True # Signal loop exit after this turn
                    elif hasattr(part, 'text') and part.text:
                        bot_response_text += part.text + " " # Accumulate all text parts

            # Consolidate and print the bot's textual response for the turn
            bot_response_text = bot_response_text.strip()
            if bot_response_text:
                print(f"\nGemini: {bot_response_text}")
            elif function_call_processed: # If only function call, provide default msg
                 print(f"\nGemini: Thank you for your feedback. Goodbye!")

            # Log the turn
            log_entry = "[No Text Response]"
            if function_call_processed:
                 log_entry = bot_response_text if bot_response_text else "[Function Call Triggered & Processed]"
            elif bot_response_text:
                 log_entry = bot_response_text
            log_conversation(user_input, log_entry)

            # Exit loop if feedback function call was processed
            if exit_requested:
                print("\n[System] Exiting chat.")
                break

        # Handle common interruptions and API errors
        except KeyboardInterrupt:
            print("\n[System] Chat interrupted by user. Exiting.")
            break
        except (genai.types.generation_types.StopCandidateException) as e:
             print(f"\n[System] Generation stopped: {e}")
        except (genai.types.generation_types.BlockedPromptException) as e:
            print(f"\n[System] Your prompt was blocked: {e}")
            log_conversation(user_input, "[Bot Response Blocked]")
        except Exception as e:
            print(f"\n[System] An unexpected error occurred: {e}")
            traceback.print_exc() # Show details for unexpected errors
            log_conversation(user_input, f"[System Error: {e}]")

# --- Function Definition for SDK Integration ---
# This function needs to be defined locally for the SDK's automatic function calling.
def submit_review_rating(review: str, rating: any):
    """
    Local function called by the SDK when Gemini uses the 'submit_review_rating' tool.
    Its primary role is to exist and return a status to Gemini via the SDK.
    Actual feedback saving is handled in the main loop.
    """
    # This local print is useful for seeing the SDK call happen, can be removed.
    # print(f"\n[Function Call Handler] SDK intercepted call: review='{review}', rating={rating} (type: {type(rating)})")
    return {"status": "Feedback received by application"}

# --- Script Execution Entry Point ---
if __name__ == "__main__":
    main()
