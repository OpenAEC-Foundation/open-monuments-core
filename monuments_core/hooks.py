from . import __version__ as app_version

app_name = "monuments_core"
app_title = "Open-Monuments Core"
app_publisher = "OpenAEC Foundation"
app_description = "Monumentenregister: centrale database voor monument-, bouwdeel- en abonnementenbeheer."
app_email = "info@openaec.org"
app_license = "lgpl-3.0"

required_apps = ["frappe", "erpnext"]

# Custom roles aanmaken bij installatie
fixtures = [
    {
        "dt": "Role",
        "filters": [["role_name", "in", ["Monumentenwachter", "Eigenaar Portal"]]],
    },
    {
        "dt": "Custom Field",
        "filters": [["module", "=", "Monuments Core"]],
    },
]

# Frappe scheduler-taken
scheduler_events = {
    "daily": [
        "monuments_core.tasks.update_rijksmonumentenregister_cache",
    ],
}
