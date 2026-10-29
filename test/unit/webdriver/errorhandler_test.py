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

import httpretty
import pytest
from selenium.common.exceptions import NoSuchElementException, WebDriverException

from appium.webdriver.errorhandler import MobileErrorHandler
from test.unit.helper.test_helper import android_w3c_driver, appium_command


class TestMobileErrorHandler:
    @pytest.mark.parametrize(
        'response',
        [
            {'status': 502, 'value': '<html><body>502 Bad Gateway</body></html>'},
            {'status': 401, 'value': 'Authorization Required'},
            {'status': 500, 'value': 'Internal Server Error'},
            {'status': 500, 'value': json.dumps(['not', 'a', 'w3c', 'error'])},
        ],
    )
    def test_raises_on_http_error_without_w3c_error_body(self, response):
        with pytest.raises(WebDriverException):
            MobileErrorHandler().check_response(response)

    def test_raises_w3c_error(self):
        response = {
            'status': 404,
            'value': json.dumps({'value': {'error': 'no such element', 'message': 'not found', 'stacktrace': ''}}),
        }
        with pytest.raises(NoSuchElementException, match='not found'):
            MobileErrorHandler().check_response(response)

    @pytest.mark.parametrize(
        'response',
        [
            {'value': {'value': {'error': 'none', 'message': 'ok'}}},
            {'value': None},
            {'status': 0, 'value': 'ok'},
        ],
    )
    def test_does_not_raise_on_success(self, response):
        MobileErrorHandler().check_response(response)

    @httpretty.activate
    def test_find_element_raises_on_proxy_error_page(self):
        driver = android_w3c_driver()
        httpretty.register_uri(
            httpretty.POST,
            appium_command('/session/1234567890/element'),
            status=502,
            body='<html><body>502 Bad Gateway</body></html>',
            content_type='text/html',
        )

        with pytest.raises(WebDriverException, match='502 Bad Gateway'):
            driver.find_element('id', 'element_id')
