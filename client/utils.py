# client/utils.py
import logging
from datetime import time
from typing import Union
import bencode
from rich.progress import Progress

def configure_logging():
    """Configure basic logging setup"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def bytes_to_human(size: int) -> str:
    """Convert bytes to human-readable format"""
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    for unit in units:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"

def safe_bdecode(data: bytes) -> Union[dict, list, int, str, None]:
    """Safely decode bencoded data with error handling"""
    try:
        return bencode.decode(data)
    except (bencode.BencodeDecodeError, ValueError) as e:
        logging.error(f"Bdecode error: {e}")
        return None

class TorrentProgress(Progress):
    """Custom progress bar with torrent-specific metrics"""

    def get_renderables(self):
        yield self.make_tasks_table(self.tasks)

    def update_task(self, task_id, **fields):
        if 'total' in fields:
            fields['total'] = int(fields['total'])
        super().update_task(task_id, **fields)

def calculate_download_speed(start_time, downloaded_bytes):
    """Calculate download speed in MB/s"""
    elapsed = time.time() - start_time
    if elapsed == 0:
        return 0.0
    return (downloaded_bytes / (1024 * 1024)) / elapsed

def decode_bencode(data):
    def decode_dict(s):
        d = {}
        while s[0] != 'e':
            key = decode_data(s)
            value = decode_data(s)
            d[key] = value
        return d[1:], s[1:]

    def decode_list(s):
        l = []
        while s[0] != 'e':
            elem, s = decode_data(s)
            l.append(elem)
        return l, s[1:]

    def decode_int(s):
        return int(s[1:s.index('e')]), s[s.index('e')+1:]

    def decode_string(s):
        colon = s.index(':')
        length = int(s[:colon])
        s = s[colon+1:]
        return s[:length], s[length:]

    def decode_data(s):
        if s[0] == 'd':
            return decode_dict(s[1:])
        elif s[0] == 'l':
            return decode_list(s[1:])
        elif s[0] == 'i':
            return decode_int(s[1:])
        elif s[0].isdigit():
            return decode_string(s)
        else:
            raise ValueError("Invalid bencode data")

    return decode_data(data.decode('latin1'))[0]