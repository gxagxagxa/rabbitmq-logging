from typing import Literal


def get_logger(name='', settings=None, handler_type: Literal['pika', 'http'] = 'pika'):
    import logging
    from rabbitmq_logging.adapter import RabbitMQLoggingExtra
    from rabbitmq_logging.formatter import RabbitMQLoggingDefaultFormatter

    logger = logging.getLogger(name)
    if handler_type == 'pika':
        from rabbitmq_logging.handler.rabbitmq_handler.rabbitmq_pika_handler import RabbitMQPikaHandler
        handler = RabbitMQPikaHandler(settings=settings)
    if handler_type == 'http':
        from rabbitmq_logging.handler.rabbitmq_handler.rabbitmq_http_handler import RabbitMQHttpHandler
        handler = RabbitMQHttpHandler(settings=settings)

    handler.setFormatter(RabbitMQLoggingDefaultFormatter())
    logger.addHandler(handler)
    return logging.LoggerAdapter(logger, RabbitMQLoggingExtra)
