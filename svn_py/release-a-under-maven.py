import re
import subprocess

ENCODE = 'gbk'


def get_logs(project_path):
    cmd = f'svn log -rHEAD:0 -l 50 {project_path}'
    print(f'run: {cmd}')
    ret = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    logs = ret.decode(ENCODE).split('\r\n')
    log_contents = []
    for l in logs:
        if l.strip() == '':
            continue
        if l.startswith('-----'):
            continue
        # r95376 | hudson | 2020-08-10 15:04:13 +0800 (周一, 10 八月 2020) | 1 line
        found = re.match('r\d+ \\| [a-zA-Z]+ \\| \d{4}-\d{2}-\d{2}', l)
        if found:
            log_contents.append(found.group())
            continue
        if l.startswith('[maven-release-plugin]'):  # last maven release commit
            log_contents.pop()  # pop r95376 | hudson | 2020-08-10
            break
        log_contents.append(f'{l}')
    assert len(log_contents) % 2 == 0
    return [f'{x} | {y}' for x, y in zip(log_contents[0::2], log_contents[1::2])]


def release_prepare(logs):
    tmplt = '1、 发版内容:\n{release_logs}\n\n2、 结果验证：\n\t结果包含: '
    print(tmplt.format(release_logs='\r\n'.join(['\t{}'.format(x) for x in logs])))


if __name__ == '__main__':
    import sys

    release_prepare(get_logs(sys.argv[1]))
