# Copyright (c) 2026, OpenAEC Foundation and contributors
# License: LGPL-3.0

from __future__ import annotations

import re

import frappe
from frappe.model.document import Document


class Monument(Document):
    """
    Monument — het centrale object in het Open-Monuments platform.

    Vertegenwoordigt één beschermd bouwwerk of -site in het Nederlandse
    monumentenregister. Bevat basisgegevens, locatiedata, bouwhistorie
    en koppeling aan Eigenaar en Complex.

    Autoname: MON-{YYYY}-{#####} (bijv. MON-2026-00001)
    """

    def validate(self) -> None:
        """Valideer het Monument-document vóór opslaan."""
        self._validate_monument_naam()
        self._validate_monument_nummer()
        self._validate_bouwperiode()
        self._validate_coordinaten()
        self._validate_postcode()

    def before_save(self) -> None:
        """Voer bewerkingen uit vlak vóór opslaan."""
        self._normalize_monument_nummer()

    def _validate_monument_naam(self) -> None:
        """Monumentnaam is verplicht en moet minimaal 2 tekens bevatten."""
        if not self.monument_naam or len(self.monument_naam.strip()) < 2:
            frappe.throw(
                frappe._("Monumentnaam is verplicht en moet minimaal 2 tekens bevatten."),
                title=frappe._("Validatiefout"),
            )

    def _validate_monument_nummer(self) -> None:
        """
        RCE-monumentnummer: maximaal 6 cijfers.
        Het nummer wordt bij opslaan genormaliseerd naar 6 posities met voorloopnullen.
        """
        if self.monument_nummer:
            cleaned = self.monument_nummer.strip()
            if not re.match(r"^\d{1,6}$", cleaned):
                frappe.throw(
                    frappe._(
                        "Monumentnummer '{0}' is ongeldig. "
                        "Voer maximaal 6 cijfers in (RCE-nummer)."
                    ).format(self.monument_nummer),
                    title=frappe._("Validatiefout"),
                )

    def _normalize_monument_nummer(self) -> None:
        """Normaliseer monumentnummer naar 6 posities met voorloopnullen."""
        if self.monument_nummer:
            self.monument_nummer = self.monument_nummer.strip().zfill(6)

    def _validate_bouwperiode(self) -> None:
        """
        Valideer de bouwperiode-jaren:
        - Beide jaren moeten realistisch zijn (700–huidig jaar)
        - Eindjaar mag niet vóór beginjaar liggen
        """
        import datetime

        huidig_jaar = datetime.date.today().year

        if self.bouwperiode_start:
            if not (700 <= int(self.bouwperiode_start) <= huidig_jaar):
                frappe.throw(
                    frappe._("Beginjaar bouwperiode ({0}) is onrealistisch.").format(
                        self.bouwperiode_start
                    ),
                    title=frappe._("Validatiefout"),
                )

        if self.bouwperiode_eind:
            if not (700 <= int(self.bouwperiode_eind) <= huidig_jaar):
                frappe.throw(
                    frappe._("Eindjaar bouwperiode ({0}) is onrealistisch.").format(
                        self.bouwperiode_eind
                    ),
                    title=frappe._("Validatiefout"),
                )

        if self.bouwperiode_start and self.bouwperiode_eind:
            if int(self.bouwperiode_eind) < int(self.bouwperiode_start):
                frappe.throw(
                    frappe._(
                        "Eindjaar bouwperiode ({0}) mag niet vóór het beginjaar ({1}) liggen."
                    ).format(self.bouwperiode_eind, self.bouwperiode_start),
                    title=frappe._("Validatiefout"),
                )

    def _validate_coordinaten(self) -> None:
        """
        Valideer GPS-coördinaten voor Nederland:
        - Breedtegraad (lat): 50.5 – 53.7
        - Lengtegraad (lon): 3.3 – 7.3
        """
        if self.latitude is not None and self.latitude != 0:
            if not (50.5 <= float(self.latitude) <= 53.7):
                frappe.throw(
                    frappe._(
                        "Breedtegraad {0} valt buiten Nederland (verwacht: 50.5–53.7)."
                    ).format(self.latitude),
                    title=frappe._("Validatiefout"),
                )

        if self.longitude is not None and self.longitude != 0:
            if not (3.3 <= float(self.longitude) <= 7.3):
                frappe.throw(
                    frappe._(
                        "Lengtegraad {0} valt buiten Nederland (verwacht: 3.3–7.3)."
                    ).format(self.longitude),
                    title=frappe._("Validatiefout"),
                )

    def _validate_postcode(self) -> None:
        """Nederlandse postcode: 4 cijfers + optionele spatie + 2 letters."""
        if self.postcode:
            postcode_pattern = re.compile(r"^\d{4}\s?[A-Za-z]{2}$")
            if not postcode_pattern.match(self.postcode.strip()):
                frappe.throw(
                    frappe._("Postcode '{0}' is ongeldig. Gebruik het formaat 1234 AB.").format(
                        self.postcode
                    ),
                    title=frappe._("Validatiefout"),
                )

    def get_bouwdelen(self) -> list[dict]:
        """Geef alle actieve bouwdelen van dit monument terug, gesorteerd op volgorde."""
        return frappe.get_all(
            "Bouwdeel",
            filters={"monument": self.name, "actief": 1},
            fields=[
                "name",
                "bouwdeel_naam",
                "nlsfb_code",
                "nlsfb_omschrijving",
                "soort",
                "materiaal",
                "oppervlak_m2",
                "volgorde",
            ],
            order_by="volgorde asc",
        )

    def get_laatste_inspectie(self) -> dict | None:
        """
        Geef de meest recente inspectie van dit monument terug.
        Vereist dat de inspect-app geïnstalleerd is.
        """
        if not frappe.db.exists("DocType", "Inspectie"):
            return None

        resultaten = frappe.get_all(
            "Inspectie",
            filters={"monument": self.name},
            fields=["name", "datum", "type", "totaalconditiescore", "status"],
            order_by="datum desc",
            limit=1,
        )
        return resultaten[0] if resultaten else None
