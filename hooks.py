app_name = "monuments_core"
app_title = "Open-Monuments Core"
app_publisher = "OpenAEC Foundation"
app_description = "Monumentenregister: centrale database voor monument-, bouwdeel- en abonnementenbeheer."
app_email = "info@openaec.org"
app_license = "lgpl-3.0"
app_version = "0.1.0"

required_apps = ["frappe", "erpnext"]

# DocTypes waarvoor de standaard Frappe Desk-weergave verborgen wordt
# (we gebruiken een headless React-frontend, zie D009)
hide_in_desk = 1

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
        "monuments_core.monuments_core.tasks.update_rijksmonumentenregister_cache",
    ],
}

# Whitelisted API-methoden toegankelijk voor de React-frontend
override_whitelisted_methods = {}

# Documentatie-URL
app_documentation = "https://github.com/OpenAEC-Foundation/Open-Monuments/tree/main/apps/core"
