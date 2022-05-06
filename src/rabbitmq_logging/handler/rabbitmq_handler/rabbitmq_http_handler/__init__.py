import logging
from logging import LogRecord
from typing import Optional
from urllib.parse import quote

import requests

from rabbitmq_logging.settings import RabbitMQSettings


class RabbitMQHttpHandler(logging.Handler):

    def __init__(self, level=logging.NOTSET, formatter=None, settings: Optional[RabbitMQSettings] = None,
                 https=False) -> None:
        super().__init__(level)
        self.level = level
        self.formatter = formatter
        self.settings: RabbitMQSettings = settings or RabbitMQSettings()
        self._is_connected = False
        self._is_https = https
        self.base_url = self._build_base_url()
        self.createLock()

    def _build_base_url(self):
        base_url = '{schema}{net_loc}:{port}'.format(schema='https://' if self._is_https else 'http://',
                                                     net_loc=self.settings.RABBITMQ_HOST,
                                                     port=self.settings.RABBITMQ_HTTP_PORT)
        return base_url

    def _ensure_exchange(self):
        endpoint = '/api/exchanges/{vhost}/{exchange}'.format(
            vhost=quote(self.settings.RABBITMQ_VIRTUAL_HOST, safe=''),
            exchange=quote(self.settings.RABBITMQ_LOGGING_EXCHANGE, safe=''))
        full_url = self.base_url + endpoint
        try:
            response = requests.put(
                full_url,
                headers={'Content-Type': 'application/json'},
                auth=(self.settings.RABBITMQ_USERNAME, self.settings.RABBITMQ_PASSWORD.get_secret_value()),
                json={"type": "topic", "auto_delete": False}
            )
        except requests.HTTPError as e:
            raise e
        else:
            if not (200 <= response.status_code <= 299):
                raise requests.exceptions.RequestException

    def _ensure_queue(self):
        endpoint = '/api/queues/{vhost}/{queue}'.format(
            vhost=quote(self.settings.RABBITMQ_VIRTUAL_HOST, safe=''),
            queue=quote(self.settings.RABBITMQ_LOGGING_QUEUE, safe=''))
        full_url = self.base_url + endpoint
        try:
            response = requests.put(
                full_url,
                headers={'Content-Type': 'application/json'},
                auth=(self.settings.RABBITMQ_USERNAME, self.settings.RABBITMQ_PASSWORD.get_secret_value()),
                json={"auto_delete": False}
            )
        except requests.HTTPError as e:
            raise e
        else:
            if not (200 <= response.status_code <= 299):
                raise requests.exceptions.RequestException

    def _ensure_bind(self):
        endpoint = '/api/bindings/{vhost}/e/{exchange}/q/{queue}'.format(
            vhost=quote(self.settings.RABBITMQ_VIRTUAL_HOST, safe=''),
            exchange=quote(self.settings.RABBITMQ_LOGGING_EXCHANGE, safe=''),
            queue=quote(self.settings.RABBITMQ_LOGGING_QUEUE, safe=''))
        full_url = self.base_url + endpoint
        try:
            response = requests.post(
                full_url,
                headers={'Content-Type': 'application/json'},
                auth=(self.settings.RABBITMQ_USERNAME, self.settings.RABBITMQ_PASSWORD.get_secret_value()),
                json={"routing_key": self.settings.RABBITMQ_LOGGING_ROUTER_KEY}
            )
        except requests.HTTPError as e:
            raise e
        else:
            if not (200 <= response.status_code <= 299):
                raise requests.exceptions.RequestException

    def open_connection(self):
        self._ensure_exchange()
        self._ensure_queue()
        self._ensure_bind()
        self._is_connected = True

    def close_connection(self):
        self._is_connected = False

    def _publish_message(self, message, **kwargs):
        endpoint = '/api/exchanges/{vhost}/{exchange}/publish'.format(
            vhost=quote(self.settings.RABBITMQ_VIRTUAL_HOST, safe=''),
            exchange=quote(self.settings.RABBITMQ_LOGGING_EXCHANGE, safe=''))
        full_url = self.base_url + endpoint
        try:
            response = requests.post(
                full_url,
                headers={'Content-Type': 'application/json'},
                auth=(self.settings.RABBITMQ_USERNAME, self.settings.RABBITMQ_PASSWORD.get_secret_value()),
                json={"routing_key": self.settings.RABBITMQ_LOGGING_ROUTER_KEY,
                      "payload": message,
                      "payload_encoding": "string",
                      "properties": kwargs}
            )
        except requests.HTTPError as e:
            raise e
        else:
            if not (200 <= response.status_code <= 299):
                raise requests.exceptions.RequestException

    def emit(self, record: LogRecord) -> None:
        self.acquire()

        if not self._is_connected:
            self.open_connection()

        try:
            formatted_record = self.format(record)
            self._publish_message(formatted_record, app_id=record.name)
        except Exception as e:
            raise e
        finally:
            self.release()

    def close(self):
        self.acquire()
        try:
            self.close_connection()
        finally:
            self.release()

    def __del__(self):
        self.close()
