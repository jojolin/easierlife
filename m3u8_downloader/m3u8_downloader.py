#

import hashlib
import os
import os.path
import sys

import requests


def download(url):
    md5 = hashlib.md5()
    md5.update(url.encode('utf8'))
    dir = md5.hexdigest()
    if not os.path.exists(dir):
        os.mkdir(dir)
        print(f'mkdir: {dir}')

    print(f'downloaded {url}')
    m3u8_head = url[: url.rfind('/')]
    resp = requests.get(url, verify=False)
    m3u8_data = resp.text
    lines = m3u8_data.split('\n')
    m3u8_ts_lines = []
    for line in [x.strip() for x in lines]:
        if line.startswith('#EXT') or not line.endswith('.ts'):
            continue
        m3u8_ts_lines.append(line)
    with open(os.path.join(dir, 'video.m3u8'), 'w', encoding='utf8') as w:
        w.write(f'#URL: {url}\n')
        for l in m3u8_ts_lines:
            w.write(f'{l}\n')
        print('save m3u8 lines to video.m3u8')

    for line in m3u8_ts_lines:
        try:
            save_fp = os.path.join(dir, line)
            if os.path.exists(save_fp):
                print(f"{line} already downloaded")
                continue
            ts_url = m3u8_head + '/' + line
            print(f'downloading {ts_url}')
            ts_resp = requests.get(ts_url, timeout=60, verify=False)
            with open(save_fp, 'wb') as w:
                w.write(ts_resp.content)
            print(f'downloaded {ts_url}')
        except:
            print(f'download failed: {line}, skip')

    print("start to merge m3u8")
    merge(dir)


def merge(dir):
    merge_fp = dir + '.ts'
    merge_fo = open(merge_fp, 'wb')
    with open(os.path.join(dir, 'video.m3u8'), 'r', encoding='utf8') as r:
        ts_names = [x.strip() for x in r.readlines() if not x.startswith('#')]

    for name in ts_names:
        fp = os.path.join(dir, name)
        if not os.path.exists(fp):
            continue
        with open(fp, 'rb') as r:
            merge_fo.write(r.read())
            print(f'merge {name}')
    merge_fo.close()
    print(f'save merge ts to {merge_fp}')


if __name__ == '__main__':
    mode = sys.argv[1]
    arg = sys.argv[2]
    if mode == 'download':
        url = arg
        download(url)
    else:
        dir = arg
        merge(dir)
