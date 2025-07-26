"""API Placeholder.

You should create your api seperately and have it hosted on PYPI.  This is included here for the sole purpose
of making this example code executable.
"""

import logging
from collections.abc import Callable

_LOGGER = logging.getLogger(__name__)


class API:
    """Class for example API."""

    def __init__(self, mac: str, pin: str | None, callback: Callable[[], None]) -> None:
        """Initialise."""
        self.mac = mac
        self.pin = pin
        self.connection_changed_callback = callback
        self._connected: bool = False

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
        """Connect once to test if connection works."""
        return

    def connect(self) -> bool:
        """Connect to api."""
        if True:
            # self._connected = True
            return True
        raise APIConnectionError(
            "Error connecting to api. Invalid username or password."
        )

    def disconnect(self) -> bool:
        """Disconnect from api."""
        self._connected = False
        return True


class APIConnectionError(Exception):
    """Exception class for connection error."""
