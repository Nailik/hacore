"""Interfaces with the Integration 101 Template api sensors."""

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .base import ExampleBaseEntity

from . import MyConfigEntry
from .coordinator import ExampleCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the Binary Sensors."""
    _LOGGER.exception("async_setup_entry binary sensor")
    # This gets the data update coordinator from the config entry runtime data as specified in your __init__.py
    coordinator: ExampleCoordinator = config_entry.runtime_data.coordinator

    # Enumerate all the binary sensors in your data value from your DataUpdateCoordinator and add an instance of your binary sensor class
    # to a list for each one.
    # This maybe different in your specific case, depending on how your data is structured
    binary_sensors = [ExampleBinarySensor(coordinator)]

    # Create the binary sensors.
    async_add_entities(binary_sensors)


class ExampleBinarySensor(ExampleBaseEntity, BinarySensorEntity):
    """Implementation of a sensor."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_has_entity_name = True
    _attr_translation_key = "connection"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "connection"

    @property
    def unique_id(self) -> str:
        """Return unique id."""
        # All entities must have a unique id.  Think carefully what you want this to be as
        # changing it later will cause HA to create new entities.
        return f"{DOMAIN}-{self.coordinator.mac}-connected"

    @property
    def is_on(self) -> bool:
        """Return if the binary sensor is on."""
        # This needs to enumerate to true or false
        return self.coordinator.api.connected
