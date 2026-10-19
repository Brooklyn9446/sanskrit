"""LLM Client Wrapper providing a unified interface across multiple providers.

Supports:
- Gemini (via google-genai)
- OpenAI / Groq / OpenAI-compatible (via openai library)
- Anthropic (via HTTP / client)

API keys and provider choices are read strictly from environment variables (.env).
"""

from __future__ import annotations

import os
from typing import Generator, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class LLMClientError(Exception):
    """Custom exception for LLM provider errors."""
    pass


class LLMClient:
    """Unified wrapper around swappable LLM providers."""

    def __init__(
        self,
        provider: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
    ):
        """Initialize the client by reading configuration from environment or parameters.

        Args:
            provider: LLM provider ('gemini', 'openai', 'groq'). Defaults to LLM_PROVIDER in .env.
            model: Model name. Defaults to LLM_MODEL in .env.
            api_key: Explicit API key if not reading from env.
        """
        self.provider = (provider or os.getenv("LLM_PROVIDER", "gemini")).lower().strip()
        self.api_key = api_key or self._resolve_api_key()
        self.model = model or os.getenv("LLM_MODEL") or self._default_model_for_provider()

        self._client: Any = None
        self._init_provider_client()

    def _resolve_api_key(self) -> str | None:
        """Resolve API key based on the selected provider."""
        if self.provider == "gemini":
            return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        elif self.provider == "openai":
            return os.getenv("OPENAI_API_KEY")
        elif self.provider == "groq":
            return os.getenv("GROQ_API_KEY")
        elif self.provider == "anthropic":
            return os.getenv("ANTHROPIC_API_KEY")
        return os.getenv("LLM_API_KEY")

    def _default_model_for_provider(self) -> str:
        """Return sensible default model for each supported provider."""
        defaults = {
            "gemini": "gemini-2.5-flash",
            "openai": "gpt-4o-mini",
            "groq": "llama-3.3-70b-versatile",
            "anthropic": "claude-3-5-haiku-20241022",
        }
        return defaults.get(self.provider, "gemini-2.5-flash")

    def _init_provider_client(self) -> None:
        """Initialize the underlying provider client if credentials are present."""
        if not self.api_key:
            return

        if self.provider == "gemini":
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                # Fallback to direct REST or handle error
                self._client = None
        elif self.provider in ("openai", "groq"):
            try:
                from openai import OpenAI
                base_url = "https://api.groq.com/openai/v1" if self.provider == "groq" else None
                self._client = OpenAI(api_key=self.api_key, base_url=base_url)
            except Exception as e:
                self._client = None

    def is_configured(self) -> bool:
        """Check whether the client has valid credentials configured."""
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    def generate_response(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
        stream: bool = False,
    ) -> str | Generator[str, None, None]:
        """Generate response from the selected LLM.

        Args:
            messages: List of chat message dicts with 'role' ('user'/'assistant') and 'content'.
            system_prompt: Optional system prompt to enforce behavior.
            stream: Whether to stream tokens.

        Returns:
            String response if stream=False, or a token generator if stream=True.
        """
        if not self.is_configured():
            msg = (
                f"⚠️ **LLM Not Configured**: No API key found for provider `{self.provider}`.\n\n"
                f"Please add `{self._key_var_name()}` to your `.env` file or export it as an "
                f"environment variable."
            )
            if stream:
                def _gen():
                    yield msg
                return _gen()
            return msg

        try:
            if self.provider == "gemini":
                return self._call_gemini(messages, system_prompt, stream=stream)
            elif self.provider in ("openai", "groq"):
                return self._call_openai(messages, system_prompt, stream=stream)
            else:
                raise LLMClientError(f"Unsupported provider: '{self.provider}'")
        except Exception as e:
            err_msg = f"❌ **LLM Error ({self.provider})**: {str(e)}"
            if stream:
                def _err_gen():
                    yield err_msg
                return _err_gen()
            return err_msg

    def _key_var_name(self) -> str:
        """Helper to get key variable name for instructions."""
        names = {
            "gemini": "GEMINI_API_KEY",
            "openai": "OPENAI_API_KEY",
            "groq": "GROQ_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
        }
        return names.get(self.provider, "LLM_API_KEY")

    def _call_gemini(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None,
        stream: bool,
    ) -> str | Generator[str, None, None]:
        """Handle Gemini generation via google-genai SDK."""
        from google.genai import types

        # Build contents from message history
        contents = []
        for m in messages:
            role = "user" if m.get("role") == "user" else "model"
            contents.append(types.Content(role=role, parts=[types.Part.from_text(text=m.get("content", ""))]))

        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.3,
        )

        if stream:
            def _stream_gen():
                response_stream = self._client.models.generate_content_stream(
                    model=self.model,
                    contents=contents,
                    config=config,
                )
                for chunk in response_stream:
                    if chunk.text:
                        yield chunk.text
            return _stream_gen()
        else:
            resp = self._client.models.generate_content(
                model=self.model,
                contents=contents,
                config=config,
            )
            return resp.text or ""

    def _call_openai(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None,
        stream: bool,
    ) -> str | Generator[str, None, None]:
        """Handle OpenAI or Groq generation."""
        chat_msgs: list[dict[str, str]] = []
        if system_prompt:
            chat_msgs.append({"role": "system", "content": system_prompt})

        for m in messages:
            chat_msgs.append({"role": m.get("role", "user"), "content": m.get("content", "")})

        if stream:
            def _stream_gen():
                response = self._client.chat.completions.create(
                    model=self.model,
                    messages=chat_msgs,
                    temperature=0.3,
                    stream=True,
                )
                for chunk in response:
                    content = chunk.choices[0].delta.content if chunk.choices else None
                    if content:
                        yield content
            return _stream_gen()
        else:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=chat_msgs,
                temperature=0.3,
                stream=False,
            )
            return response.choices[0].message.content or ""
