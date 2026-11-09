import json
import logging
import requests
from odoo import _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AIService:
    TIMEOUT = 30

    def __init__(self, env):
        self.env = env
        params = env["ir.config_parameter"].sudo()
        self.provider = params.get_str("ai_business_copilot.provider", "openai")
        self.api_key = params.get_str("ai_business_copilot.api_key", "")
        self.model = params.get_str("ai_business_copilot.model_name", "gpt-4o-mini")
        self.enabled = params.get_bool("ai_business_copilot.enabled", False)

    def request_json(self, prompt):
        if not self.enabled:
            raise UserError(_("AI Business Copilot is disabled in Settings."))
        if not self.api_key:
            raise UserError(_("AI API key is missing. Configure it in Settings."))
        if self.provider == "gemini":
            response = self._request_gemini(prompt)
        else:
            response = self._request_openai(prompt)
        try:
            return json.loads(response)
        except (TypeError, json.JSONDecodeError) as error:
            raise UserError(_("The AI provider returned invalid JSON.")) from error

    def _request_openai(self, prompt):
        url = "https://api.openai.com/v1/chat/completions"
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
        }
        try:
            response = requests.post(
                url, json=payload, headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=self.TIMEOUT,
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except (requests.RequestException, KeyError, TypeError, ValueError) as error:
            _logger.warning("AI provider request failed: %s", type(error).__name__)
            raise UserError(_("The AI provider request failed. Check configuration and try again.")) from error

    def _request_gemini(self, prompt):
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        try:
            response = requests.post(url, json=payload, timeout=self.TIMEOUT)
            response.raise_for_status()
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except (requests.RequestException, KeyError, TypeError, ValueError) as error:
            _logger.warning("AI provider request failed: %s", type(error).__name__)
            raise UserError(_("The AI provider request failed. Check configuration and try again.")) from error
