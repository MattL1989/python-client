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

import logging

from appium.common.logger import logger, setup_logger


def _stderr_handlers() -> list[logging.Handler]:
    # pytest attaches its own capture handlers (StreamHandler subclasses) to non-propagating
    # loggers while a test runs, so only count plain StreamHandlers.
    return [handler for handler in logger.handlers if type(handler) is logging.StreamHandler]


class TestSetupLogger:
    def setup_method(self):
        self._level = logger.level

    def teardown_method(self):
        logger.setLevel(self._level)

    def test_setup_logger_does_not_add_another_handler(self):
        handlers = _stderr_handlers()
        # added when the module is imported
        assert len(handlers) == 1

        setup_logger()
        setup_logger(logging.DEBUG)

        assert _stderr_handlers() == handlers

    def test_setup_logger_updates_level(self):
        setup_logger(logging.DEBUG)
        assert logger.level == logging.DEBUG

        setup_logger(logging.WARNING)
        assert logger.level == logging.WARNING
        assert logger.propagate is False
