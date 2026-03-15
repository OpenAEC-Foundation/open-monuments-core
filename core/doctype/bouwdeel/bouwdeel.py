# Copyright (c) 2026, OpenAEC Foundation and contributors
# License: LGPL-3.0

from __future__ import annotations

import re

import frappe
from frappe.model.document import Document


class Bouwdeel(Document):
    """
    Bouwdeel — een onderdeel van een monument dat afzonderlijk wordt geïnspecteerd.

    Elk bouwdeel krijgt een NL-SfB code voor standaardisatie. Bouwdelen zijn
    gekoppeld aan één monument en kunnen meerdere elementen bevatten.

    Voorbeelden: Hoofddak, Noordgevel, Fundamenten, Dakgoten.
    """

    def validate(self) -> None:
        """Valideer het Bouwdeel-document vóór opslaan."""
        self._validate_bouwdeel_naam()
        self._validate_monument()
        self._validate_nlsfb_code()
        self._validate_oppervlak()
        self._validate_volgorde()

    def before_save(self) -> None:
        """Stel standaardvolgorde in als deze niet ingevuld is."""
        self._set_volgorde_default()

    def _validate_bouwdeel_naam(self) -> None:
        """Bouwdeelnaam is verplicht en moet minimaal 2 tekens bevatten."""
        if not self.bouwdeel_naam or len(self.bouwdeel_naam.strip()) < 2:
            frappe.throw(
                frappe._("Bouwdeelnaam is verplicht en moet minimaal 2 tekens bevatten."),
                title=frappe._("Validatiefout"),
            )

    def _validate_monument(self) -> None:
        """Controleer of het gekoppelde monument bestaat."""
        if not self.monument:
            frappe.throw(
                frappe._("Koppeling aan een monument is verplicht."),
                title=frappe._("Validatiefout"),
            )
        if not frappe.db.exists("Monument", self.monument):
            frappe.throw(
                frappe._("Monument '{0}' bestaat niet.").format(self.monument),
                title=frappe._("Validatiefout"),
            )

    def _validate_nlsfb_code(self) -> None:
        """
        NL-SfB code: max 5 tekens, combinatie van cijfers en letters.
        Voorbeelden: 23, 27, 43, 45.1, B
        """
        if self.nlsfb_code:
            if not re.match(r"^[A-Za-z0-9./]{1,10}$", self.nlsfb_code.strip()):
                frappe.throw(
                    frappe._("NL-SfB code '{0}' heeft een ongeldig formaat.").format(
                        self.nlsfb_code
                    ),
                    title=frappe._("Validatiefout"),
                )

    def _validate_oppervlak(self) -> None:
        """Oppervlak moet positief zijn als het ingevuld is."""
        if self.oppervlak_m2 is not None and self.oppervlak_m2 < 0:
            frappe.throw(
                frappe._("Oppervlak kan niet negatief zijn."),
                title=frappe._("Validatiefout"),
            )

    def _validate_volgorde(self) -> None:
        """Volgorde moet een positief getal zijn."""
        if self.volgorde is not None and self.volgorde < 0:
            frappe.throw(
                frappe._("Volgorde moet een positief getal zijn."),
                title=frappe._("Validatiefout"),
            )

    def _set_volgorde_default(self) -> None:
        """
        Stel de volgorde automatisch in op het hoogste bestaande volgordenummer + 10
        als de volgorde nog niet is ingevuld.
        """
        if not self.volgorde:
            max_volgorde = frappe.db.get_value(
                "Bouwdeel",
                filters={"monument": self.monument},
                fieldname="max(volgorde)",
            )
            self.volgorde = (int(max_volgorde) + 10) if max_volgorde else 10

    def get_elementen(self) -> list[dict]:
        """Geef alle elementen van dit bouwdeel terug."""
        return frappe.get_all(
            "Element",
            filters={"bouwdeel": self.name},
            fields=["name", "element_naam", "beschrijving", "materiaal_detail"],
        )
