from enum import Enum


class RabbitMQLoggingFormatEnum(Enum):
    DEFAULT_FORMAT = '%(asctime)s - %(levelname)s - %(name)s - %(username)s - %(ip)s - %(filename)s - %(lineno)d : %(message)s'
