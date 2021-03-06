# rabbitmq-logging

A Python logging handler and formatter for RabbitMQ.

- minimal impact on your existing codes
- centralized logging
- support pika and HTTP handler
- could be customized on demand

# Diagram

```mermaid
flowchart LR
A[clientA]
B[clientB]
C[clientC]

subgraph RabbitMQ
exchange --> queue
end

A --> exchange
B --> exchange
C --> exchange

queue --> LogConsumer
```

# How to use?

1. install RabbitMQ (by using docker)

```shell
docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.9-management 
```

2. log something in your code, as before.

```python
import rabbitmq_logging

# get a logger, with handler and formatter
logger = rabbitmq_logging.get_logger('hello.world')

# start using logger!
logger.warning('first logging to rabbitMQ')
```

The message in the queue will looks like:

```text
2022-05-06 14:47:18,062 - ERROR - hello.world - andyguo - 192.168.0.108 - example.py - 17 : first logging to rabbitMQ
```

3. Run `RabbitMQDiskLogConsumer` as a daemon. (check
   about [daemonize](https://github.com/gxagxagxa/useful-snippets/tree/main/src/daemonlize)). Or write your own log consumer to process logs.

```python
from rabbitmq_logging.consumer.disk_consumer import RabbitMQDiskLogConsumer

consumer = RabbitMQDiskLogConsumer()
consumer.start()
```

or by shell:

```shell
$ python disk_consumer.py
```

To prevent the consumer process from going offline, you can use `cron` to start it periodically. Don't worry, if the
daemon process remains online, it will not be started twice.

# Config

All info needed are packaged into a `RabbitMQSettings` object, inherent from `pydantic.BaseSettings`. See more
from [pydantic docs](https://pydantic-docs.helpmanual.io/usage/settings/).

# Performance

It's not been benchmarked. However, from Offical HTTP API doc, `RabbitMQHTTPHandler` is not recommended for
high-throughput scenario.
> Please note that the HTTP API is not ideal for high performance publishing; the need to create a new TCP connection for each message published can limit message throughput compared to AMQP or other protocols using long-lived connections.