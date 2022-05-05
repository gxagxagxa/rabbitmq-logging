from typing import Optional, Union, Literal, Any

from pydantic import BaseSettings, NonNegativeInt, PositiveInt, SecretStr


class RabbitMQSettings(BaseSettings):
    # from rabbitmq config file, and pika.ConnectionParameter class
    RABBITMQ_HOST: Optional[str] = '127.0.0.1'
    RABBITMQ_PORT: Optional[PositiveInt] = 5672
    RABBITMQ_VIRTUAL_HOST: Optional[str] = '/'
    RABBITMQ_USERNAME: Optional[str] = 'guest'
    RABBITMQ_PASSWORD: Optional[SecretStr] = 'guest'
    RABBITMQ_CHANNEL_MAX: Optional[PositiveInt] = 2047
    RABBITMQ_FRAME_MAX: Optional[PositiveInt] = 131072
    RABBITMQ_HEARTBEAT: Optional[NonNegativeInt] = 60
    RABBITMQ_SSL_OPTIONS: Optional[Any]
    RABBITMQ_CONNECTION_ATTEMPTS: Optional[NonNegativeInt]
    RABBITMQ_RETRY_DELAY: Optional[NonNegativeInt]
    RABBITMQ_SOCKET_TIMEOUT: Optional[NonNegativeInt]
    RABBITMQ_STACK_TIMEOUT: Optional[NonNegativeInt]
    RABBITMQ_LOCALE: Optional[str] = 'en_US'
    RABBITMQ_BLOCKED_CONNECTION_TIMEOUT: Optional[NonNegativeInt]
    RABBITMQ_CLIENT_PROPERTIES: Optional[Any]
    RABBITMQ_TCP_OPTIONS: Optional[Any]

    # rabbitmq handler package
    RABBITMQ_LOGGING_EXCHANGE: Optional[str] = 'default_rabbitmq_logging_exchange'
    RABBITMQ_LOGGING_QUEUE: Optional[str] = 'default_rabbitmq_logging_queue'
    RABBITMQ_LOGGING_ROUTER_KEY: Optional[str] = 'default_rabbitmq_logging'

    # from rabbitmq docs
    RABBITMQ_NODE_IP_ADDRESS: Optional[str] = ''
    RABBITMQ_NODE_PORT: Optional[PositiveInt] = 5672
    RABBITMQ_DIST_PORT: Optional[PositiveInt] = RABBITMQ_NODE_PORT + 2000
    ERL_EPMD_ADDRESS: Optional[str]
    ERL_EPMD_PORT: Optional[PositiveInt] = 4369
    RABBITMQ_DISTRIBUTION_BUFFER_SIZE: Optional[PositiveInt] = 128000
    RABBITMQ_NODENAME: Optional[str]
    RABBITMQ_CONFIG_FILE: Optional[str]
    RABBITMQ_CONFIG_FILES: Optional[str]
    RABBITMQ_ADVANCED_CONFIG_FILE: Optional[str]
    RABBITMQ_CONF_ENV_FILE: Optional[str]
    RABBITMQ_MNESIA_BASE: Optional[str]
    RABBITMQ_MNESIA_DIR: Optional[str]
    RABBITMQ_PLUGINS_DIR: Optional[Union[list, str]]
    RABBITMQ_PLUGINS_EXPAND_DIR: Optional[str]
    RABBITMQ_USE_LONGNAME: bool = False
    RABBITMQ_SERVICENAME: Optional[str] = 'RabbitMQ'
    RABBITMQ_CONSOLE_LOG: Optional[Literal['new', 'reuse']]
    RABBITMQ_SERVER_CODE_PATH: Optional[str]
    RABBITMQ_CTL_ERL_ARGS: Optional[Any]
    RABBITMQ_SERVER_ERL_ARGS: Optional[Any]
    RABBITMQ_SERVER_ADDITIONAL_ERL_ARGS: Optional[Any]
    RABBITMQ_SERVER_START_ARGS: Optional[str]
    RABBITMQ_DEFAULT_USER: Optional[str]
    RABBITMQ_DEFAULT_PASS: Optional[str]
    RABBITMQ_DEFAULT_VHOST: Optional[str]
    HOSTNAME: Optional[str]
    # only available in windows
    COMPUTERNAME: Optional[str]
    ERLANG_SERVICE_MANAGER_PATH: Optional[str]
    # find in docker container inspect
    RABBITMQ_DATA_DIR: Optional[str]
    RABBITMQ_VERSION: Optional[str]
    RABBITMQ_PGP_KEY_ID: Optional[SecretStr]
    RABBITMQ_HOME: Optional[str]
