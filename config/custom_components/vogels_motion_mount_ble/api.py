"""API Placeholder.

You should create your api seperately and have it hosted on PYPI.  This is included here for the sole purpose
of making this example code executable.
"""

from bleak import BleakClient, BleakScanner
import logging
from collections.abc import Callable
import asyncio

_LOGGER = logging.getLogger(__name__)


class API:
    """Class for example API."""

    def __init__(self, mac: str, pin: str | None, callback: Callable[[], None]) -> None:
        """Initialise."""
        self.mac = mac
        self.pin = pin
        self.connection_changed_callback = callback
        self._connected: bool = False
        self._client: BleakClient | None = None
        self.disconnected_event = asyncio.Event()

    @property
    def connected(self) -> bool:
        """Return connection state."""
        return self._connected

    @connected.setter
    def connected(self, value: bool) -> None:
        """Set connection state and call callback if changed."""
        if self._connected != value:
            self._connected = value
            if self.connection_changed_callback:
                self.connection_changed_callback()

    async def testConnect(self):
        """Test connection to the BLE device once using BleakClient."""
        try:
            _LOGGER.debug("start connectingd")
            async with BleakClient(self.mac, timeout=120) as client:
                connected = client.is_connected
                _LOGGER.debug("Connected to device: %s", connected)
        except Exception as err:
            _LOGGER.error("Failed to connect to device: %s", err)
            raise APIConnectionError("Error connecting to api.") from err

    def _handle_disconnect(self, client):
        _LOGGER.debug("handle Device disconnected!")
        self.disconnected_event.set()

    # todo make it optional if the connection should be maintained or connect on command (when required to send command) or poll time
    async def maintainConnection(self):
        """Maintain connection to device."""
        while True:
            _LOGGER.debug("scanning for device")
            device = await BleakScanner.find_device_by_address(self.mac)

            if device is None:
                _LOGGER.debug("no device found, wait then scan again")
                await asyncio.sleep(5)
                continue

            try:
                _LOGGER.debug("connecting to device")
                async with BleakClient(
                    device, disconnected_callback=self._handle_disconnect, timeout=120
                ) as client:
                    self.connected = client.is_connected
                    _LOGGER.debug("connected to device %s", self.connected)
                    self._client = client
                    self.connected = True
                    await self.disconnected_event.wait()
                    # reset event
                    self.disconnected_event.clear()
                    self.connected = client.is_connected
                    _LOGGER.debug("device disconnected %s", self.connected)
                    self.connected = False
                    await asyncio.sleep(1)
            except Exception:
                # catch bleak.exc.BleakError: No backend with an available connection slot that can reach address D9:13:5D:AB:3B:37 was found
                _LOGGER.exception("Exception while connecting/connected")
                await asyncio.sleep(5)

    def disconnect(self) -> bool:
        """Disconnect from api."""
        self.connected = False
        return True


class APIConnectionError(Exception):
    """Exception class for connection error."""
