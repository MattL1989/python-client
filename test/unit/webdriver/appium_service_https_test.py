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

import warnings
from unittest.mock import Mock

from appium.webdriver import appium_service
from appium.webdriver.appium_service import is_service_listening

STATUS_URL = 'https://127.0.0.1:4723/status'


def _mock_pool_manager(monkeypatch, request: Mock) -> Mock:
    connection = Mock()
    connection.request = request
    pool_manager = Mock(return_value=connection)
    monkeypatch.setattr(appium_service.urllib3, 'PoolManager', pool_manager)
    return pool_manager


class TestServiceListeningOverHttps:
    def test_probe_does_not_verify_server_certificate(self, monkeypatch):
        pool_manager = _mock_pool_manager(monkeypatch, Mock(return_value=Mock(status=200)))

        assert is_service_listening(STATUS_URL, timeout=1)
        assert pool_manager.call_args.kwargs['cert_reqs'] == 'CERT_NONE'

    def test_probe_suppresses_insecure_request_warning_only_for_its_request(self, monkeypatch):
        insecure_request_warning = appium_service.urllib3.exceptions.InsecureRequestWarning

        def request(method, url):
            warnings.warn('Unverified HTTPS request', insecure_request_warning)
            return Mock(status=200)

        _mock_pool_manager(monkeypatch, Mock(side_effect=request))

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            assert is_service_listening(STATUS_URL, timeout=1)
            assert caught == []

            warnings.warn('Unverified HTTPS request', insecure_request_warning)
            assert [w.category for w in caught] == [insecure_request_warning]
