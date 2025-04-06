from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ENTITY_ID, STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_NAME, CONF_CALCULATION_MODE, CONF_AZIMUTH, CONF_WIDTH, CONF_HEIGHT

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Window Buddy sensor from a config entry."""
    async_add_entities([WindowBuddySensor(entry)])


class WindowBuddySensor(SensorEntity):
    """Representation of a Window Buddy sun exposure sensor."""

    _attr_has_entity_name = True
    _attr_translation_key = "window_buddy_sensor"
    _attr_icon = "mdi:sun-angle-outline"
    _attr_native_unit_of_measurement = "%"

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_sun_exposure"
        self._attr_name = entry.data[CONF_NAME]
        self._attr_extra_state_attributes = {
            "calculation_mode": entry.data[CONF_CALCULATION_MODE],
            "azimuth": entry.data.get(CONF_AZIMUTH),
            "width": entry.data.get(CONF_WIDTH),
            "height": entry.data.get(CONF_HEIGHT),
        }
        self.sun_entity_id = entry.data[CONF_ENTITY_ID]

    @property
    def native_value(self) -> float:
        """Return the estimated sun exposure value."""
        if self._entry.data[CONF_CALCULATION_MODE] == "simple":
            return self._simple_exposure()
        return self._precise_exposure()

    def _simple_exposure(self) -> float:
        """
        Calculate exposure based on sun's azimuth relative to the window's defined range.
        The window is defined by:
          - start = center - 90°
          - center = configured window azimuth (100% exposure)
          - end = center + 90°
        Exposure rises linearly from start (0%) to center (100%), then falls linearly to end (0%).
        Handles circular ranges (i.e. if the range crosses 0°).
        """
        # Get configured center (window azimuth), then compute start and end.
        center = self._entry.data.get(CONF_AZIMUTH, 0)
        start = (center - 90) % 360
        end = (center + 90) % 360

        sun = self._get_sun_azimuth()
        if sun is None:
            return 0.0

        if self._get_sun_elevation() < 0:
            return 0.0

        # Unwrap the angles so that we have a continuous number line.
        unwrapped_center = center
        unwrapped_start = start
        unwrapped_end = end
        unwrapped_sun = sun

        # Adjust start and end if necessary so that start < center < end.
        if unwrapped_start > unwrapped_center:
            unwrapped_start -= 360
        if unwrapped_end < unwrapped_center:
            unwrapped_end += 360

        # Adjust sun similarly: if sun is less than start, add 360.
        if unwrapped_sun < unwrapped_start:
            unwrapped_sun += 360

        # If sun is outside the window range, return 0.
        if unwrapped_sun < unwrapped_start or unwrapped_sun > unwrapped_end:
            return 0.0

        # Piecewise linear interpolation:
        if unwrapped_sun <= unwrapped_center:
            # Rising edge: from start (0%) to center (100%)
            exposure = (unwrapped_sun - unwrapped_start) / (unwrapped_center - unwrapped_start) * 100
        else:
            # Falling edge: from center (100%) to end (0%)
            exposure = (unwrapped_end - unwrapped_sun) / (unwrapped_end - unwrapped_center) * 100

        return round(exposure, 2)


    def _precise_exposure(self) -> float:
        if self._get_sun_azimuth() is None:
            return 0.0

        # Dummy logic using width and height
        azimuth = self._entry.data.get(CONF_AZIMUTH, 0)
        width = self._entry.data.get(CONF_WIDTH, 1.0)
        height = self._entry.data.get(CONF_HEIGHT, 1.0)
        factor = width * height
        angle_factor = max(0.0, min(1.0, 1 - abs(azimuth - 180) / 180))
        return round(angle_factor * factor, 2)

    def _get_sun_azimuth(self) -> float | None:
        """Get the azimuth of the configured sun entity."""
        sun_state = self.hass.states.get(self.sun_entity_id)
        if sun_state is None or sun_state.state == STATE_UNAVAILABLE:
            return None  # If the sun entity is unavailable, return None
        return sun_state.attributes.get("azimuth")

    def _get_sun_elevation(self) -> float | None:
        """Get the elevation of the configured sun entity."""
        sun_state = self.hass.states.get(self.sun_entity_id)
        if sun_state is None or sun_state.state == STATE_UNAVAILABLE:
            return None  # If the sun entity is unavailable, return None
        return sun_state.attributes.get("elevation")

    def _azimuth_start(self) -> int:
        result = self._entry.data.get(CONF_AZIMUTH, 0)
        result = result - 90

        if result < 0:
            result = 360 + result

        return result

    def _azimuth_end(self) -> int:
        result = self._entry.data.get(CONF_AZIMUTH, 0)
        result = result + 90

        if result > 360:
            result = result - 360

        return result
