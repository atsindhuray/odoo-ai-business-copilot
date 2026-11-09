from odoo import fields, models


class AICopilotSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ai_provider = fields.Selection(
        [("openai", "OpenAI"), ("gemini", "Gemini")],
        string="AI Provider",
        default="openai",
    )
    ai_api_key = fields.Char(string="API Key", password=True)
    ai_model_name = fields.Char(string="Model Name", default="gpt-4o-mini")
    ai_enable_copilot = fields.Boolean(string="Enable AI Copilot")

    def get_values(self):
        values = super().get_values()
        params = self.env["ir.config_parameter"].sudo()
        values.update(
            ai_provider=params.get_str("ai_business_copilot.provider", "openai"),
            ai_api_key=params.get_str("ai_business_copilot.api_key", ""),
            ai_model_name=params.get_str("ai_business_copilot.model_name", "gpt-4o-mini"),
            ai_enable_copilot=params.get_bool("ai_business_copilot.enabled", False),
        )
        return values

    def set_values(self):
        result = super().set_values()
        params = self.env["ir.config_parameter"].sudo()
        params.set_str("ai_business_copilot.provider", self.ai_provider or "openai")
        params.set_str("ai_business_copilot.api_key", self.ai_api_key or "")
        params.set_str("ai_business_copilot.model_name", self.ai_model_name or "gpt-4o-mini")
        params.set_bool("ai_business_copilot.enabled", self.ai_enable_copilot)
        return result
