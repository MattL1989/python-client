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

import json

import pytest
from selenium.common.exceptions import DetachedShadowRootException, NoSuchShadowRootException

from appium.webdriver.errorhandler import MobileErrorHandler


def _w3c_error_response(error: str) -> dict:
    return {
        'status': 404,
        'value': json.dumps({'value': {'error': error, 'message': error, 'stacktrace': ''}}),
    }


class TestShadowRootErrors:
    def test_detached_shadow_root_raises_detached_shadow_root_exception(self):
        with pytest.raises(DetachedShadowRootException):
            MobileErrorHandler().check_response(_w3c_error_response('detached shadow root'))

    def test_no_such_shadow_root_raises_no_such_shadow_root_exception(self):
        with pytest.raises(NoSuchShadowRootException):
            MobileErrorHandler().check_response(_w3c_error_response('no such shadow root'))
