import json
import os
import socket
import struct

from contextlib import contextmanager, suppress
from enum import Enum
from sys import platform
from typing import Dict, Optional as Opt, Tuple
from uuid import uuid4

from .pidlock import get_tempdir

DiscordError = type('DiscordError', (Exception,), {})
ReconnectError = type('ReconnectError', (DiscordError,), {})
NoDiscordClientError = type('NoDiscordClientError', (DiscordError,), {})


class OP(Enum):
    """API operation enum."""
    AUTHENTICATE = 0
    FRAME = 1
    CLOSE = 2

    def __int__(self) -> int:
        """Get the value of the enum."""
        return self.value


class Message:
    """API message class."""
    @staticmethod
    def authenticate(client_id: int, version: int = 1) -> Dict:
        """Create an authentication message."""
        return {'v': version, 'client_id': str(client_id)}

    @staticmethod
    def set_activity(activity: Dict, nonce: str,
                     pid: int = os.getpid()) -> Dict:
        """Create an activity message."""
        return {
            'cmd': 'SET_ACTIVITY',
            'args': {'activity': activity, 'pid': pid},
            'nonce': nonce
        }


class IPC:
    """Cross-platform IPC compatibility wrapper."""
    def __init__(self):
        self._is_windows = platform in ('win32', 'cygwin')
        self.socket = None
        if self._is_windows:
            self.path = r'\\?\pipe\discord-ipc-0'
        else:
            self.path = '{}/discord-ipc-0'.format(get_tempdir())

    def open(self):
        """Open the IPC socket."""
        if self._is_windows:
            self.socket = open(self.path, 'r+b')
        else:
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.socket.connect(self.path)

    def close(self):
        """Close the IPC socket."""
        with suppress(OSError, socket.error, BrokenPipeError):
            self.socket.close()
        self.socket = None

    def send(self, body: bytes):
        """Send data through the IPC socket."""
        if not self.socket:
            self.open()
        if self._is_windows:
            self.socket.write(body)
            self.socket.flush()
            self.close()
        else:
            self.socket.sendall(body)

    def recv(self, length: int):
        """Receive data from the IPC socket."""
        if not self.socket:
            self.open()
        if self._is_windows:
            data = self.socket.read(length)
            self.close()
            return data
        else:
            return self.socket.recv(length)


class Discord:
    def __init__(self, client_id: Opt[int] = None,
                 reconnect_threshold: int = 5):
        # Reconnect props
        self.reconnect_threshold = reconnect_threshold
        self.reconnect_counter = 0

        # Socket
        self.ipc = IPC()

        # Discord
        self.client_id = client_id

    def connect(self, client_id: Opt[int] = None):
        """Connect to the Discord socket."""
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
        """Disconnect from the Discord socket."""
        self.ipc.close()

    def send(self, op: OP, payload: Dict):
        """Send data to the Discord socket."""
        payload = json.dumps(payload).encode('utf8')
        body = struct.pack('<ii', int(op), len(payload)) + payload
        with self._reconnect_on_failure():
            self.ipc.send(body)

    def set_activity(self, activity, pid: int = os.getpid()):
        """Send the activity status to the Discord socket."""
        nonce = str(uuid4())
        self.send(OP.FRAME, Message.set_activity(activity, nonce, pid))
        op, length = self.peek()
        if not op and not length:
            # There was a successful reconnect attempt
            return self.set_activity(activity, pid)
        body = self.recv(length)
        if not body:
            return self.set_activity(activity, pid)
        assert body['cmd'] == 'SET_ACTIVITY'
        assert body['nonce'] == nonce

    def shutdown(self):
        """Close the API connection and disconnect from the socket."""
        with suppress(socket.error, OSError, BrokenPipeError):
            self.send(OP.CLOSE, {})
        self.disconnect()

    def peek(self) -> Tuple[Opt[int], Opt[int]]:
        """Receive the operation code and data length from the socket."""
        with self._reconnect_on_failure():
            return struct.unpack('<ii', self.ipc.recv(8))
        return None, None

    def recv(self, length: int) -> Opt[bytes]:
        """Receive the response body from the socket."""
        with self._reconnect_on_failure():
            body = json.loads(self.ipc.recv(length).decode('utf8'))
            if body['evt'] == 'ERROR':
                raise DiscordError(body['data']['message'])
            return body
        return None

    def handshake(self) -> Opt[bytes]:
        """Perform a handshake with the Discord API."""
        self.send(OP.AUTHENTICATE, Message.authenticate(self.client_id))
        op, length = self.peek()
        assert op == int(OP.FRAME)
        body = self.recv(length)
        assert body['evt'] == 'READY'
        return body

    def reconnect(self):
        """Reconnect to the Discord socket."""
        if self.reconnect_counter > self.reconnect_threshold:
            raise ReconnectError('reconnect_counter > reconnect_threshold')
        self.disconnect()
        self.reconnect_counter += 1
        self.connect(self.client_id)

    @contextmanager
    def _reconnect_on_failure(self):
        """Try reconnecting on failure."""
        try:
            yield
        except (socket.error, BrokenPipeError, ConnectionResetError):
            self.reconnect()


__all__ = ['ReconnectError', 'NoDiscordClientError', 'Discord']
