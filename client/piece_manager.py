import hashlib
from collections import defaultdict
import logging
from typing import Dict, List, Optional

class PieceManager:
    def __init__(self, torrent):
        self.torrent = torrent
        self.pieces: Dict[int, Piece] = {
            index: Piece(index, self._piece_size(index))
            for index in range(len(torrent.pieces))
        }
        self.completed_pieces = 0
        self.ongoing_pieces = defaultdict(list)

    def _piece_size(self, index: int) -> int:
        if index == len(self.torrent.pieces) - 1:
            return self.torrent.total_size - (index * self.torrent.piece_length)
        return self.torrent.piece_length

    def next_piece(self, bitfield: bytes) -> Optional[int]:
        for index, piece in self.pieces.items():
            if not piece.is_complete and self._has_piece(bitfield, index):
                return index
        return None

    def _has_piece(self, bitfield: bytes, index: int) -> bool:
        byte_index = index // 8
        bit_index = index % 8
        return bool(bitfield[byte_index] & (1 << (7 - bit_index)))

    def piece_completed(self, index: int, data: bytes):
        if self.pieces[index].validate(data):
            self.completed_pieces += 1
            self._save_piece(index, data)
        else:
            self.pieces[index].reset()

    def _save_piece(self, index: int, data: bytes):
       
        pass

class Piece:
    def __init__(self, index: int, length: int):
        self.index = index
        self.length = length
        self.is_complete = False
        self.data = b""

    def validate(self, data: bytes) -> bool:
        return hashlib.sha1(data).digest() == self.hash

    def reset(self):
        self.is_complete = False
        self.data = b""
