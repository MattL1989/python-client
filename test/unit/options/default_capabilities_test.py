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

import pytest

from appium.options.android import EspressoOptions, UiAutomator2Options
from appium.options.flutter_integration import FlutterOptions
from appium.options.gecko import GeckoOptions
from appium.options.ios import SafariOptions, XCUITestOptions
from appium.options.mac import Mac2Options
from appium.options.windows import WindowsOptions

OPTIONS_WITH_DEFAULTS = [
    (EspressoOptions, 'Espresso', 'Android'),
    (UiAutomator2Options, 'UIAutomator2', 'Android'),
    (FlutterOptions, 'FlutterIntegration', None),
    (GeckoOptions, 'Gecko', None),
    (SafariOptions, 'Safari', 'iOS'),
    (XCUITestOptions, 'XCUITest', 'iOS'),
    (Mac2Options, 'Mac2', 'Mac'),
    (WindowsOptions, 'Windows', 'Windows'),
]


@pytest.mark.parametrize('options_class, automation_name, platform_name', OPTIONS_WITH_DEFAULTS)
def test_default_capabilities_are_stored_with_w3c_names(options_class, automation_name, platform_name):
    expected = {'appium:automationName': automation_name}
    if platform_name is not None:
        expected['platformName'] = platform_name

    options = options_class()

    assert options.to_capabilities() == expected
    assert options.automation_name == automation_name
    assert options.to_w3c() == {'capabilities': {'firstMatch': [{}], 'alwaysMatch': expected}}


def test_automation_name_setter_replaces_default():
    options = UiAutomator2Options()
    options.automation_name = 'Espresso'

    assert options.automation_name == 'Espresso'
    assert options.to_capabilities() == {'appium:automationName': 'Espresso', 'platformName': 'Android'}


def test_automation_name_can_be_removed():
    options = UiAutomator2Options()
    options.automation_name = None

    assert options.automation_name is None
    assert options.to_capabilities() == {'platformName': 'Android'}
