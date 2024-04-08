#  Copyright 2024 Simone Rubino - Aion Tech
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    _partner_name_history_field_map = {
        "partner_id": "name_history_invoice_date",
    }

    name_history_invoice_date = fields.Date(related="move_id.invoice_date")
