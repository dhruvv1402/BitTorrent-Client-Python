from dataclasses import dataclass
from pathlib import Path
import hashlib
import bencode
from typing import List, Dict, Union

from client.utils import decode_bencode


@dataclass
class File:
    path: Path
    length: int

class Torrent:
    def __init__(self, torrent_path: str):
        self.torrent_path = Path(torrent_path)
        self.data = self._parse_torrent_file()
        self.info = self.data["info"]
        self.info_hash = self._calculate_info_hash()
        self._validate_structure()

        self.total_size: int = 0
        self.files: List[File] = []
        self._process_files()

    def _parse_torrent_file(self) -> dict:
        with open(self.torrent_path, "rb") as f:
            return bencode.decode(f.read())

    def _calculate_info_hash(self) -> bytes:
        encoded_info = bencode.encode(self.info)
        return hashlib.sha1(encoded_info).digest()

    def _process_files(self) -> None:
        if "files" in self.info:
            
            base_path = Path(self.info["name"])
            for file_info in self.info["files"]:
                path = base_path / Path(*file_info["path"])
                self.files.append(File(path, file_info["length"]))
                self.total_size += file_info["length"]
        else:
           
            path = Path(self.info["name"])
            self.files.append(File(path, self.info["length"]))
            self.total_size = self.info["length"]

    def _validate_structure(self) -> None:
        required_keys = ["info", "announce"]
        for key in required_keys:
            if key not in self.data:
                raise ValueError(f"Invalid torrent file - missing {key}")

    @property
    def piece_length(self) -> int:
        return self.info["piece length"]

    @property
    def pieces(self) -> List[bytes]:
        return [self.info["pieces"][i:i+20]
                for i in range(0, len(self.info["pieces"]), 20)]

    @property
    def announce_list(self) -> List[str]:
        return self.data.get("announce-list", [])

    from .utils import decode_bencode

class Torrent:
    def __init__(self, torrent_path: str):
        self.torrent_path = Path(torrent_path)
        self.data = self._parse_torrent_file()
        self.info = self.data["info"]
        self.info_hash = self._calculate_info_hash()
        self._validate_structure()
        self.total_size: int = 0
        self.files: List[File] = []
        self._process_files()

    def _parse_torrent_file(self) -> dict:
        with open(self.torrent_path, "rb") as f:
            return decode_bencode(f.read())
