import os

_temp = ('XDG_RUNTIME_DIR', 'TEMP', 'TMPDIR', 'TEMPDIR', 'TMP')


def get_tempdir() -> str:
    """Get the directory where temporary files are stored."""
    return next((os.environ.get(path) for path
                 in _temp if path in os.environ), '/tmp')


class PidLock:
    """PID lock handler class."""
    def __init__(self, name: str):
        self.path = os.path.join(get_tempdir(), name + '.pid')

    def lock(self):
        """Create the pidfile."""
        self.unlock()
        with open(self.path, 'w') as f:
            f.write(str(os.getpid()))

    def unlock(self):
        """Remove the pidfile."""
        if os.path.exists(self.path):
            with open(self.path, 'r') as f:
                pid = int(f.read())
                if pid and pid != os.getpid():
                    os.kill(pid, 0)
                    raise OSError(17, 'Pidfile exists', self.path)
            os.remove(self.path)
