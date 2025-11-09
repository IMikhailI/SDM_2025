from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Type, Optional
import os, uuid, requests


class BaseAIProvider(ABC):
    TIMEOUT = 20
    @abstractmethod
    def ask(self, context: str, question: str, system_text: str) -> str: ...


# Google Gemini
class GoogleGeminiProvider(BaseAIProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY", "")
        self.model   = model   or os.getenv("GOOGLE_MODEL", "gemini-2.5-flash")
        self.url     = f"https://generativelanguage.googleapis.com/v1/models/{self.model}:generateContent"

    def ask(self, context: str, question: str, system_text: str) -> str:
        if not self.api_key:
            return ""
        payload = {
            "contents": [{
                "role": "user",
                "parts": [{"text": f"{system_text}\n\nКОНТЕКСТ:\n{context}\n\nВОПРОС:\n{question}"}]
            }],
            "generation_config": {"temperature": 0.2, "maxOutputTokens": 256}
        }
        try:
            r = requests.post(self.url, params={"key": self.api_key}, json=payload, timeout=self.TIMEOUT)
            if r.status_code != 200:
                return ""
            data = r.json()
        except Exception:
            return ""

        for cand in (data.get("candidates") or []):
            content = cand.get("content") or {}
            for part in (content.get("parts") or []):
                t = part.get("text")
                if t:
                    return t.strip()
        return ""


# Sber GigaChat
class GigaChatProvider(BaseAIProvider):
    AUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    API_URL  = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    MODEL    = "GigaChat"

    def _token(self) -> str:
        basic = (os.getenv("SBER_BASIC_AUTH") or "").strip()
        if basic.lower().startswith("basic "):
            basic = basic.split(" ", 1)[1].strip()
        if not basic:
            return ""
        headers = {
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "RqUID": str(uuid.uuid4()),
        }
        try:
            r = requests.post(self.AUTH_URL, headers=headers, data={"scope": "GIGACHAT_API_PERS"},
                              timeout=20, verify=False)
            if r.status_code != 200:
                return ""
            return r.json().get("access_token") or ""
        except Exception:
            return ""

    @staticmethod
    def _text(content) -> str:
        if isinstance(content, str):
            return content.strip()
        if isinstance(content, list):
            parts = []
            for p in content:
                if isinstance(p, dict) and p.get("type") in ("text", "output_text"):
                    t = (p.get("text") or "").strip()
                    if t:
                        parts.append(t)
            return " ".join(parts) if parts else ""
        return ""

    def ask(self, context: str, question: str, system_text: str) -> str:
        import requests
        tok = self._token()
        if not tok:
            return ""
        payload = {
            "model": self.MODEL,
            "messages": [
                {"role": "system", "content": system_text},
                {"role": "user",   "content": f"КОНТЕКСТ:\n{context}\n\nВОПРОС:\n{question}"},
            ],
            "temperature": 0.2,
            "max_tokens": 256,
        }
        try:
            r = requests.post(self.API_URL,
                              headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"},
                              json=payload, timeout=20, verify=False)
            if r.status_code != 200:
                return ""
            data = r.json()
            return self._text(data["choices"][0]["message"]["content"])
        except Exception:
            return ""


# Registry
class ProviderRegistry:
    _providers: Dict[str, Type[BaseAIProvider]] = {
        "google":   GoogleGeminiProvider,
        "gigachat": GigaChatProvider,
    }

    @classmethod
    def create(cls, name: str) -> BaseAIProvider:
        name = (name or "").lower()
        return (cls._providers.get(name) or GigaChatProvider)()

def provider_chain(env_value: str | None, override: str | None = None) -> list[str]:
    base = [p.strip().lower() for p in (env_value or "").split(",") if p.strip()]
    ov = (override or "").strip().lower()
    return [ov] + [p for p in base if p != ov] if ov else base

def ask_ai(
    *,
    prompt: str,
    providers: list[str] | None = None,
    system_text: str = "Ты — помощник. Отвечай чётко и по делу.",
    context: str = "",
) -> str:
    chain = providers or provider_chain(os.getenv("DEFAULT_PROVIDERS"))
    question = prompt

    for name in chain:
        try:
            provider = ProviderRegistry.create(name)
            text = provider.ask(context=context, question=question, system_text=system_text) or ""
            if text.strip():
                return text.strip()
        except Exception:
            continue
    return ""
