# Copyright (c) 2026, OpenAEC Foundation and contributors
# License: LGPL-3.0

from __future__ import annotations

import re

import frappe
from frappe.model.document import Document


class Eigenaar(Document):
    """
    Eigenaar van een monument. Kan een particulier, organisatie, kerkgenootschap
    of overheidsinstantie zijn.

    Gekoppeld aan Abonnement en Monument om de eigendomsrelatie vast te leggen.
    """

    def validate(self) -> None:
        """Valideer de eigenaar-gegevens vóór opslaan."""
        self._validate_naam()
        self._validate_email()
        self._validate_postcode()
        self._validate_telefoon()

    def _validate_naam(self) -> None:
        """Naam moet minimaal 2 tekens bevatten."""
        if not self.eigenaar_naam or len(self.eigenaar_naam.strip()) < 2:
            frappe.throw(
                frappe._("Naam eigenaar moet minimaal 2 tekens bevatten."),
                title=frappe._("Validatiefout"),
            )

    def _validate_email(self) -> None:
        """Controleer of het e-mailadres een geldig formaat heeft."""
        if self.email:
            email_pattern = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")
            if not email_pattern.match(self.email.strip()):
                frappe.throw(
                    frappe._("Het e-mailadres '{0}' is ongeldig.").format(self.email),
                    title=frappe._("Validatiefout"),
                )

    def _validate_postcode(self) -> None:
        """Nederlandse postcode: 4 cijfers + spatie + 2 letters (bijv. 1234 AB)."""
        if self.postcode:
            postcode_pattern = re.compile(r"^\d{4}\s?[A-Za-z]{2}$")
            if not postcode_pattern.match(self.postcode.strip()):
                frappe.throw(
                    frappe._("Postcode '{0}' is ongeldig. Gebruik het formaat 1234 AB.").format(
                        self.postcode
                    ),
                    title=frappe._("Validatiefout"),
                )

    def _validate_telefoon(self) -> None:
        """Telefoonnummer: alleen cijfers, spaties en +, minimaal 10 tekens."""
        if self.telefoon:
            cleaned = re.sub(r"[\s\-()]", "", self.telefoon)
            if not re.match(r"^\+?[0-9]{9,15}$", cleaned):
                frappe.throw(
                    frappe._("Telefoonnummer '{0}' is ongeldig.").format(self.telefoon),
                    title=frappe._("Validatiefout"),
                )

    def get_monumenten(self) -> list[dict]:
        """Geef alle monumenten terug die aan deze eigenaar zijn gekoppeld."""
        return frappe.get_all(
            "Monument",
            filters={"eigenaar": self.name},
            fields=["name", "monument_naam", "adres", "plaats", "monument_nummer"],
        )

    def get_abonnementen(self) -> list[dict]:
        """Geef alle abonnementen van deze eigenaar terug."""
        return frappe.get_all(
            "Abonnement",
            filters={"eigenaar": self.name},
            fields=["name", "monument", "abonnement_type", "status", "startdatum"],
        )
