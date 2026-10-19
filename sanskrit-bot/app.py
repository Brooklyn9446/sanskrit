"""Sanskrit Learning & Bhagavad Gita Q&A Bot - Streamlit UI (Stage 1)."""

import os
import streamlit as st
from dotenv import load_dotenv

from src.llm_client import LLMClient
from src.prompts import SYSTEM_PROMPT, DEFAULT_WELCOME_MESSAGE

# Reload environment
load_dotenv(override=True)

# Page configuration
st.set_page_config(
    page_title="Sanskrit & Gita AI Assistant",
    page_icon="🕉️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling for Sanskrit Typography & Card Aesthetics
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&family=Noto+Sans+Devanagari:wght@400;600;700&family=Plus+Jakarta+Sans:wght@400;500;600&display=swap');

    .main-header {
        font-family: 'Cinzel', serif;
        font-weight: 700;
        font-size: 2.2rem;
        color: #d97706; /* Saffron gold */
        margin-bottom: 0.1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .sub-header {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.95rem;
        color: #6b7280;
        margin-bottom: 1.5rem;
    }
    .sanskrit-devanagari {
        font-family: 'Noto Sans Devanagari', sans-serif;
        font-size: 1.25rem;
        font-weight: 600;
        color: #92400e;
        background: #fef3c7;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        display: inline-block;
    }
    .sample-pill {
        cursor: pointer;
        padding: 0.4rem 0.8rem;
        background: #f3f4f6;
        border: 1px solid #e5e7eb;
        border-radius: 20px;
        font-size: 0.85rem;
        margin-bottom: 0.4rem;
        display: inline-block;
        transition: all 0.2s;
    }
    .sample-pill:hover {
        background: #fde68a;
        border-color: #d97706;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_llm_client() -> LLMClient:
    """Retrieve or initialize LLM Client in session state."""
    provider = st.session_state.get("selected_provider", os.getenv("LLM_PROVIDER", "gemini"))
    model = st.session_state.get("selected_model", os.getenv("LLM_MODEL"))
    api_key = st.session_state.get("custom_api_key") or None

    return LLMClient(provider=provider, model=model, api_key=api_key)


# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": DEFAULT_WELCOME_MESSAGE}
    ]

# Sidebar configuration
with st.sidebar:
    st.markdown("### ⚙️ Engine Settings")

    providers = ["gemini", "openai", "groq"]
    default_provider = os.getenv("LLM_PROVIDER", "gemini").lower()
    default_idx = providers.index(default_provider) if default_provider in providers else 0

    selected_provider = st.selectbox(
        "LLM Provider",
        options=providers,
        index=default_idx,
        help="Select the model provider to use.",
        key="selected_provider",
    )

    client = get_llm_client()
    default_model = client.model

    model_name = st.text_input(
        "Model Name",
        value=default_model,
        help="Model ID to pass to the API.",
        key="selected_model",
    )

    # API key input (optional manual override)
    key_var_name = client._key_var_name()
    has_env_key = bool(client.api_key and not st.session_state.get("custom_api_key"))

    st.markdown(
        f"**API Key Status**: "
        + ("🟢 Configured (`.env`)" if has_env_key else "🟡 Key needed"),
    )

    custom_key = st.text_input(
        f"Override {key_var_name} (optional)",
        type="password",
        help="Provide a key here if you haven't set it in your .env file.",
        key="custom_api_key",
    )

    st.divider()

    st.markdown("### 💡 Quick Sanskrit Inquiries")
    quick_prompts = [
        "Explain 'कर्मण्येवाधिकारस्ते मा फलेषु कदाचन' (BG 2.47)",
        "What does 'स्थितप्रज्ञ' (Sthitaprajña) mean?",
        "Explain the 7 Sanskrit noun cases (विभक्ति / Vibhakti)",
        "Break down the word 'धृतराष्ट्र' (Dhṛtarāṣṭra)",
    ]

    for p in quick_prompts:
        if st.button(p, use_container_width=True):
            st.session_state.pending_user_input = p

    st.divider()

    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": DEFAULT_WELCOME_MESSAGE}
        ]
        st.rerun()

    st.markdown(
        """
        ---
        **Rules Enforced**:
        - ✅ Devanagari text
        - ✅ IAST transliteration
        - ✅ English translation & breakdown
        - 🚫 Zero verse fabrication
        """
    )

# Main UI layout
st.markdown('<div class="main-header">🕉️ संस्कृत & गीता AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Authentic Sanskrit learning and Bhagavad Gita Q&A powered by verified source retrieval.</div>',
    unsafe_allow_html=True,
)

# Render Chat History
for message in st.session_state.messages:
    role = message["role"]
    avatar = "🪷" if role == "assistant" else "👤"
    with st.chat_message(role, avatar=avatar):
        st.markdown(message["content"])

# Check for pending prompt from quick buttons
user_input = None
if st.session_state.get("pending_user_input"):
    user_input = st.session_state.pop("pending_user_input")

# Chat input prompt
chat_input = st.chat_input("Ask a question in English, Devanagari, or IAST...")
if chat_input:
    user_input = chat_input

if user_input:
    # Append and render user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    # Generate assistant response
    with st.chat_message("assistant", avatar="🪷"):
        active_client = get_llm_client()

        if not active_client.is_configured():
            err_msg = (
                f"⚠️ **API Key Missing**: Please set `{active_client._key_var_name()}` in your "
                f"`.env` file or enter it in the sidebar to activate responses."
            )
            st.warning(err_msg)
            st.session_state.messages.append({"role": "assistant", "content": err_msg})
        else:
            try:
                # Prepare message history excluding the initial welcome greeting
                chat_payload = [
                    m for m in st.session_state.messages[1:]
                    if m.get("content") != DEFAULT_WELCOME_MESSAGE
                ]

                # Stream response
                response_stream = active_client.generate_response(
                    messages=chat_payload,
                    system_prompt=SYSTEM_PROMPT,
                    stream=True,
                )
                full_reply = st.write_stream(response_stream)
                st.session_state.messages.append({"role": "assistant", "content": full_reply})
            except Exception as e:
                err_text = f"❌ **Error generating response**: {str(e)}"
                st.error(err_text)
                st.session_state.messages.append({"role": "assistant", "content": err_text})
