import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

import pika
import pika.exceptions

from daemonlize import Daemon
from rabbitmq_logging.settings import RabbitMQSettings


class RabbitMQDiskLogConsumer(Daemon):

    def __init__(self, pid_file=None, stdin='/dev/null', stdout='', stderr='',
                 settings: Optional[RabbitMQSettings] = None,
                 log_file: Optional[Path] = None) -> None:
        pid_file = pid_file or Path(__file__).with_name('pid_file')
        stdout = stdout or Path(__file__).with_name('stdout')
        stderr = stderr or Path(__file__).with_name('stderr')
        super().__init__(pid_file, stdin, stdout, stderr)
        self.settings: RabbitMQSettings = settings or RabbitMQSettings()
        self._is_connected: bool = False
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.adapters.blocking_connection.BlockingChannel] = None
        self.log_file = log_file or Path(__file__).with_name('rabbitmq_default_logging.log')
        self.logger = self.setup_logger()

    def setup_logger(self):
        logger = logging.getLogger(__file__)
        handler = RotatingFileHandler(self.log_file, maxBytes=1024 * 1024 * 16, backupCount=8)
        handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(handler)
        return logger

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

    def exit_callback(self):
        self.close_connection()
        super().exit_callback()

    def on_message(self, channel, method, properties, body):
        self.logger.critical(body.decode())
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def run(self):
        self.open_connection()
        self.channel.basic_consume(self.settings.RABBITMQ_LOGGING_QUEUE,
                                   on_message_callback=self.on_message,
                                   auto_ack=False)
        self.channel.start_consuming()
        print('end')


if __name__ == '__main__':
    log_daemon = RabbitMQDiskLogConsumer()
    log_daemon.start()
