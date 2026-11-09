from odoo import fields, models


class AICopilotActivityWizard(models.TransientModel):
    _name = "ai.business.copilot.activity.wizard"
    _description = "Confirm AI Suggested Activity"

    lead_id = fields.Many2one("crm.lead", required=True)
    subject = fields.Char(required=True)
    note = fields.Html()
    user_id = fields.Many2one("res.users", required=True, default=lambda self: self.env.user)
    date_deadline = fields.Date(required=True, default=lambda self: fields.Date.add(fields.Date.today(), days=1))

    def action_confirm(self):
        self.ensure_one()
        self.env["mail.activity"].create({
            "res_model_id": self.env["ir.model"]._get_id("crm.lead"),
            "res_id": self.lead_id.id,
            "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
            "summary": self.subject,
            "note": self.note,
            "user_id": self.user_id.id,
            "date_deadline": self.date_deadline,
        })
        return {"type": "ir.actions.act_window_close"}
