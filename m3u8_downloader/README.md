# m3u8 downloader
Download m3u8 data.

## Usage
- `python3 m3u8_downloader.py download "url_of_m3u8_file"`
- `python3 m3u8_downloader.py merge "downloaded-dir"`

## 原来用ffmpeg下载m3u8更简单
- 一条命令搞掂： `ffmpeg -i {url} -c copy save_filepath` :)
- ffmpeg 还自带各种视频和音频转码功能，真是太方便了!
