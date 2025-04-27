import google.generativeai as genai
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# --- Configuration & Initialization ---
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file.")

genai.configure(api_key=API_KEY)

# --- Function Declaration for Gemini ---
submit_review_rating_func = genai.protos.FunctionDeclaration(
    name="submit_review_rating",
    description="Submit a user's review and rating for the chat session when they indicate they want to exit.",
    parameters=genai.protos.Schema(
        type=genai.protos.Type.OBJECT,
        properties={
            "review": genai.protos.Schema(type=genai.protos.Type.STRING, description="The user's textual feedback."),
            "rating": genai.protos.Schema(type=genai.protos.Type.INTEGER, description="The user's rating from 1 to 5.")
        },
        required=["review", "rating"]
    )
)

# --- Tool Configuration ---
feedback_tool = genai.protos.Tool(
    function_declarations=[submit_review_rating_func]
)

# --- Model Configuration ---
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash', # Or another model supporting function calling
    tools=[feedback_tool]
)

# --- File Paths ---
FEEDBACK_FILE = "feedback.txt"
HISTORY_FILE = "chat_history.txt" # Bonus

# --- Helper Functions ---
def save_feedback(review: str, rating: int):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        rating_to_save = "Invalid"
        if isinstance(rating, int) and 1 <= rating <= 5:
            rating_to_save = rating
        else:
             print(f"\n[System] Warning: Invalid rating '{rating}' received. Saving as 'Invalid'.")

        with open(FEEDBACK_FILE, "a", encoding="utf-8") as f:
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Rating: {rating_to_save}\n")
            f.write(f"Review: {review}\n")
            f.write("---\n")
        print(f"\n[System] Feedback saved to {FEEDBACK_FILE}")
    except Exception as e:
        print(f"\n[System] Error saving feedback: {e}")

def log_conversation(user_message: str, bot_response: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] User: {user_message}\n")
            f.write(f"[{timestamp}] Bot: {bot_response}\n")
            f.write("---\n")
    except Exception as e:
        print(f"\n[System] Error logging conversation: {e}")

# --- Main Chat Logic ---
def main():
    print("Welcome to the Gemini Chat App!")
    print("Type your message or say 'bye', 'exit', etc. to finish.")

    chat = model.start_chat(enable_automatic_function_calling=True)

    while True:
        try:
            user_input = input("\nYou: ")
            if not user_input:
                continue

            response = chat.send_message(user_input)
            exit_requested = False

            # Check if the model's response contains a function call triggered by exit intent
            if response.candidates[0].content.parts:
                 part = response.candidates[0].content.parts[0]
                 if part.function_call and part.function_call.name == "submit_review_rating":
                    args = part.function_call.args
                    review = args.get('review', 'N/A')
                    rating = args.get('rating', None)

                    print("\n[System] Gemini extracted feedback.")
                    save_feedback(review, rating)
                    # The SDK handles the function response back to Gemini automatically.
                    # Gemini will then generate its final message (often a thank you/goodbye).
                    # We print this final message below.
                    exit_requested = True # Mark that we should exit after printing the final response

            # Print the bot's response (either normal text or final text after function call)
            bot_response = response.text.strip()
            print(f"\nGemini: {bot_response}")

            # Log conversation (Bonus) - Log before potentially exiting
            log_conversation(user_input, bot_response if bot_response else "[Function Call Triggered]")

            if exit_requested:
                print("\n[System] Exiting chat.")
                break # Exit the loop

        except KeyboardInterrupt:
            print("\n[System] Chat interrupted. Exiting.")
            break
        except (genai.types.generation_types.StopCandidateException) as e:
             print(f"\n[System] Generation stopped: {e}")
        except (genai.types.generation_types.BlockedPromptException) as e:
            print(f"\n[System] Prompt blocked: {e}")
            log_conversation(user_input, "[Bot Response Blocked]")
        except Exception as e:
            print(f"\n[System] An error occurred: {e}")
            log_conversation(user_input, f"[System Error: {e}]")
            # Consider breaking here on critical errors if desired

# --- Function Definition for SDK ---
# This function needs to exist so enable_automatic_function_calling finds it
def submit_review_rating(review: str, rating: int):
    """
    Placeholder function called by the SDK.
    The actual saving is handled in the main loop after checking the response.
    Returns a dict confirming receipt to Gemini.
    """
    print(f"\n[Function Call Handler] Intercepted: review='{review}', rating={rating}")
    # Return value is sent back to Gemini by the SDK as the function's result
    return {"status": "Feedback received by application"}

if __name__ == "__main__":
    main()
