"""Tests for Stage 1: LLM client abstraction and system prompts."""

import os
import pytest
from src.llm_client import LLMClient
from src.prompts import SYSTEM_PROMPT, DEFAULT_WELCOME_MESSAGE


def test_system_prompt_rules():
    """Verify that system prompt explicitly mandates Devanagari, IAST, and English."""
    assert "Devanagari" in SYSTEM_PROMPT
    assert "IAST" in SYSTEM_PROMPT
    assert "English" in SYSTEM_PROMPT
    assert "NEVER FABRICATE" in SYSTEM_PROMPT


def test_llm_client_initialization():
    """Test client initializes with default or specified providers."""
    # Gemini
    client_gemini = LLMClient(provider="gemini")
    assert client_gemini.provider == "gemini"
    assert "gemini" in client_gemini.model

    # OpenAI
    client_openai = LLMClient(provider="openai")
    assert client_openai.provider == "openai"
    assert "gpt" in client_openai.model

    # Groq
    client_groq = LLMClient(provider="groq")
    assert client_groq.provider == "groq"
    assert "llama" in client_groq.model


def test_llm_client_unconfigured_graceful_handling():
    """Test client returns informative warning when API key is not present."""
    client = LLMClient(provider="gemini", api_key="")
    assert not client.is_configured()

    response = client.generate_response(
        messages=[{"role": "user", "content": "Tell me about Sanskrit"}],
        system_prompt=SYSTEM_PROMPT,
        stream=False,
    )
    assert isinstance(response, str)
    assert "API key" in response or "Not Configured" in response
