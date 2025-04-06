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
        if self._get_sun_azimuth() is None:
            return 0.0

        if self._entry.data[CONF_CALCULATION_MODE] == "simple":
            return self._simple_exposure()
        return self._precise_exposure()

    def _simple_exposure(self) -> float:
        """Calculate exposure based on azimuth, considering circular ranges."""
        start_azimuth = self._azimuth_start()
        end_azimuth = self._azimuth_end()
        sun_azimuth = self._get_sun_azimuth()

        # If the range crosses the 360-degree mark, we need to handle it in two parts
        if start_azimuth > end_azimuth:
            # Two parts: from start_azimuth to 360, then from 0 to end_azimuth
            if sun_azimuth >= start_azimuth or sun_azimuth <= end_azimuth:
                # Calculate exposure for the first part (start to 360)
                if sun_azimuth >= start_azimuth:
                    exposure_part1 = (360 - start_azimuth + sun_azimuth) / (360 - start_azimuth + end_azimuth) * 100
                else:
                    exposure_part1 = (360 - start_azimuth + sun_azimuth) / (360 - start_azimuth + end_azimuth) * 100
                return round(exposure_part1, 2)
        else:
            # Normal case: Start azimuth is less than end azimuth
            return round((sun_azimuth - start_azimuth) / (end_azimuth - start_azimuth) * 100, 2)


    def _precise_exposure(self) -> float:
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
