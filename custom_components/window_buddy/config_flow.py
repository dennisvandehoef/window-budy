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

from .const import (
    DOMAIN,
    CONF_CALCULATION_MODE,
    CONF_AZIMUTH,
    CONF_WIDTH,
    CONF_HEIGHT,
)

# Additional constants for blockade configuration.
BLOCK_LEFT_SIDE = "block_left_side"
BLOCK_LEFT_AWAY = "block_left_away"
BLOCK_LEFT_ANGLE = "block_left_angle"
BLOCK_RIGHT_SIDE = "block_right_side"
BLOCK_RIGHT_AWAY = "block_right_away"
BLOCK_RIGHT_ANGLE = "block_right_angle"
BLOCK_TOP_SIDE = "block_top_side"
BLOCK_TOP_AWAY = "block_top_away"
BLOCK_TOP_ANGLE = "block_top_angle"
BLOCK_BOTTOM_SIDE = "block_bottom_side"
BLOCK_BOTTOM_AWAY = "block_bottom_away"
BLOCK_BOTTOM_ANGLE = "block_bottom_angle"

CALCULATION_MODES = ["simple", "precise"]

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Window Buddy integration."""
    VERSION = 1

    def __init__(self) -> None:
        self._user_input: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 1: Get name, calculation method, and sun entity."""
        if user_input is not None:
            self._user_input.update(user_input)
            return await self.async_step_azimuth()

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

    async def async_step_azimuth(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """
        Step 2: Ask for the window's azimuth.
        This step is common for both simple and precise modes.
        """
        if user_input is not None:
            self._user_input.update(user_input)
            if self._user_input[CONF_CALCULATION_MODE] == "precise":
                return await self.async_step_precise_extra()
            return self.async_create_entry(title=self._user_input[CONF_NAME], data=self._user_input)

        return self.async_show_form(
            step_id="azimuth",
            data_schema=vol.Schema({
                vol.Required(CONF_AZIMUTH): NumberSelector(
                    NumberSelectorConfig(
                        unit_of_measurement="°",
                        step=1,
                        mode=NumberSelectorMode.BOX
                    )
                )
            })
        )

    async def async_step_precise_extra(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """
        Step 3 (Precise mode only): Get additional configuration:
          - Window width and height.
          - Optional blockade configuration for Left, Right, Top, and Bottom.
            Each direction has:
              • A 'side distance'
              • A 'distance away'
              • An 'angle'
        The explanation advises the user to use a consistent unit (e.g. cm or inches) for all measurements.
        """
        if user_input is not None:
            self._user_input.update(user_input)
            return self.async_create_entry(title=self._user_input[CONF_NAME], data=self._user_input)

        schema = {
            vol.Required(CONF_WIDTH): NumberSelector(
                NumberSelectorConfig(
                    step=0.1,
                    mode=NumberSelectorMode.BOX
                )
            ),
            vol.Required(CONF_HEIGHT): NumberSelector(
                NumberSelectorConfig(
                    step=0.1,
                    mode=NumberSelectorMode.BOX
                )
            ),
            # Optional blockade fields:
            vol.Optional(BLOCK_LEFT_SIDE): NumberSelector(
                NumberSelectorConfig(step=0.1, mode=NumberSelectorMode.BOX)
            ),
            vol.Optional(BLOCK_LEFT_AWAY): NumberSelector(
                NumberSelectorConfig(step=0.1, mode=NumberSelectorMode.BOX)
            ),
            vol.Optional(BLOCK_LEFT_ANGLE): NumberSelector(
                NumberSelectorConfig(step=1, mode=NumberSelectorMode.BOX)
            ),
            vol.Optional(BLOCK_RIGHT_SIDE): NumberSelector(
                NumberSelectorConfig(step=0.1, mode=NumberSelectorMode.BOX)
            ),
            vol.Optional(BLOCK_RIGHT_AWAY): NumberSelector(
                NumberSelectorConfig(step=0.1, mode=NumberSelectorMode.BOX)
            ),
            vol.Optional(BLOCK_RIGHT_ANGLE): NumberSelector(
                NumberSelectorConfig(step=1, mode=NumberSelectorMode.BOX)
            ),
            vol.Optional(BLOCK_TOP_SIDE): NumberSelector(
                NumberSelectorConfig(step=0.1, mode=NumberSelectorMode.BOX)
            ),
            vol.Optional(BLOCK_TOP_AWAY): NumberSelector(
                NumberSelectorConfig(step=0.1, mode=NumberSelectorMode.BOX)
            ),
            vol.Optional(BLOCK_TOP_ANGLE): NumberSelector(
                NumberSelectorConfig(step=1, mode=NumberSelectorMode.BOX)
            ),
            vol.Optional(BLOCK_BOTTOM_SIDE): NumberSelector(
                NumberSelectorConfig(step=0.1, mode=NumberSelectorMode.BOX)
            ),
            vol.Optional(BLOCK_BOTTOM_AWAY): NumberSelector(
                NumberSelectorConfig(step=0.1, mode=NumberSelectorMode.BOX)
            ),
            vol.Optional(BLOCK_BOTTOM_ANGLE): NumberSelector(
                NumberSelectorConfig(step=1, mode=NumberSelectorMode.BOX)
            ),
        }

        return self.async_show_form(
            step_id="precise_extra",
            data_schema=vol.Schema(schema),
        )
