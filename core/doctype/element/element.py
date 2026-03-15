# Copyright (c) 2026, OpenAEC Foundation and contributors
# License: LGPL-3.0

from __future__ import annotations

import frappe
from frappe.model.document import Document


class Element(Document):
    """
    Element — een specifiek onderdeel binnen een bouwdeel.

    Elementen zijn het meest gedetailleerde niveau in de objecthiërarchie:
    Monument → Bouwdeel → Element.

    Voorbeelden: Dakpannen (onder Dak), Topgevelmetselwerk (onder Gevel Noord),
    Voordeur (onder Kozijnen en deuren).
    """

    def validate(self) -> None:
        """Valideer het Element-document vóór opslaan."""
        self._validate_element_naam()
        self._validate_bouwdeel()

    def _validate_element_naam(self) -> None:
        """Elementnaam is verplicht en moet minimaal 2 tekens bevatten."""
        if not self.element_naam or len(self.element_naam.strip()) < 2:
            frappe.throw(
                frappe._("Elementnaam is verplicht en moet minimaal 2 tekens bevatten."),
                title=frappe._("Validatiefout"),
            )

    def _validate_bouwdeel(self) -> None:
        """Controleer of het gekoppelde bouwdeel bestaat."""
        if not self.bouwdeel:
            frappe.throw(
                frappe._("Koppeling aan een bouwdeel is verplicht."),
                title=frappe._("Validatiefout"),
            )
        if not frappe.db.exists("Bouwdeel", self.bouwdeel):
            frappe.throw(
                frappe._("Bouwdeel '{0}' bestaat niet.").format(self.bouwdeel),
                title=frappe._("Validatiefout"),
            )

    def get_monument(self) -> str | None:
        """Geef het monumentnummer terug via het gekoppelde bouwdeel."""
        if self.bouwdeel:
            return frappe.db.get_value("Bouwdeel", self.bouwdeel, "monument")
        return None
