from atexit import register
from contextlib import contextmanager
from os.path import basename, join
from re import compile as regex
from time import time
from typing import Any, List, Optional as Opt

import neovim as nvim

from .constants import CLIENT_ID, SPECIAL_FTS, SUPPORTED_FTS
from .discord_rpc import Discord, NoDiscordClientError, ReconnectError
from .pidlock import PidLock


@nvim.plugin
class DiscordPlugin:
    """The Discord plugin class."""
    def __init__(self, vim: nvim.Nvim):
        self._vim = vim
        self.discord = None
        self.activate = 0
        self.rich_presence = 1
        self.blacklist = []
        self.fts_blacklist = []
        self.fts_aliases = {}
        self._ft_cache = {}
        self.activity = {'assets': {}}
        self.lock = PidLock('dnvim')
        self.is_locked = False
        self.con_timer = None
        self.last_file = None
        self.last_used = False
        self.last_time = time()
        register(self.shutdown)

    def __call__(self, func: str, *args) -> Any:
        """Call a vimscript function."""
        return self._vim.call(func, *args)

    def __getitem__(self, var: str) -> Any:
        """Get the value of a vim variable."""
        if var[:1] != '&':
            return self._vim.vars.get(var)
        return self('getbufvar', self.bufnr, var)

    @nvim.autocmd('VimEnter', pattern='*', sync=True)
    def on_vimenter(self):
        """Handle the VimEnter autocmd."""
        self.blacklist = list(map(regex, self['discord_blacklist']))
        self.activate = self['discord_activate_on_enter']
        self.rich_presence = self['discord_rich_presence']
        self.fts_blacklist = self['discord_fts_blacklist']
        self.fts_aliases = self['discord_fts_aliases']

    @nvim.autocmd('BufEnter', pattern='*', sync=True)
    def on_bufenter(self, *args):
        """Handle the BufEnter autocmd."""
        if self.activate:
            self.update_presence()

    @nvim.command('DiscordUpdatePresence', bang=True)
    def update_presence(self, bang: bool = False):
        """Handle the DiscordUpdatePresence command."""
        if not self.activate:
            self.activate = 1
        self.activity['assets'] = {
            'small_image': 'neovim',
            'small_text': 'Neovim FTW'
        }
        self.activity.setdefault('timestamps', {'start': int(time())})
        if self.is_locked:
            return
        if not self.discord:
            reconnect_threshold = self['discord_reconnect_threshold']
            try:
                self.lock.lock()
            except (OSError, ValueError) as e:
                self.log_error(str(e))
                return
            self.discord = Discord(CLIENT_ID, reconnect_threshold)
            with self._handle_lock():
                self.discord.connect()
                self.log_debug('Init')
            if self.is_locked:
                return
        if self['&readonly']:
            return
        if not self.rich_presence:
            self.activity['assets'] = {
                'large_image': 'neovim',
                'large_text': 'The one true editor'
            }
            self.discord.set_activity(self.activity, self('getpid'))
            return
        filename = self.filename
        if not filename:
            return
        self.log_debug('filename: {}'.format(filename))
        if any(f.match(filename) for f in self.blacklist):
            return
        fn = basename(filename)
        ft = self.get_filetype(fn)
        if not ft:
            return
        self.log_debug('ft: {}'.format(ft))
        if ft in self.fts_blacklist:
            return
        if ft not in SUPPORTED_FTS:
            ft = 'unknown'
        workspace = self.workspace
        if not bang and self.is_ratelimited():
            if self.con_timer:
                self('timer_stop', self.con_timer)
            self.con_timer = self('timer_start', 15, '_DiscordRunScheduled')
            return
        self.log_debug('Update presence')
        with self._handle_lock():
            if ft:
                text = 'Filetype: {}'.format(ft.upper())
                image = ft if len(ft) > 1 else ft + 'lang'
                self.activity['assets']['large_image'] = image
                self.activity['assets']['large_text'] = text
                self.activity['details'] = 'Editing {}'.format(fn)
            if workspace:
                self.activity['state'] = 'Working on {}'.format(workspace)
            self.discord.set_activity(self.activity, self('getpid'))

    @nvim.command('DiscordListFiletypes', '?')
    def list_filetypes(self, args: List[str]):
        """Handle the DiscordListFiletypes command."""
        if len(args) > 0:
            pat = regex('.*{}.*'.format(args[0]))
            fts = filter(pat.match, SUPPORTED_FTS)
            self._vim.command('echo {}'.format(list(fts)))
        else:
            self._vim.command('echo {}'.format(SUPPORTED_FTS))

    @nvim.command('DiscordClearCache')
    def clear_cache(self, args):
        """Handle the DiscordClearCache command."""
        self._ft_cache.clear()

    @nvim.function('_DiscordRunScheduled')
    def run_scheduled(self, args: List[int]):
        """Handle the _DiscordRunScheduled function."""
        self.con_timer = None
        self.update_presence()

    @property
    def filename(self) -> str:
        """Get the current filename."""
        return self._vim.current.buffer.name

    @property
    def bufnr(self) -> int:
        """Get the current buffer number."""
        return self._vim.current.buffer.number

    @property
    def workspace(self) -> Opt[str]:
        """Get the current workspace."""
        dirpath = self('discord#get_workspace', self.bufnr)
        return basename(dirpath) if dirpath else None

    @property
    def filetype(self) -> str:
        """Get the current filetype."""
        ft = self['&filetype']
        return self.fts_aliases.get(ft, ft)

    def get_filetype(self, var: str) -> str:
        """Get the filetype, taking special files into account."""
        if var not in self._ft_cache:
            self._ft_cache[var] = next((
                k for k, v in SPECIAL_FTS.items() if bool(v.match(var))
            ), self.filetype)
        return self._ft_cache[var]

    def is_ratelimited(self) -> bool:
        """Check whether we're being rate-limited."""
        filename = self.filename
        if self.last_file == filename:
            return True
        now = time()
        if now - self.last_time >= 15:
            self.last_used = False
            self.last_time = now
        if self.last_used:
            return True
        self.last_used = True
        self.last_file = filename
        return False

    def log_debug(self, message: str):
        """Log a debug message."""
        self('discord#log_debug', message)

    def log_warn(self, message: str):
        """Log a warning message."""
        self('discord#log_warn', message)

    def log_error(self, message: str):
        """Log an error message."""
        self('discord#log_error', message)

    def shutdown(self):
        """Shut everything down."""
        try:
            self.lock.unlock()
        except (OSError, ValueError) as e:
            self.log_warn(str(e))
        if self.con_timer:
            self('timer_stop', self.con_timer)
        if self.discord:
            self.discord.shutdown()

    @contextmanager
    def _handle_lock(self):
        """Handle the plugin lock."""
        try:
            yield
        except NoDiscordClientError:
            self.is_locked = True
            self.log_warn('Local Discord client not found')
        except ReconnectError:
            self.is_locked = True
            self.log_error('Ran out of reconnect attempts')


__all__ = ['DiscordPlugin']
