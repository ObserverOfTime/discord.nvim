import os


def get_tempdir() -> str:
    """Get the directory where temporary files are stored."""
    return next((os.environ[var] for var in (
        'XDG_RUNTIME_DIR', 'TMPDIR', 'TMP', 'TEMP'
    ) if var in os.environ), '/tmp')


class PidLock:
    """PID lock handler class."""
    def __init__(self, name: str):
        self.path = os.path.join(get_tempdir(), name + '.pid')

    def lock(self):
        """Create the pidfile."""
        with open(self.path, 'w') as f:
            f.write(str(os.getpid()))

    def unlock(self):
        """Remove the pidfile."""
        with open(self.path, 'r') as f:
            os.unlink(self.path)
            pid = int(f.read())
            if pid and pid != os.getpid():
                os.kill(pid, 0)
