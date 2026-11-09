from odoo import fields, models


class AIBusinessCopilotLog(models.Model):
    _name = "ai.business.copilot.log"
    _description = "AI Business Copilot Request Log"
    _order = "created_on desc"

    lead_id = fields.Many2one("crm.lead", required=True, ondelete="cascade")
    requested_by = fields.Many2one(
        "res.users", required=True, readonly=True, default=lambda self: self.env.user
    )
    request_type = fields.Selection(
        [("summary", "Summary"), ("email", "Email"), ("activity", "Activity")],
        required=True,
        readonly=True,
    )
    input_preview = fields.Text(readonly=True)
    response_text = fields.Text(readonly=True)
    status = fields.Selection(
        [("success", "Success"), ("failed", "Failed")], required=True, readonly=True
    )
    error_message = fields.Text(readonly=True)
    created_on = fields.Datetime(readonly=True, default=fields.Datetime.now)
    token_count = fields.Integer(readonly=True)
    estimated_cost = fields.Float(readonly=True)
