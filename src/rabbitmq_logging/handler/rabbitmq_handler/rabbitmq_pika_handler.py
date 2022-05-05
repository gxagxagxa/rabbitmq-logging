import logging
from logging import LogRecord
from typing import Optional

import pika
import pika.exceptions

from rabbitmq_logging.settings import RabbitMQSettings


class RabbitMQPikaHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET, formatter=None, settings: Optional[RabbitMQSettings] = None) -> None:
        super().__init__(level)
        self.level = level
        self.formatter = formatter
        self.settings: RabbitMQSettings = settings or RabbitMQSettings()
        self._is_connected: bool = False
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.adapters.blocking_connection.BlockingChannel] = None
        self.createLock()

    def open_connection(self):
        if not self._is_connected:
            credential_param = pika.PlainCredentials(username=self.settings.RABBITMQ_USERNAME,
                                                     password=self.settings.RABBITMQ_PASSWORD.get_secret_value())
            connection_param = pika.ConnectionParameters(host=self.settings.RABBITMQ_HOST,
                                                         port=self.settings.RABBITMQ_PORT,
                                                         virtual_host=self.settings.RABBITMQ_VIRTUAL_HOST,
                                                         credentials=credential_param)
            try:
                self.connection = pika.BlockingConnection(connection_param)
            except pika.exceptions.AMQPConnectionError as e:
                self.close_connection()
                raise e
            else:
                try:
                    self.channel = self.connection.channel()
                except pika.exceptions.AMQPChannelError as e:
                    self.close_connection()
                    raise e
                else:
                    try:
                        self._setup_exchange_and_queue()
                    except pika.exceptions.AMQPError as e:
                        self.close_connection()
                        raise e
                    else:
                        self._is_connected = True

    def close_connection(self):
        if self.channel:
            try:
                self.channel.close()
            except pika.exceptions.AMQPChannelError as e:
                raise e
        if self.connection:
            try:
                self.connection.close()
            except pika.exceptions.AMQPConnectionError as e:
                raise e

        self.channel = None
        self.connection = None
        self._is_connected = False

    def _setup_exchange_and_queue(self):
        self.channel.exchange_declare(self.settings.RABBITMQ_LOGGING_EXCHANGE, 'topic', auto_delete=False)
        self.channel.queue_declare(self.settings.RABBITMQ_LOGGING_QUEUE, auto_delete=False)
        self.channel.queue_bind(self.settings.RABBITMQ_LOGGING_QUEUE, self.settings.RABBITMQ_LOGGING_EXCHANGE,
                                routing_key=self.settings.RABBITMQ_LOGGING_ROUTER_KEY)

    def emit(self, record: LogRecord) -> None:
        self.acquire()

        if not self._is_connected:
            self.open_connection()

        try:
            formatted_record = self.format(record)
            self.channel.basic_publish(exchange=self.settings.RABBITMQ_LOGGING_EXCHANGE,
                                       routing_key=self.settings.RABBITMQ_LOGGING_ROUTER_KEY,
                                       body=formatted_record.encode(),
                                       properties=pika.BasicProperties(app_id=record.name))

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
