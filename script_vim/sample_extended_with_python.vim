" This script is useful when you handle multiple lines of a text file with complex logic.
" Usage: Add your own handle lines in #TODO block 
" 1. :source sample_extended_with_python.vim
"
" 2. :call LinesHandle()
" OR 
" 2. :py handle_lines()
" 
" 
" ALSO SEE :help python 
"
" ! Make sure your vim compiled with python supportted.
"

function! LinesHandle()
python << EOF


import vim

def handle_lines():
    b = vim.current.buffer
    lines = [line for line in b]
    hd_lines = []
    for line in lines:
        # TODO: your own handle lines
        hd_lines.append(line.upper())

    b[:] = hd_lines
    return hd_lines

handle_lines()

EOF
endfunction

