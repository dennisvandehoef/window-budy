from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_ENTITY_ID

from .const import DOMAIN

class WindowBuddyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Window Buddy."""
    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> config_entries.FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        schema = vol.Schema({
            vol.Required(CONF_NAME, default="Window 1"): str,
            vol.Required("width"): vol.All(int, vol.Range(min=1)),
            vol.Required("height"): vol.All(int, vol.Range(min=1)),
            vol.Required("azimuth"): vol.All(int, vol.Range(min=0, max=360)),
            vol.Optional(CONF_ENTITY_ID, default="sun.sun"): str,
        })

        return self.async_show_form(step_id="user", data_schema=schema)
