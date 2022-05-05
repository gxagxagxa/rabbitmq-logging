import logging

from rabbitmq_logging.formatter.enums import RabbitMQLoggingFormatEnum


class RabbitMQLoggingDefaultFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%', validate=True) -> None:
        self.fmt = fmt or RabbitMQLoggingFormatEnum.DEFAULT_FORMAT.value
        super().__init__(self.fmt, datefmt, style, validate)
