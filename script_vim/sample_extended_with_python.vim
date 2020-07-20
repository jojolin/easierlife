function! LinesHandle()
python << EOF

## SEE :help python 

import vim

def handle_lines():
    b = vim.current.buffer
    lines = [line for line in b]
    hd_lines = []
    for line in lines:
        # TODO: handle line
        hd_lines.append(line.upper())

    b[:] = hd_lines
    return hd_lines

handle_lines()

EOF
endfunction

