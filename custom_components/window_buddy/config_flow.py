from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_ENTITY_ID, CONF_NAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    TextSelector,
    EntitySelector,
    EntitySelectorConfig,
    SelectSelector,
    SelectSelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
)

from .const import DOMAIN, CONF_CALCULATION_MODE, CONF_AZIMUTH, CONF_WIDTH, CONF_HEIGHT

CALCULATION_MODES = ["simple", "precise"]


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._user_input: dict[str, Any] = {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """First step: Get name, sun entity, and calculation method."""
        if user_input is not None:
            self._user_input.update(user_input)
            return await self.async_step_mode_specific()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_NAME): TextSelector(),
                vol.Required(CONF_CALCULATION_MODE, default="simple"): SelectSelector(
                    SelectSelectorConfig(
                        options=CALCULATION_MODES,
                        translation_key="calculation_mode"
                    )
                ),
                vol.Required(CONF_ENTITY_ID, default="sun.sun"): EntitySelector(
                    EntitySelectorConfig(domain=["sun"])
                ),
            })
        )

    async def async_step_mode_specific(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Second step: Get azimuth or width/height depending on mode."""
        if user_input is not None:
            self._user_input.update(user_input)
            return self.async_create_entry(title=self._user_input[CONF_NAME], data=self._user_input)

        mode = self._user_input[CONF_CALCULATION_MODE]

        schema = {
            vol.Required(CONF_AZIMUTH): NumberSelector(
                NumberSelectorConfig(min=0, max=360, step=1, mode=NumberSelectorMode.BOX)
            )
        }

        if mode == "precise":
            schema.update({
                vol.Required(CONF_WIDTH): NumberSelector(
                    NumberSelectorConfig(min=0.1, max=10, step=0.1, mode=NumberSelectorMode.BOX)
                ),
                vol.Required(CONF_HEIGHT): NumberSelector(
                    NumberSelectorConfig(min=0.1, max=10, step=0.1, mode=NumberSelectorMode.BOX)
                ),
            })

        return self.async_show_form(
            step_id="mode_specific",
            data_schema=vol.Schema(schema),
        )
