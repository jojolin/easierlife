import hashlib
import os
import os.path
import sys
import hashlib
import re
import requests

# TODO: 添加请求的headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
}


def parse_ts_key(line):
    '#EXT-X-KEY:METHOD=AES-128,URI="https://...",IV=0x00000000000000000000000000000000'
    found = re.search('#EXT-X-KEY:METHOD=AES-128,URI="(.*)",IV=(.*)', line)
    if found:
        key_url = found.group(1)
        IV = found.group(2)
        if IV.startswith('0x'):
            bIV = bytes.fromhex(IV[2:])
            return key_url, bIV
        else:
            print('Attention! IV not parsed')
    return found


def download(url):
    md5 = hashlib.md5()
    md5.update(url.encode('utf8'))
    dir = md5.hexdigest()
    if not os.path.exists(dir):
        os.mkdir(dir)
        print(f'mkdir: {dir}')

    print(f'downloaded {url}')
    m3u8_head = url[: url.rfind('/')]
    resp = requests.get(url, headers=headers, verify=False)
    # resp = requests.get(url, verify=False)
    m3u8_data = resp.text
    lines = m3u8_data.split('\n')
    m3u8_ts_lines = [x.strip() for x in lines]
    key_url, bIV = None, None
    with open(os.path.join(dir, 'video.m3u8'), 'w', encoding='utf8') as w:
        w.write(f'#URL: {url}\n')
        for l in m3u8_ts_lines:
            w.write(f'{l}\n')
            if not key_url:
                may_has_key = parse_ts_key(l)
                if may_has_key:
                    key_url, bIV = may_has_key
    if key_url:
        key_resp = requests.get(key_url)
        with open(os.path.join(dir, 'video.key'), 'wb') as w:
            w.write(key_resp.content)
        with open(os.path.join(dir, 'video.key.IV'), 'wb') as w:
            w.write(bIV)
        print(f'save {dir}/video.key,video.key.IV')

    print(f'save m3u8 lines to {dir}/video.m3u8')

    for line in m3u8_ts_lines:
        try:
            if line.startswith('#') or not line.find('.ts') > -1:
                continue

            md5 = hashlib.md5()
            md5.update(line.encode('utf-8'))
            save_name = md5.hexdigest()
            save_fp = os.path.join(dir, save_name)
            if os.path.exists(save_fp):
                print(f"{line} already downloaded")
                continue
            ts_url = (m3u8_head + '/' + line) if not line.startswith('http') else line
            print(f'downloading {ts_url}')
            ts_resp = requests.get(ts_url, headers=headers, timeout=60, verify=False)
            with open(save_fp, 'wb') as w:
                w.write(ts_resp.content)
            print(f'downloaded {ts_url}')
        except Exception as ex:
            print(ex)
            print(f'download failed: {line}, skip')

    print("start to merge m3u8")
    merge(dir)


def merge(dir):
    merge_fp = dir + '.ts'
    merge_fo = open(merge_fp, 'wb')
    with open(os.path.join(dir, 'video.m3u8'), 'r', encoding='utf8') as r:
        ts_names = [x.strip() for x in r.readlines() if not x.startswith('#')]

    aes, key, bIV = None, None, None
    if os.path.exists(os.path.join(dir, 'video.key')):
        with open(os.path.join(dir, 'video.key'), 'rb') as r, \
                open(os.path.join(dir, 'video.key.IV'), 'rb') as r2:
            key = r.read()
            bIV = r2.read()
    if key and bIV:  # 如果是加密的m3u8
        from Crypto.Cipher import AES  # require pycrypto
        aes = AES.new(key, AES.MODE_CBC, bIV)

    for name in ts_names:
        md5 = hashlib.md5()
        md5.update(name.encode('utf-8'))
        save_name = md5.hexdigest()
        # save_name = name.split('/')[-1] if name.startswith('http') else name
        fp = os.path.join(dir, save_name)
        if not os.path.exists(fp):
            continue
        with open(fp, 'rb') as r:
            content = r.read()
            if aes:
                content = aes.decrypt(content)
            merge_fo.write(content)
            print(f'merge {save_name}')
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
