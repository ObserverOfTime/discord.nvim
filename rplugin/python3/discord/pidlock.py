import os


def get_tempdir():
    temp = ['TMPDIR', 'TEMPDIR', 'TMP', 'TEMP']
    return next((os.environ.get(path, None)
                 for path in temp if path
                 in os.environ), '/tmp')


class PidLock(object):
    def __init__(self, path):
        self.path = path

    def lock(self):
        if not self.unlock():
            return False
        with open(self.path, 'w') as f:
            f.write(str(os.getpid()))
        return True

    def unlock(self):
        if os.path.exists(self.path):
            with open(self.path, 'r') as f:
                pid = int(f.read())
                if pid and pid != os.getpid():
                    try:
                        os.kill(pid, 0)
                        return False
                    except OSError:
                        pass
            os.remove(self.path)
        return True

# vim:set et sw=4 ts=4:

