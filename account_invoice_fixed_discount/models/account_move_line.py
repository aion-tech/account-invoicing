# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_round


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    discount_fixed = fields.Monetary(
        string="Discount (Fixed)",
        default=0.0,
        currency_field="currency_id",
        help=(
            "Apply a fixed amount discount to this line. The amount is multiplied by "
            "the quantity of the product."
        ),
    )

    @api.constrains("discount_fixed", "discount")
    def _check_discounts(self):
        """Check that the fixed discount and the discount percentage are consistent."""
        for line in self:
            if line.discount_fixed and line.discount:
                currency = line.currency_id
                calculated_fixed_discount = float_round(
                    line._get_discount_from_fixed_discount(),
                    precision_rounding=currency.rounding,
                )

                if calculated_fixed_discount != line.discount:
                    raise ValidationError(
                        _(
                            "The fixed discount %(fixed)s does not match the calculated "
                            "discount %(discount)s %%. Please correct one of the discounts."
                        )
                        % {
                            "fixed": line.discount_fixed,
                            "discount": line.discount,
                        }
                    )

    def _get_discount_from_fixed_discount(self):
        """Calculate the discount percentage from the fixed discount amount."""
        self.ensure_one()
        if not self.discount_fixed:
            return 0.0

        return self.discount_fixed / self.price_unit * 100

    @api.onchange("discount_fixed", "quantity", "price_unit")
    def _onchange_discount_fixed(self):
        """When the discount fixed is changed, we set the ``discount`` on the line to the
        appropriate value and apply the default downstream implementation.

        When the display_type is not ``'product'`` we reset the discount_fixed to 0.0.

        """
        if self.display_type != "product" or not self.quantity or not self.price_unit:
            self.discount_fixed = 0.0
            return

        if self.discount_fixed:
            self.discount = self._get_discount_from_fixed_discount()
