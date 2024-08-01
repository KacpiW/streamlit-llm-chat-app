import json
import os

from dotenv import load_dotenv
import streamlit as st

from models import claude, chatgpt, llama
from app.database import (
    create_new_chat_history,
    save_chat_message,
    load_all_chat_messages,
    get_last_chat_message,
    load_all_chat_histories,
)

# Load environment variables
load_dotenv()

PERSISTENCE_FILE = "session_state.json"

def save_current_chat_id(chat_id):
    with open(PERSISTENCE_FILE, "w") as f:
        json.dump({"current_chat_id": chat_id}, f)

def load_current_chat_id():
    if os.path.exists(PERSISTENCE_FILE):
        with open(PERSISTENCE_FILE, "r") as f:
            data = json.load(f)
            return data.get("current_chat_id", None)
    return None

if st.session_state.get("current_chat_id", None) is None:
    st.session_state["current_chat_id"] = load_current_chat_id()

def clear_chat_history():
    """Create a new chat history in the database."""
    st.session_state["current_chat_id"] = None
    if os.path.exists(PERSISTENCE_FILE):
        os.remove(PERSISTENCE_FILE)

# Load CSS styles from a separate file
def load_css():
    with open("static/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def generate_response(model, prompt, temperature, max_tokens):
    if model == "Claude 3.5 Sonnet":
        return claude.generate_response(prompt, temperature, max_tokens)
    elif model == "chatGPT4-mini":
        return chatgpt.generate_response(prompt, temperature, max_tokens)
    elif model == "LLaMA":
        return llama.generate_response(prompt, temperature, max_tokens)
    else:
        return "Error: Invalid model selected."

def display_sidebar():
    with st.sidebar:
        st.title("Settings")
        st.write(
            "This app allows you to chat with different models. Select a model and start chatting!"
        )

        st.session_state["model_option"] = st.selectbox(
            "Choose a model", ("Claude 3.5 Sonnet", "chatGPT4-mini", "LLaMA")
        )
        st.session_state["temperature"] = st.slider(
            "Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.05
        )
        st.session_state["max_tokens"] = st.slider(
            "Max Tokens", min_value=1000, max_value=10000, value=4000, step=1000
        )
        st.button("Clear chat history", on_click=clear_chat_history)
        
        st.write("### Chat History:")
        chat_histories = load_all_chat_histories()
        sorted_histories = sorted(chat_histories, key=lambda x: x.id, reverse=True)
        
        for history in sorted_histories:
            if st.button(history.title, key=history.id, use_container_width=True):
                st.session_state["current_chat_id"] = save_current_chat_id(history.id)
                st.rerun()
        
def display_chat_message(role, content):
    message_html = f"""
    <div class="chat-message {role}">
        <div class="message">
            {content}
        </div>
    </div>
    """
    with st.container():
        st.markdown(message_html, unsafe_allow_html=True)

def display_chat_messages():
    messages = load_all_chat_messages(st.session_state["current_chat_id"])
    if messages:
        for message in messages:
            display_chat_message(message.role, message.content)

def handle_user_input():
    if prompt := st.chat_input(placeholder="Type a message..."):
        if st.session_state.get("current_chat_id", None) is None:
            st.session_state["current_chat_id"] = create_new_chat_history(title=prompt)
        save_chat_message(st.session_state["current_chat_id"], role="user", content=prompt)
        display_chat_message("user", prompt)
        return prompt
    return None

def generate_and_display_response(prompt):
    last_message = get_last_chat_message(st.session_state["current_chat_id"])
    if last_message and last_message.role == "user":
        with st.spinner("Generating response..."):
            try:
                response = generate_response(
                    st.session_state["model_option"],
                    prompt,
                    st.session_state["temperature"],
                    st.session_state["max_tokens"],
                )
                full_response = "".join(response)
                save_chat_message(st.session_state["current_chat_id"], "bot", full_response)
                display_chat_message("bot", full_response)
            except Exception as e:
                st.error(f"Error generating response: {e}")

def main():
    st.title("🔥 Chat Interface")
    load_css()
    display_sidebar()
    display_chat_messages()
    prompt = handle_user_input()
    if prompt:
        generate_and_display_response(prompt)

if __name__ == "__main__":
    main()