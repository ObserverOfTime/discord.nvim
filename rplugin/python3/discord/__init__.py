import neovim
import re

from contextlib import contextmanager
from os.path import basename, join
from atexit import register
from time import time
from .discord_rpc import Discord, NoDiscordClientError, ReconnectError
from .pidlock import PidLock, get_tempdir
from .constants import CLIENT_ID, SPECIAL_FTS, SUPPORTED_FTS


@contextmanager
def handle_lock(plugin):
    try:
        yield
    except NoDiscordClientError:
        plugin.locked = True
        plugin.log_warning('Local Discord client not found')
    except ReconnectError:
        plugin.locked = True
        plugin.log_error('Ran out of reconnect attempts')


@neovim.plugin
class DiscordPlugin(object):
    def __init__(self, vim):
        self.vim = vim
        self.discord = None
        self.activate = 0
        self.rich_presence = 1
        self.blacklist = []
        self.fts_blacklist = []
        self.fts_aliases = {}
        self.activity = {'assets': {}}
        # Ratelimits
        self.lock = None
        self.locked = False
        self.lastfilename = None
        self.lastused = False
        self.lasttimestamp = time()
        self.cbtimer = None

    @neovim.autocmd('VimEnter', '*')
    def on_vimenter(self):
        self.blacklist = [
            re.compile(x) for x in self.vim.vars.get('discord_blacklist')
        ]
        self.activate = self.vim.vars.get('discord_activate_on_enter')
        self.rich_presence = self.vim.vars.get('discord_rich_presence')
        self.fts_blacklist = self.vim.vars.get('discord_fts_blacklist')
        self.fts_aliases = self.vim.vars.get('discord_fts_aliases')

    @neovim.autocmd('BufEnter', '*')
    def on_bufenter(self):
        if self.activate:
            self.update_presence()

    @neovim.command('DiscordUpdatePresence', bang=True)
    def update_presence(self, bang=False):
        if not self.activate:
            self.activate = 1
        self.activity['assets'] = {
            'small_image': 'neovim',
            'small_text': 'Neovim FTW'
        }
        self.activity.setdefault('timestamps', {'start': int(time())})
        if not self.lock:
            self.lock = PidLock(join(get_tempdir(), 'dnvim_lock'))
        if self.locked:
            return
        if not self.discord:
            reconnect_threshold = \
                self.vim.vars.get('discord_reconnect_threshold')
            self.locked = not self.lock.lock()
            if self.locked:
                self.log_warning('Pidfile exists')
                return
            self.discord = Discord(CLIENT_ID, reconnect_threshold)
            with handle_lock(self):
                self.discord.connect()
                self.log_debug('Init')
            if self.locked:
                return
            register(self.shutdown)
        if self.get_current_buf_var('&ro'):
            return
        if not self.rich_presence:
            self.activity['assets'] = {
                'large_image': 'neovim',
                'large_text': 'The one true editor'
            }
            self.discord.set_activity(self.activity,
                                      self.vim.call('getpid'))
            return
        filename = self.vim.current.buffer.name
        if not filename:
            return
        self.log_debug('filename: %s' % filename)
        if any(f.match(filename) for f in self.blacklist):
            return
        fn = basename(filename)
        ft = self.check_special_fts(fn) or self.get_filetype()
        if not ft:
            return
        self.log_debug('ft: %s' % ft)
        if ft in self.fts_blacklist:
            return
        if ft not in SUPPORTED_FTS:
            ft = 'unknown'
        workspace = self.get_workspace()
        if not bang and self.is_ratelimited(filename):
            if self.cbtimer:
                self.vim.call('timer_stop', self.cbtimer)
            self.cbtimer = self.vim.call('timer_start', 15,
                                         '_DiscordRunScheduled')
            return
        self.log_debug('Update presence')
        with handle_lock(self):
            self._update_presence(filename, ft, workspace)

    def _update_presence(self, filename, ft, workspace=None):
        if ft:
            text = 'Filetype: %s' % ft.upper()
            image = ft if len(ft) > 1 else ft + 'lang'
            self.activity['assets']['large_image'] = image
            self.activity['assets']['large_text'] = text
            self.activity['details'] = 'Editing %s' % basename(filename)
        if workspace:
            self.activity['state'] = 'Working on %s' % workspace
        self.discord.set_activity(self.activity, self.vim.call('getpid'))

    def get_current_buf_var(self, var):
        return self.vim.call('getbufvar', self.vim.current.buffer.number, var)

    def get_filetype(self):
        ft = self.get_current_buf_var('&ft')
        return self.fts_aliases.get(ft, ft)

    def get_workspace(self):
        bufnr = self.vim.current.buffer.number
        dirpath = self.vim.call('discord#get_workspace', bufnr)
        return (basename(dirpath) if dirpath else None)

    def check_special_fts(self, var):
        return next((k for k, v in SPECIAL_FTS.items()
                     if bool(v.fullmatch(var))), None)

    @neovim.command('DiscordListFiletypes', '?')
    def list_filetypes(self, args):
        a = args[0] if len(args) > 0 else ''
        fts = list(filter(re.compile(a).match, SUPPORTED_FTS))
        self.vim.command('echo %s' % fts)

    @neovim.function('_DiscordRunScheduled')
    def run_scheduled(self, args):
        self.cbtimer = None
        self.update_presence()

    def is_ratelimited(self, filename):
        if self.lastfilename == filename:
            return True
        now = time()
        if (now - self.lasttimestamp) >= 15:
            self.lastused = False
            self.lasttimestamp = now
        if self.lastused:
            return True
        self.lastused = True
        self.lastfilename = filename

    def log_debug(self, message, trace=None):
        self.vim.call('discord#log_debug', message, trace)

    def log_warning(self, message, trace=None):
        self.vim.call('discord#log_warn', message, trace)

    def log_error(self, message, trace=None):
        self.vim.call('discord#log_error', message, trace)

    def shutdown(self):
        if self.lock:
            self.lock.unlock()
        if self.cbtimer:
            self.vim.call('timer_stop', self.cbtimer)
        if self.discord:
            self.discord.shutdown()

