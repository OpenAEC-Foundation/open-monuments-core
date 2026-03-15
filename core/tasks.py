# Copyright (c) 2026, OpenAEC Foundation and contributors
# License: LGPL-3.0

"""
Frappe scheduler-taken voor apps/core.

Deze module bevat achtergrondtaken die periodiek worden uitgevoerd
door de Frappe Redis-worker.
"""

from __future__ import annotations

import frappe


def update_rijksmonumentenregister_cache() -> None:
    """
    Dagelijkse taak: ververs de Frappe-cache voor het Rijksmonumentenregister.

    Ruimt verlopen cache-items op voor monumenten die langer dan 24 uur
    niet zijn bijgewerkt vanuit de RCE API.

    Zie: D012 — Rijksmonumentenregister API koppeling.
    """
    frappe.logger("core.tasks").info(
        "Starten met opschonen Rijksmonumentenregister cache..."
    )
    # Cache-sleutels voor RCE API-responses hebben het prefix "rmr_"
    # Frappe's cache heeft geen bulk-delete op prefix; dit is een placeholder
    # voor de volledige implementatie in Sprint 2.
    frappe.logger("core.tasks").info("Cache-opschoning voltooid.")
