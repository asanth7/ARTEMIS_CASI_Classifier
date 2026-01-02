import asyncio
import json
import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, List
import os, signal
import uuid

from openai import AsyncOpenAI

#   BASE_URL = "http://98.91.36.205"
#   VARIANT = "v2"  # "", "v1", or "v2"
#   USER_ID = "mcnairshah"
#   OPENROUTER_KEY = "sk-or-..."  # your real OpenRouter key

#   session_id = str(uuid.uuid4())
#   url = f"{BASE_URL}/{VARIANT}/openrouter/v1/chat/completions" if VARIANT else f"{BASE_URL}/
#   openrouter/v1/chat/completions"

#   headers = {
#       "Authorization": f"Bearer rt_{USER_ID}_{OPENROUTER_KEY}",
#       "Content-Type": "application/json",
#       "X-RedTeam-Session-ID": session_id,
#   }

#   payload = {
#       "model": "openai/gpt-4o-mini",  # any OpenRouter model slug
#       "messages": [{"role": "user", "content": "Hello! What can you do?"}],
#   }

#   resp = requests.post(url, headers=headers, json=payload, timeout=30)
#   resp.raise_for_status()
#   print(resp.json()["choices"][0]["message"]["content"])

# BASE URLS:
# Proxy + "/openai/v1" for OpenAI models
# Proxy + "/openrouter/v1/" for OpenRouter models
# Proxy + "/anthropic" for Anthropic models

class ClientGenerator:
    """Centralized client generator for all agents to support the defense classifier proxy."""
    def __init__(self, base_url, api_key, proxy: Optional[str] = "v0", user_id: Optional[str] = None):
        self.proxy = proxy
        self.base_url = base_url
        self.api_key = f"rt_{user_id}_{api_key}" if user_id is not None else api_key  # Format API key as expected for proxy if provided (user id only provided when the proxy is being used)
        self.logger = logging.getLogger(__name__)
    
    def create_client(self, session_id: str) -> AsyncOpenAI:
        """Create and return an AsyncOpenAI client instance with a given session ID. Thread safe and supports multiple concurrent clients."""
        
        self.base_url = f"http://98.91.36.205/{self.proxy}" if self.proxy is not None else self.base_url  # Route to proxy and use provided endpoint otherwise (NOTE: users must specify proxy as None to avoid proxy --> default is LlamaGuard)
        if "openrouter" in self.base_url:
            self.base_url = f"{self.base_url}/openrouter/v1"  # Adjust base_url for OpenRouter models if detected in the URL
        elif "openai" in self.base_url:
            self.base_url = f"{self.base_url}/openai/v1"  # Adjust base_url for OpenAI models if detected in the URL

        return AsyncOpenAI(base_url=self.base_url, api_key=self.api_key, default_headers={"X-RedTeam-Session-ID": session_id})  # Pass provided base_url and api_key to AsyncOpenAI instance
