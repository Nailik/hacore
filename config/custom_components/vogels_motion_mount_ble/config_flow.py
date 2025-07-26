"""Config flow for Integration 101 Template integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PIN
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import selector
from homeassistant.helpers.device_registry import format_mac

from .api import API, APIConnectionError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Data to be input by the user in the config flow.
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(
            CONF_NAME, description={"suggested_value": "Vogel's Motion Mount"}
        ): str,
        vol.Optional(CONF_PIN): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=0, max=9999, mode=selector.NumberSelectorMode.BOX
            )
        ),
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    mac = data[CONF_HOST]

    # Create an API instance and try to connect.
    api = API(mac, data.get(CONF_PIN), lambda *_, **__: None)
    try:
        await hass.async_add_executor_job(api.connect)
    except APIConnectionError as err:
        raise CannotConnect from err
    _LOGGER.debug("return")
    return {"title": f"Vogels Motion Mount - {mac}", "mac": mac}


class VogelsMotionMountConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the config flow for VogelsMotionMount Integration."""

    VERSION = 1
    _input_data: dict[str, Any]

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        _LOGGER.debug("async_step_user")
        # Called when you initiate adding an integration via the UI
        errors: dict[str, str] = {}

        if user_input is not None:
            # The form has been filled in and submitted, so process the data provided.
            try:
                _LOGGER.debug("await validate_input")
                # Validate that the setup data is valid and if not handle errors.
                # The errors["base"] values match the values in your strings.json and translation files.
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                _LOGGER.exception("Cannot_connect")
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

            if "base" not in errors:
                _LOGGER.debug("async_step_user2")
                # Validation was successful, so create a unique id for this instance of your integration
                # and create the config entry.
                await self.async_set_unique_id(info["mac"])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info["title"], data=user_input)

        _LOGGER.debug("return self.async_show_form")
        # Show initial form.
        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_bluetooth(self, discovery_info):
        """Handle a bluetooth device being discovered."""
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()

        self.discovery_info = discovery_info  # ← Save for later use

        return await self.async_step_confirm()

    async def async_step_confirm(self, user_input=None):
        """Confirm adding the discovered Bluetooth device."""
        if user_input is not None:
            # User confirmed, create the config entry
            address = self.discovery_info.address
            name = self.discovery_info.name or "Bluetooth Device"

            return self.async_create_entry(
                title=name,
                data={
                    CONF_HOST: address,
                    CONF_NAME: name,
                    CONF_PIN: None,
                },
            )

        # Show a confirmation form
        return self.async_show_form(
            step_id="confirm",
            description_placeholders={
                "name": self.discovery_info.name or "Bluetooth Device"
            },
            data_schema=vol.Schema({}),  # empty form with only "Submit"
        )

    # async def async_step_bluetooth(self, discovery_info):
    #    """Handle the bluetooth device discovered."""
    #    mac = discovery_info.address
    #    name = discovery_info.name or "Bluetooth Device"

    #    await self.async_set_unique_id(mac)
    #    self._abort_if_unique_id_configured()

    #    return self.async_create_entry(
    #        title=name, data={CONF_HOST: mac, CONF_NAME: name, CONF_PIN: None}
    #   )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
