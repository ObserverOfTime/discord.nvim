" Stolen from https://github.com/w0rp/ale/blob/master/autoload/ale/path.vim#37
function! discord#_find_nearest_dir(buffer, dirname)
    let l:file = fnameescape(fnamemodify(bufname(a:buffer), ':p'))
    let l:path = finddir(a:dirname, l:file . ';')
    if !empty(l:path)
        return fnamemodify(l:path, ':p')
    endif
    return ''
endfunction

function! discord#_parse_vcs_info(info) abort
    let l:vcs_output = system(a:info.cmd)
    if v:shell_error | return '' | endif
    let l:parsed_name = substitute(l:vcs_output,
                \ a:info.sub[0], a:info.sub[1], '')
    return fnameescape(fnamemodify(l:parsed_name, ':t'))
endfunction

let s:project_info = {}
let s:project_info['.git'] = {
            \ 'cmd': 'git config --get remote.origin.url',
            \ 'sub': ['\(\.git\)\?\n$', '']
            \ }
let s:project_info['.svn'] = {
            \ 'cmd': 'svn info --show-item url',
            \ 'sub': ['\(\.svn\)\?\n*$', '']
            \ }
let s:project_info['.hg'] = {
            \ 'cmd': 'hg path default',
            \ 'sub': ['\(\.hg\)\?\n$', '']
            \ }
let s:project_info['.bzr'] = {
            \ 'cmd': 'bzr info',
            \ 'sub': ['.*parent branch: \(.*\)/.*/.*\n', '\1']
            \ }
let s:project_info['_darcs'] = {
            \ 'cmd': 'darcs show repo --no-enum-patches '.
            \        '--no-posthook --no-prehook --no-cache',
            \ 'sub': ['.*Default Remote: \(.*\)\n', '\1']
            \ }

function! discord#get_workspace(buffer)
    if !empty(get(g:, 'discord_workspace'))
        return g:discord_workspace
    endif
    for l:vcs_dir in g:discord_vcs_dirs
        let l:dir = discord#_find_nearest_dir(a:buffer, l:vcs_dir)
        if !empty(l:dir)
            let l:info = s:project_info[l:vcs_dir]
            let l:name = discord#_parse_vcs_info(l:info)
            if !empty(l:name)
                return l:name
            else
                return fnamemodify(l:dir, ':h:h')
            endif
        endif
    endfor
    return ''
endfunction

function! discord#log_debug(message)
    if g:discord_log_debug
        echomsg '[Discord] ' . a:message
    endif
endfunction

function! discord#log_warn(message)
    echohl WarningMsg | echomsg '[Discord] ' . a:message | echohl None
endfunction

function! discord#log_error(message)
    echohl ErrorMsg | echomsg '[Discord] ' . a:message | echohl None
endfunction
