import getpass
import socket

RabbitMQLoggingExtra = {'username': getpass.getuser(),
                        'ip': socket.gethostbyname(socket.gethostname())}
