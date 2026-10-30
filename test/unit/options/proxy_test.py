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

from selenium.webdriver.common.proxy import Proxy, ProxyType

from appium.options.android import UiAutomator2Options
from appium.options.common import AppiumOptions


def test_proxy_is_none_by_default():
    assert AppiumOptions().proxy is None
    assert UiAutomator2Options().proxy is None


def test_proxy_can_be_set():
    proxy = Proxy({'proxyType': ProxyType.MANUAL, 'httpProxy': 'proxy.example:8080'})
    options = UiAutomator2Options()
    options.proxy = proxy

    assert options.proxy is proxy
    assert options.to_w3c()['capabilities']['alwaysMatch']['proxy'] == {
        'proxyType': 'manual',
        'httpProxy': 'proxy.example:8080',
    }


def test_default_capabilities_are_unchanged():
    assert AppiumOptions().to_capabilities() == {}
    assert UiAutomator2Options().to_w3c() == {
        'capabilities': {
            'firstMatch': [{}],
            'alwaysMatch': {'appium:automationName': 'UIAutomator2', 'platformName': 'Android'},
        }
    }
