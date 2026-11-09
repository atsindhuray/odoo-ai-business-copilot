# AI Business Copilot

AI-assisted CRM lead summaries and follow-up drafts for Odoo 20 Community.

## Installation

1. Add this `addons` directory to the Odoo addons path.
2. Restart Odoo and update the Apps list.
3. Install **AI Business Copilot**.

## Configuration

Open Settings as a System Administrator, configure the provider, model and API key, then enable the copilot.

## Usage

Open a CRM lead and use the AI Copilot tab or the header buttons. AI results are drafts and do not automatically modify the lead priority, stage, send email, or create activities. Activities require confirmation.

## Manual tests

- Configure each provider and verify the settings persist.
- Attempt an AI action with the copilot disabled or without an API key; a clear error must be shown.
- Generate a summary and verify all four structured fields are populated while CRM priority and stage remain unchanged.
- Generate an email and verify it is saved only as a draft.
- Create a suggested activity and verify no activity exists before confirmation and exactly one exists after confirmation.
- Verify CRM users cannot open AI logs and System Administrators can manage settings and logs.
