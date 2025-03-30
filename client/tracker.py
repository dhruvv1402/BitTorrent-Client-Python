import hashlib
import os

import bencode
import requests
import socket
import struct
import asyncio
from typing import List, Tuple
from urllib.parse import urlparse
from .torrent import Torrent

class Tracker:
    def __init__(self, torrent: Torrent):
        self.torrent = torrent
        self.peer_id = "-PC0001-" + hashlib.sha1(os.urandom(20)).hexdigest()[:12]

    async def get_peers(self) -> List[Tuple[str, int]]:
        peers = []
        for tracker_url in self._get_tracker_urls():
            try:
                if tracker_url.startswith("udp"):
                    peers += await self._contact_udp_tracker(tracker_url)
                else:
                    peers += self._contact_http_tracker(tracker_url)
            except Exception as e:
                continue
        return list(set(peers))

    def _get_tracker_urls(self) -> List[str]:
        base = [self.torrent.data["announce"]]
        return base + [url for tier in self.torrent.announce_list
                       for url in tier]

    def _contact_http_tracker(self, url: str) -> List[Tuple[str, int]]:
        params = {
            "info_hash": self.torrent.info_hash,
            "peer_id": self.peer_id,
            "port": 6881,
            "uploaded": 0,
            "downloaded": 0,
            "left": self.torrent.total_size,
            "compact": 1
        }
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        return self._decode_peers(response.content)

    async def _contact_udp_tracker(self, url: str) -> List[Tuple[str, int]]:
        
        pass  

    def _decode_peers(self, data: bytes) -> List[Tuple[str, int]]:
        peers = []
        try:
            decoded = bencode.decode(data)
            peers_data = decoded.get("peers", b"")
            if isinstance(peers_data, list):
                peers = [(p["ip"], p["port"]) for p in peers_data]
            else:
                peers = [(peers_data[i:i+4].decode('latin1'),
                          struct.unpack("!H", peers_data[i+4:i+6])[0])
                         for i in range(0, len(peers_data), 6)]
        except Exception:
            pass
        return peers
