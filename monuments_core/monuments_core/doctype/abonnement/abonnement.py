# Copyright (c) 2026, OpenAEC Foundation and contributors
# License: LGPL-3.0

from __future__ import annotations

import datetime

import frappe
from frappe.model.document import Document


class Abonnement(Document):
    """
    Abonnement — de contractuele relatie tussen een eigenaar en Monumentenwacht
    voor de periodieke inspectie van een monument.

    Autoname: ABO-{YYYY}-{#####} (bijv. ABO-2026-00001)

    Abonnementstypen:
    - Basis: jaarlijkse quickscan
    - Standaard: jaarlijkse volledige inspectie
    - Plus: halfjaarlijkse inspectie + MJOP-update

    Koppelt Eigenaar en Monument. Een monument kan per periode maar één actief
    abonnement hebben.
    """

    def validate(self) -> None:
        """Valideer het Abonnement-document vóór opslaan."""
        self._validate_eigenaar()
        self._validate_monument()
        self._validate_datums()
        self._validate_prijs()
        self._check_dubbel_actief_abonnement()

    def _validate_eigenaar(self) -> None:
        """Controleer of de gekoppelde eigenaar bestaat."""
        if not self.eigenaar:
            frappe.throw(
                frappe._("Een eigenaar is verplicht voor een abonnement."),
                title=frappe._("Validatiefout"),
            )
        if not frappe.db.exists("Eigenaar", self.eigenaar):
            frappe.throw(
                frappe._("Eigenaar '{0}' bestaat niet.").format(self.eigenaar),
                title=frappe._("Validatiefout"),
            )

    def _validate_monument(self) -> None:
        """Controleer of het gekoppelde monument bestaat."""
        if not self.monument:
            frappe.throw(
                frappe._("Een monument is verplicht voor een abonnement."),
                title=frappe._("Validatiefout"),
            )
        if not frappe.db.exists("Monument", self.monument):
            frappe.throw(
                frappe._("Monument '{0}' bestaat niet.").format(self.monument),
                title=frappe._("Validatiefout"),
            )

    def _validate_datums(self) -> None:
        """
        Valideer de abonnementsperiode:
        - Einddatum mag niet vóór startdatum liggen
        - Startdatum moet in het verleden of heden zijn (niet meer dan 1 jaar in de toekomst)
        """
        if self.startdatum and self.einddatum:
            start = frappe.utils.getdate(self.startdatum)
            eind = frappe.utils.getdate(self.einddatum)
            if eind < start:
                frappe.throw(
                    frappe._("Einddatum ({0}) mag niet vóór de startdatum ({1}) liggen.").format(
                        frappe.utils.formatdate(self.einddatum),
                        frappe.utils.formatdate(self.startdatum),
                    ),
                    title=frappe._("Validatiefout"),
                )

        if self.startdatum:
            start = frappe.utils.getdate(self.startdatum)
            max_toekomst = datetime.date.today() + datetime.timedelta(days=366)
            if start > max_toekomst:
                frappe.msgprint(
                    frappe._(
                        "Startdatum ligt meer dan een jaar in de toekomst. Controleer of dit correct is."
                    ),
                    indicator="orange",
                    alert=True,
                )

    def _validate_prijs(self) -> None:
        """Prijs per jaar mag niet negatief zijn."""
        if self.prijs_per_jaar is not None and self.prijs_per_jaar < 0:
            frappe.throw(
                frappe._("Prijs per jaar kan niet negatief zijn."),
                title=frappe._("Validatiefout"),
            )

    def _check_dubbel_actief_abonnement(self) -> None:
        """
        Waarschuw als er al een actief abonnement bestaat voor dezelfde
        eigenaar-monument combinatie.
        """
        if self.status not in ("Actief", "Proef"):
            return

        filters = {
            "eigenaar": self.eigenaar,
            "monument": self.monument,
            "status": ["in", ["Actief", "Proef"]],
            "name": ["!=", self.name],
        }
        bestaand = frappe.db.exists("Abonnement", filters)
        if bestaand:
            frappe.msgprint(
                frappe._(
                    "Let op: er bestaat al een actief of proefabonnement ({0}) voor "
                    "dezelfde eigenaar-monument combinatie."
                ).format(bestaand),
                indicator="orange",
                alert=True,
            )

    def is_actief(self) -> bool:
        """Geef True terug als het abonnement momenteel actief is."""
        if self.status != "Actief":
            return False
        vandaag = datetime.date.today()
        if self.startdatum and frappe.utils.getdate(self.startdatum) > vandaag:
            return False
        if self.einddatum and frappe.utils.getdate(self.einddatum) < vandaag:
            return False
        return True
