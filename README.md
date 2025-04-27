# CHATBOT


## Setup Instructions

Follow these steps to set up and run the application:

1.  **Prerequisites:**
    *   Python 3.7 or later installed.
    *   `pip` (Python package installer) available in your terminal.

2.  **Get Project Files:**
    *   Create a directory for your project (e.g., `gemini-chat-cli`).
    *   Download or create the `cli_chat.py` script (provided in the assignment solution) and place it inside this directory.

3.  **Get Gemini API Key:**
    *   **Visit: OR below link both works fine if you are logged in with any google account** [Google AI Studio](https://aistudio.google.com/apikey).
    *   **Visit:** [Google AI Studio](https://aistudio.google.com/).
    *   **Sign in** with your Google account.
    *   Click **"Get API key"** (usually found on the left sidebar or top of the page).
    *   Click **"Create API key in new project"** (or select an existing project if you prefer).
    *   **Copy the generated API key.** Treat this key like a password – keep it secure and private!

4.  **Configure API Key (`.env` file):**
    *   Inside your project directory, create a new file named exactly `.env` (note the leading dot).
    *   Open the `.env` file in a text editor.
    *   Add the following line, replacing `YOUR_API_KEY` with the actual API key you copied in the previous step:
        ```dotenv
        GOOGLE_API_KEY = YOUR_API_KEY
        ```
    *   Save and close the `.env` file.
    *   **Security Note:** If you are using Git for version control, **add `.env` to your `.gitignore` file** immediately to prevent accidentally committing your secret API key to a public repository.

5.  **Install Dependencies (`requirements.txt` file):**
    *   Inside your project directory, create a new file named `requirements.txt`.
    *   Open `requirements.txt` and add the following lines:
        ```txt
        google-generativeai
        python-dotenv
        ```
    *   Save and close the `requirements.txt` file.
    *   Now, open your terminal or command prompt, navigate (`cd`) into your project directory, and run the following command to install the necessary Python libraries:
        ```bash
        pip install -r requirements.txt
        ```

## How to Run the Application

1.  Ensure you have completed all the setup steps above.
2.  Open your terminal or command prompt.
3.  Navigate (`cd`) into your project directory (the one containing `cli_chat.py`, `.env`, and `requirements.txt`).
4.  Run the application using Python:
    ```bash
    python cli_chat.py
    ```
5.  The application will display a welcome message. You can now type your messages to Gemini and press Enter.
6.  To finish the chat, use phrases like "bye", "exit", "end chat", "I want to leave", "I'm finished", etc.
7.  The application, using Gemini, should recognize your intent to leave and ask for feedback (a short review and a rating from 1 to 5).
8.  Provide your feedback naturally (e.g., "It was very helpful, 5 stars" or "4/5, good responses").
9.  The application will use function calling to extract the review and rating, save them to `feedback.txt`, print a final message, and exit.
10. If the bonus logging is enabled in the script, the full conversation will also be appended to `chat_history.txt`.

## Example Chat Session

Here’s how a typical interaction might look in your terminal:

```plaintext
Welcome to the Gemini Chat App!
Type your message or say 'bye', 'exit', etc. to finish.

You: Hi! Can you explain the difference between HTTP and HTTPS?

Gemini: Hello! Certainly. HTTP (Hypertext Transfer Protocol) is the standard protocol for transferring web pages and other data over the internet. HTTPS (Hypertext Transfer Protocol Secure) is the secure version of HTTP. The key difference is that HTTPS encrypts the data exchanged between your browser and the website using TLS/SSL protocols, making it much harder for attackers to intercept or tamper with the information. You can tell if a site uses HTTPS by the padlock icon in your browser's address bar and the URL starting with "https://".

You: That was clear, thank you. I need to sign off now, bye.

Gemini: Okay, understood. Before you go, would you mind providing a short review of our chat and a rating from 1 to 5? Your feedback helps improve the experience!

You: Yes, the explanation was excellent. 5 stars.

[System] Gemini extracted feedback.
[Function Call Handler] SDK intercepted call: review='the explanation was excellent.', rating=5
[System] Feedback saved to feedback.txt

Gemini: Thank you very much for your feedback! Have a great day! Goodbye!

[System] Exiting chat.
