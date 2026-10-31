import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
from urllib import parse

from appium.webdriver import appium_connection
from appium.webdriver.client_config import AppiumClientConfig


class AppiumConnectionTest(unittest.TestCase):
    def tearDown(self):
        appium_connection.AppiumConnection.extra_headers = {}

    def test_get_remote_connection_headers(self):
        headers = appium_connection.AppiumConnection.get_remote_connection_headers(
            parse.urlparse('http://http://127.0.0.1:4723/session')
        )
        self.assertIsNotNone(headers.get('X-Idempotency-Key'))

        headers = appium_connection.AppiumConnection.get_remote_connection_headers(
            parse.urlparse('http://http://127.0.0.1:4723/session/session_id')
        )
        self.assertIsNone(headers.get('X-Idempotency-Key'))

        appium_connection.AppiumConnection.extra_headers = {'custom': 'header'}

        headers = appium_connection.AppiumConnection.get_remote_connection_headers(
            parse.urlparse('http://http://127.0.0.1:4723/session')
        )
        self.assertIsNotNone(headers.get('X-Idempotency-Key'))
        self.assertEqual(headers.get('custom'), 'header')

        headers = appium_connection.AppiumConnection.get_remote_connection_headers(
            parse.urlparse('http://http://127.0.0.1:4723/session/session_id')
        )
        self.assertIsNone(headers.get('X-Idempotency-Key'))
        self.assertEqual(headers.get('custom'), 'header')

    def test_concurrent_new_sessions_get_distinct_idempotency_keys(self):
        barrier = threading.Barrier(2)

        def base_headers(cls, parsed_url, keep_alive=True):
            barrier.wait(timeout=2)
            return {}

        appium_connection.AppiumConnection.extra_headers = {}
        with (
            patch.object(
                appium_connection.RemoteConnection,
                'get_remote_connection_headers',
                new=classmethod(base_headers),
            ),
            ThreadPoolExecutor(max_workers=2) as pool,
        ):
            results = list(
                pool.map(
                    lambda _: appium_connection.AppiumConnection.get_remote_connection_headers(
                        parse.urlparse('http://127.0.0.1:4723/session')
                    ),
                    range(2),
                )
            )

        keys = [headers['X-Idempotency-Key'] for headers in results]
        self.assertEqual(len(set(keys)), 2)

    def test_remove_headers_case_insensitive(self):
        for h in ['X-Idempotency-Key', 'X-idempotency-Key', 'x-idempotency-key']:
            appium_connection.AppiumConnection.extra_headers = {h: 'value'}
            headers = appium_connection.AppiumConnection.get_remote_connection_headers(
                parse.urlparse('http://http://127.0.0.1:4723/session/session_id')
            )
            self.assertNotIn('x-idempotency-key', {k.lower() for k in headers})

    def test_idempotency_key_is_not_stored_on_the_class(self):
        first = appium_connection.AppiumConnection.get_remote_connection_headers(
            parse.urlparse('http://127.0.0.1:4723/session')
        )
        second = appium_connection.AppiumConnection.get_remote_connection_headers(
            parse.urlparse('http://127.0.0.1:4723/session')
        )
        self.assertNotEqual(first['X-Idempotency-Key'], second['X-Idempotency-Key'])
        self.assertEqual(appium_connection.AppiumConnection.extra_headers, {})

    def test_connection_uses_its_client_config_headers(self):
        connection = appium_connection.AppiumConnection(
            client_config=AppiumClientConfig(
                remote_server_addr='http://127.0.0.1:4723',
                extra_headers={'X-Tenant': 'team-a'},
                user_agent='my-agent/1.0',
            )
        )

        headers = connection.get_remote_connection_headers(parse.urlparse('http://127.0.0.1:4723/session'))
        self.assertEqual(headers.get('X-Tenant'), 'team-a')
        self.assertEqual(headers.get('User-Agent'), 'my-agent/1.0')
        self.assertIsNotNone(headers.get('X-Idempotency-Key'))

        headers = connection.get_remote_connection_headers(parse.urlparse('http://127.0.0.1:4723/session/session_id'))
        self.assertEqual(headers.get('X-Tenant'), 'team-a')
        self.assertIsNone(headers.get('X-Idempotency-Key'))

    def test_connection_keeps_appium_user_agent_by_default(self):
        connection = appium_connection.AppiumConnection(
            client_config=AppiumClientConfig(remote_server_addr='http://127.0.0.1:4723')
        )

        headers = connection.get_remote_connection_headers(parse.urlparse('http://127.0.0.1:4723/session'))
        self.assertTrue(headers.get('User-Agent', '').startswith(appium_connection.PREFIX_HEADER))
