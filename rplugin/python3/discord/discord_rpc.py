import json
import os
import socket
import struct

from contextlib import contextmanager, suppress
from enum import Enum
from sys import platform
from uuid import uuid4

from .pidlock import get_tempdir


@contextmanager
def reconnect_on_failure(discord):
    try:
        yield
    except (socket.error, BrokenPipeError, ConnectionResetError):
        discord.reconnect()


class OP(Enum):
    AUTHENTICATE = 0
    FRAME = 1
    CLOSE = 2

    def __int__(self):
        return self.value


class Message:
    @staticmethod
    def authenticate(client_id, version=1):
        return {'v': version, 'client_id': client_id}

    @staticmethod
    def set_activity(activity, nonce, pid=os.getpid()):
        return {
            'cmd': 'SET_ACTIVITY',
            'args': {'activity': activity, 'pid': pid},
            'nonce': nonce
        }


class DiscordError(Exception):
    pass


class NoDiscordClientError(DiscordError):
    pass


class ReconnectError(DiscordError):
    pass


class IPC(object):
    _is_windows = platform in ('win32', 'cygwin')

    def __init__(self):
        self.socket = None
        if self._is_windows:
            self.path = r'\\?\pipe\discord-ipc-0'
        else:
            self.path = '{}/discord-ipc-0'.format(get_tempdir())

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def open(self):
        if self._is_windows:
            self.socket = open(self.path, 'r+b')
        else:
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.socket.connect(self.path)

    def close(self):
        with suppress(OSError, socket.error, BrokenPipeError):
            self.socket.close()
        self.socket = None

    def send(self, body):
        if self._is_windows:
            self.socket.write(body)
            self.socket.flush()
        else:
            self.socket.sendall(body)

    def recv(self, length):
        if self._is_windows:
            return self.socket.read(length)
        else:
            return self.socket.recv(length)


class Discord(object):
    def __init__(self, client_id=None, reconnect_threshold=5):
        # Reconnect props
        self.reconnect_threshold = reconnect_threshold
        self.reconnect_counter = 0

        # Socket
        self.ipc = IPC()

        # Discord
        self.client_id = client_id

    def connect(self, client_id=None):
        try:
            os.stat(self.ipc.path)
        except FileNotFoundError:
            raise NoDiscordClientError()
        self.client_id = self.client_id or client_id
        try:
            self.ipc.open()
        except (OSError, ConnectionAbortedError, ConnectionRefusedError):
            raise NoDiscordClientError()
        self.handshake()

    def disconnect(self):
        self.ipc.close()

    def send(self, op, payload):
        payload = json.dumps(payload).encode('utf8')
        body = struct.pack('<ii', int(op), len(payload)) + payload
        with reconnect_on_failure(self):
            self.ipc.send(body)
        return None

    def set_activity(self, activity, pid=os.getpid()):
        nonce = str(uuid4())
        self.send(OP.FRAME, Message.set_activity(activity, nonce, pid))
        op, length = self.recv()
        if not op and not length:
            # There was a successful reconnect attempt
            return self.set_activity(activity, pid)
        body = self.recv_body(length)
        if not body:
            return self.set_activity(activity, pid)
        assert body['cmd'] == 'SET_ACTIVITY'
        assert body['nonce'] == nonce

    def shutdown(self):
        with suppress(socket.error, OSError, BrokenPipeError):
            self.send(OP.CLOSE, {})
        self.disconnect()

    def recv(self):
        with reconnect_on_failure(self):
            return struct.unpack('<ii', self.ipc.recv(8))
        return (None, None)

    def recv_body(self, length):
        with reconnect_on_failure(self):
            body = json.loads(self.ipc.recv(length).decode('utf8'))
            if body['evt'] == 'ERROR':
                raise DiscordError(body['data']['message'])
            return body
        return None

    def handshake(self):
        self.send(OP.AUTHENTICATE, Message.authenticate(str(self.client_id)))
        op, length = self.recv()
        assert op == OP.FRAME.value
        body = self.recv_body(length)
        assert body['evt'] == 'READY'
        return body

    def reconnect(self):
        if self.reconnect_counter > self.reconnect_threshold:
            raise ReconnectError('reconnect_counter > reconnect_threshold')
        self.disconnect()
        self.reconnect_counter += 1
        self.connect(self.client_id)
