from homeassistant.helpers.entity import Entity
from homeassistant.core import HomeAssistant
from homeassistant.const import STATE_UNKNOWN

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Set up the Window Buddy sensor."""
    config = entry.data
    async_add_entities([WindowBuddySensor(config)], True)

class WindowBuddySensor(Entity):
    """Representation of a Window Buddy sensor."""

    def __init__(self, config: dict):
        """Initialize the sensor."""
        self._name = config.get("name", "Window Buddy")
        self._width = config["width"]
        self._height = config["height"]
        self._window_azimuth = config["azimuth"]
        self._sun_entity = config.get("entity_id", "sun.sun")
        self._state = None

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._name} Exposure"

    @property
    def state(self):
        """Return the current sun exposure percentage."""
        return self._state

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return "%"

    async def async_update(self) -> None:
        """Update the sensor state."""
        sun_state = self.hass.states.get(self._sun_entity)
        if sun_state is None or sun_state.state == STATE_UNKNOWN:
            self._state = None
            return

        # Retrieve sun attributes.
        sun_azimuth = sun_state.attributes.get("azimuth")
        sun_elevation = sun_state.attributes.get("elevation")
        if sun_azimuth is None or sun_elevation is None:
            self._state = None
            return

        # Example calculation:
        # If the sun's azimuth is within ±15° of the window's azimuth, set exposure to 100%.
        if abs(sun_azimuth - self._window_azimuth) <= 15:
            self._state = 100
        else:
            self._state = 0
