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
from selenium.common.exceptions import UnexpectedAlertPresentException

from appium.webdriver.errorhandler import MobileErrorHandler
from test.unit.helper.test_helper import android_w3c_driver, appium_command


def _unexpected_alert_body(**extra) -> str:
    return json.dumps({'value': {'error': 'unexpected alert open', 'message': 'alert', 'stacktrace': '', **extra}})


class TestUnexpectedAlertText:
    def test_alert_text_is_taken_from_w3c_data(self):
        response = {'status': 500, 'value': _unexpected_alert_body(data={'text': 'Hello'})}

        with pytest.raises(UnexpectedAlertPresentException) as excinfo:
            MobileErrorHandler().check_response(response)

        assert excinfo.value.alert_text == 'Hello'
        assert 'Alert Text: Hello' in str(excinfo.value)

    @pytest.mark.parametrize('extra', [{}, {'data': {}}])
    def test_alert_text_is_none_without_text(self, extra):
        response = {'status': 500, 'value': _unexpected_alert_body(**extra)}

        with pytest.raises(UnexpectedAlertPresentException) as excinfo:
            MobileErrorHandler().check_response(response)

        assert excinfo.value.alert_text is None

    @httpretty.activate
    def test_find_element_raises_with_alert_text(self):
        driver = android_w3c_driver()
        httpretty.register_uri(
            httpretty.POST,
            appium_command('/session/1234567890/element'),
            status=500,
            body=_unexpected_alert_body(data={'text': 'Hello'}),
            content_type='application/json',
        )

        with pytest.raises(UnexpectedAlertPresentException) as excinfo:
            driver.find_element('id', 'element_id')

        assert excinfo.value.alert_text == 'Hello'
