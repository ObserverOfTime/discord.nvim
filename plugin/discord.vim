if !has('nvim')
    echoerr 'This plugin requires Neovim'
    finish
endif

if !has('timers')
    echoerr 'This plugin requires +timers build option'
    finish
endif

if !has('python3')
    echoerr 'This plugin requires python3'
    finish
endif

if !exists('g:discord_activate_on_enter')
    let g:discord_activate_on_enter = 1
endif

if !exists('g:discord_rich_presence')
    let g:discord_rich_presence = 1
endif

if !exists('g:discord_reconnect_threshold')
    let g:discord_reconnect_threshold = 5
endif

if !exists('g:discord_log_debug')
    let g:discord_log_debug = 0
endif

if !exists('g:discord_blacklist')
    let g:discord_blacklist = []
endif

if !exists('g:_discord_trace')
    let g:_discord_trace = []
endif

if !exists('g:discord_fts_blacklist')
    let g:discord_fts_blacklist = [
                \ 'ale-preview',
                \ 'connvorax',
                \ 'deol',
                \ 'fzf',
                \ 'gitcommit',
                \ 'help',
                \ 'mail',
                \ 'netrw',
                \ 'nerdtree',
                \ 'pydoc',
                \ 'outputvorax',
                \ 'qf',
                \ 'scratch',
                \ 'tagbar',
                \ 'vim-plug',
                \ 'vimfiler',
                \ 'vimshell'
                \ ]
endif

if !exists('g:discord_fts_aliases')
    let g:discord_fts_aliases = {}
endif
let g:discord_fts_aliases['asp'] = 'dotnet'
let g:discord_fts_aliases['aspvbs'] = 'dotnet'
let g:discord_fts_aliases['awk'] = 'sh'
let g:discord_fts_aliases['bib'] = 'tex'
let g:discord_fts_aliases['cfg'] = 'config'
let g:discord_fts_aliases['conf'] = 'config'
let g:discord_fts_aliases['delphi'] = 'pascal'
let g:discord_fts_aliases['dosini'] = 'config'
let g:discord_fts_aliases['fasm'] = 'asm'
let g:discord_fts_aliases['fish'] = 'sh'
let g:discord_fts_aliases['htmldjango'] = 'django'
let g:discord_fts_aliases['html.mustache'] = 'mustache'
let g:discord_fts_aliases['html.twig'] = 'twig'
let g:discord_fts_aliases['javascript.jsx'] = 'jsx'
let g:discord_fts_aliases['jproperties'] = 'config'
let g:discord_fts_aliases['json5'] = 'json'
let g:discord_fts_aliases['mips'] = 'asm'
let g:discord_fts_aliases['nasm'] = 'asm'
let g:discord_fts_aliases['plaintex'] = 'tex'
let g:discord_fts_aliases['qbs'] = 'qt'
let g:discord_fts_aliases['qmake'] = 'qt'
let g:discord_fts_aliases['qml'] = 'qt'
let g:discord_fts_aliases['scss'] = 'sass'
let g:discord_fts_aliases['sed'] = 'sh'
let g:discord_fts_aliases['vb'] = 'dotnet'
let g:discord_fts_aliases['vbnet'] = 'dotnet'
let g:discord_fts_aliases['zsh'] = 'sh'

