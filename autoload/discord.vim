" Stolen from https://github.com/w0rp/ale/blob/master/autoload/ale/path.vim#L46
function! discord#find_nearest_dir(buffer, directory_name)
  let l:buffer_filename = fnamemodify(bufname(a:buffer), ':p')

  let l:relative_path = finddir(a:directory_name, l:buffer_filename . ';')

  if !empty(l:relative_path)
    return fnamemodify(l:relative_path, ':p')
  endif

  return ''
endfunction

function! discord#get_project_dir(buffer)
  for l:vcs_dir in ['.git', '.hg', '.bzr', '_darcs', '.svn']
    let l:dir = discord#find_nearest_dir(a:buffer, l:vcs_dir)
    if !empty(l:dir)
      return fnamemodify(l:dir, ':h:h')
    endif
  endfor
  return ''
endfunction

function! discord#log_debug(message, trace)
  call add(g:discord_trace, a:trace)
  if g:discord_log_debug
    echomsg '[Discord] ' . a:message
  endif
endfunction

function! discord#log_warn(message, trace)
  call add(g:discord_trace, a:trace)
  echohl WarningMsg | echomsg '[Discord] ' . a:message | echohl None
endfunction

function! discord#log_error(message, trace)
  call add(g:discord_trace, a:trace)
  echohl ErrorMsg | echomsg '[Discord] ' . a:message | echohl None
endfunction

" vim:set et sw=2 ts=2:

