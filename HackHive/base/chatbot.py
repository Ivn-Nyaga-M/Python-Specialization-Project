from .utils import query_gemini_api

class ChatBot:
    """
    ChatBot class to manage conversation context and interact with the Gemini API.
    """
    def __init__(self):
        self.conversation_history = []

    def get_response(self, user_message):
        """
        Processes user input, updates the context, and queries the Gemini API.
        """
        # Add user's message to the conversation history
        self.conversation_history.append({"role": "user", "message": user_message})

        # Construct the prompt from the conversation history
        prompt = "\n".join(
            f"{msg['role'].capitalize()}: {msg['message']}" for msg in self.conversation_history
        )

        # Query the Gemini API
        bot_message = query_gemini_api(prompt)

        # Add bot's response to the conversation history
        if bot_message:
            self.conversation_history.append({"role": "bot", "message": bot_message})
        else:
            bot_message = "Error: No response from the AI."

        return bot_message

    def clear_history(self):
        """
        Clears the conversation history.
        """
        self.conversation_history = []

    def to_dict(self):
        """
        Serializes the chatbot state to a dictionary.
        """
        return {"conversation_history": self.conversation_history}

    @staticmethod
    def from_dict(data):
        """
        Deserializes the chatbot state from a dictionary.
        """
        chatbot = ChatBot()
        chatbot.conversation_history = data.get("conversation_history", [])
        return chatbot

    def handle_conversation(self):
        """
        Handles a continuous conversation via the command line.
        """
        print("Welcome to the AI chatbot! Type 'exit' to quit.")
        while True:
            # Get user input
            user_input = input("You: ")
            if user_input.lower() == "exit":
                print("Goodbye!")
                break

            # Get and display the bot's response
            bot_message = self.get_response(user_input)
            print("Bot:", bot_message)


# Example usage for a standalone chat session
if __name__ == "__main__":
    bot = ChatBot()
    bot.handle_conversation()
