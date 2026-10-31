#!/usr/bin/env python

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import functools
import uuid
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from selenium.webdriver.remote.remote_connection import RemoteConnection

from appium.common.helper import library_version

if TYPE_CHECKING:
    from urllib.parse import ParseResult


PREFIX_HEADER = 'appium/'

HEADER_IDEMOTENCY_KEY = 'X-Idempotency-Key'


def _get_new_headers(key: str, headers: dict[str, str]) -> dict[str, str]:
    """Return a new dictionary of heafers without the given key.
    The key match is case-insensitive."""
    lower_key = key.lower()
    return {k: v for k, v in headers.items() if k.lower() != lower_key}


class _classorinstancemethod:
    """Bind the wrapped function to the instance when accessed on one, else to the class.

    Selenium's RemoteConnection.get_remote_connection_headers is bound this way, so that
    a connection uses the user agent and the extra headers of its own client config.
    """

    def __init__(self, func: Callable) -> None:
        self.func = func
        functools.update_wrapper(self, func)  # type: ignore[arg-type]

    def __get__(self, obj: Any, cls: type | None = None) -> Callable:
        return functools.partial(self.func, obj if obj is not None else cls)


class AppiumConnection(RemoteConnection):
    """
    A subclass of selenium.webdriver.remote.remote_connection.Remoteconnection.

    The changes are

    * The default user agent
    * Adds 'X-Idempotency-Key' header in a new session request to avoid proceeding
        the same request multiple times in the Appium server side.
        * https://github.com/appium/appium-base-driver/pull/400
    """

    user_agent = f'{PREFIX_HEADER}{library_version()} ({RemoteConnection.user_agent})'
    extra_headers = {}

    @_classorinstancemethod
    def get_remote_connection_headers(cls, parsed_url: 'ParseResult', keep_alive: bool = True) -> dict[str, Any]:
        """Override get_remote_connection_headers in RemoteConnection to control the extra headers.
        This method will be used in sending a request method in this class.

        When called on a connection instance, the user agent and the extra headers come from
        that connection's client config, as in RemoteConnection.
        """
        headers = _get_new_headers(
            HEADER_IDEMOTENCY_KEY, super().get_remote_connection_headers(parsed_url, keep_alive=keep_alive)
        )
        if parsed_url.path.endswith('/session'):
            # https://github.com/appium/appium-base-driver/pull/400
            # Keep the per-request idempotency key local: sessions may be created concurrently.
            headers[HEADER_IDEMOTENCY_KEY] = str(uuid.uuid4())
        return headers
