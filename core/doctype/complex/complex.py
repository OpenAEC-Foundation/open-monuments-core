# Copyright (c) 2026, OpenAEC Foundation and contributors
# License: LGPL-3.0

from __future__ import annotations

import frappe
from frappe.model.document import Document


class Complex(Document):
    """
    Monumentencomplex — een groep gerelateerde monumenten die gezamenlijk
    een architectonisch of historisch geheel vormen.

    Voorbeelden: een kloostercomplex, een historisch stadsgebied,
    een ensemble van boerderijgebouwen.
    """

    def validate(self) -> None:
        """Valideer het Complex-document vóór opslaan."""
        self._validate_complex_naam()

    def _validate_complex_naam(self) -> None:
        """Complexnaam mag niet leeg zijn en moet uniek zijn."""
        if not self.complex_naam:
            frappe.throw(
                frappe._("Complexnaam is verplicht."),
                title=frappe._("Validatiefout"),
            )
        if len(self.complex_naam.strip()) < 2:
            frappe.throw(
                frappe._("Complexnaam moet minimaal 2 tekens bevatten."),
                title=frappe._("Validatiefout"),
            )

    def get_monumenten(self) -> list[dict]:
        """Geef alle monumenten terug die tot dit complex behoren."""
        return frappe.get_all(
            "Monument",
            filters={"complex": self.name},
            fields=["name", "monument_naam", "adres", "plaats", "status"],
        )
