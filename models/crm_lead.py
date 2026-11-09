import json

from odoo import _, fields, models
from odoo.exceptions import UserError

from ..services.ai_service import AIService


class CrmLead(models.Model):
    _inherit = "crm.lead"

    ai_summary = fields.Text(string="AI Summary")
    ai_customer_need = fields.Text(string="Customer Need")
    ai_suggested_priority = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        string="Suggested Priority",
    )
    ai_suggested_next_action = fields.Text(string="Suggested Next Action")
    ai_followup_email_draft = fields.Html(string="Follow-up Email Draft")
    ai_status = fields.Selection(
        [("draft", "Draft"), ("approved", "Approved"), ("failed", "Failed")],
        string="AI Status",
        default="draft",
    )
    ai_last_generated_on = fields.Datetime(string="Last AI Generated On", readonly=True)

    def _get_recent_ai_messages(self):
        self.ensure_one()
        messages = self.env["mail.message"].search(
            [("res_id", "=", self.id), ("model", "=", self._name), ("message_type", "!=", "notification")],
            order="date desc",
            limit=10,
        )
        return "\n".join(
            f"{message.author_id.name or 'System'}: {message.body or ''}" for message in messages
        )[:8000]

    def _prepare_ai_context(self):
        self.ensure_one()
        return {
            "lead_name": self.name or "",
            "customer_name": self.partner_name or "",
            "email": self.email_from or "",
            "phone": self.phone or "",
            "description": self.description or "",
            "recent_chatter": self._get_recent_ai_messages(),
        }

    def _ai_prompt(self, context, request_type):
        context_json = json.dumps(context, ensure_ascii=False)
        if request_type == "summary":
            return (
                "Analyze this CRM lead. Return JSON only with exactly these keys: "
                "summary, customer_need, priority, next_action. Priority must be low, medium, or high.\n"
                f"Lead context:\n{context_json}"
            )
        return (
            "Write a short, polite, professional follow-up email for this CRM lead. "
            "Return JSON only with exactly one key: email. Do not send the email.\n"
            f"Lead context:\n{context_json}"
        )

    def _create_ai_log(self, request_type, context, response_text, status, error_message=None):
        self.ensure_one()
        return self.env["ai.business.copilot.log"].create({
            "lead_id": self.id,
            "request_type": request_type,
            "input_preview": json.dumps(context, ensure_ascii=False)[:4000],
            "response_text": (response_text or "")[:10000],
            "status": status,
            "error_message": error_message or False,
        })

    def action_generate_ai_summary(self):
        for lead in self:
            context = lead._prepare_ai_context()
            try:
                result = AIService(self.env).request_json(lead._ai_prompt(context, "summary"))
                priority = result.get("priority")
                if priority not in {"low", "medium", "high"}:
                    raise UserError(_("AI returned an invalid priority."))
                lead.write({
                    "ai_summary": result.get("summary", ""),
                    "ai_customer_need": result.get("customer_need", ""),
                    "ai_suggested_priority": priority,
                    "ai_suggested_next_action": result.get("next_action", ""),
                    "ai_status": "draft",
                    "ai_last_generated_on": fields.Datetime.now(),
                })
                lead._create_ai_log("summary", context, json.dumps(result), "success")
            except Exception as error:
                lead.write({"ai_status": "failed"})
                lead._create_ai_log("summary", context, "", "failed", str(error)[:2000])
                raise
        return True

    def action_generate_followup_email(self):
        for lead in self:
            context = lead._prepare_ai_context()
            context["generated_summary"] = lead.ai_summary or ""
            try:
                result = AIService(self.env).request_json(lead._ai_prompt(context, "email"))
                email = result.get("email")
                if not email:
                    raise UserError(_("AI returned an empty email draft."))
                lead.write({
                    "ai_followup_email_draft": email,
                    "ai_status": "draft",
                    "ai_last_generated_on": fields.Datetime.now(),
                })
                lead._create_ai_log("email", context, json.dumps(result), "success")
            except Exception as error:
                lead.write({"ai_status": "failed"})
                lead._create_ai_log("email", context, "", "failed", str(error)[:2000])
                raise
        return True

    def action_create_suggested_activity(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Confirm Suggested Activity"),
            "res_model": "ai.business.copilot.activity.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_lead_id": self.id,
                "default_subject": self.ai_suggested_next_action or _("Follow up with lead"),
                "default_note": self.ai_summary or "",
                "default_user_id": self.env.uid,
                "default_date_deadline": fields.Date.add(fields.Date.today(), days=1),
            },
        }
