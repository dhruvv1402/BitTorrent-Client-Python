import asyncio
import hashlib
import logging
import struct
from typing import Optional, Tuple

class PeerConnection:
    CHUNK_SIZE = 16 * 1024 

    def __init__(self, peer: Tuple[str, int], torrent, piece_manager):
        self.peer = peer
        self.torrent = torrent
        self.piece_manager = piece_manager
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.bitfield = bytearray(len(self.torrent.pieces))
        self.peer_id: Optional[bytes] = None
        self.connected = False

    async def connect(self):
        try:
            self.reader, self.writer = await asyncio.wait_for(
                asyncio.open_connection(*self.peer),
                timeout=5
            )
            await self._perform_handshake()
            await self._receive_bitfield()
            self.connected = True
        except Exception as e:
            logging.error(f"Connection failed: {e}")

    async def _perform_handshake(self):
        handshake = struct.pack(">B19s8x20s20s",
                                19,
                                b"BitTorrent protocol",
                                self.torrent.info_hash,
                                self.torrent.peer_id)
        self.writer.write(handshake)
        await self.writer.drain()

        response = await self.reader.readexactly(68)
        if len(response) != 68:
            raise ConnectionError("Invalid handshake length")
        if response[1:20] != b"BitTorrent protocol":
            raise ConnectionError("Invalid protocol")

    async def _receive_bitfield(self):
        while True:
            header = await self.reader.readexactly(4)
            length = struct.unpack(">I", header)[0]
            if length == 0:
                continue  

            message_id = await self.reader.read(1)
            if message_id == b'\x05':  
                bitfield = await self.reader.readexactly(length - 1)
                self.bitfield = bitfield
                break

    async def download_piece(self, piece_index: int):
        if not self.bitfield[piece_index // 8] & (1 >> (piece_index % 8)):
            return None

        piece_size = self._calculate_piece_size(piece_index)
        blocks = []
        for offset in range(0, piece_size, self.CHUNK_SIZE):
            block = await self._request_block(piece_index, offset)
            blocks.append(block)

        piece_data = b"".join(blocks)
        if self._validate_piece(piece_index, piece_data):
            return piece_data
        return None

    async def _request_block(self, piece_index: int, offset: int):
        message = struct.pack(">IBHIII",
                              13, 
                              6,   
                              piece_index,
                              offset,
                              self.CHUNK_SIZE)
        self.writer.write(message)
        await self.writer.drain()

        while True:
            response_header = await self.reader.readexactly(4)
            response_length = struct.unpack(">I", response_header)[0]
            if response_length == 0:
                continue

            message_id = await self.reader.read(1)
            if message_id == b'\x07': 
                piece = await self.reader.readexactly(response_length - 1)
                return piece[8:]

    def _validate_piece(self, index: int, data: bytes) -> bool:
        return hashlib.sha1(data).digest() == self.torrent.pieces[index]

    def _calculate_piece_size(self, index: int) -> int:
        if index == len(self.torrent.pieces) - 1:
            return self.torrent.total_size - (index * self.torrent.piece_length)
        return self.torrent.piece_length
