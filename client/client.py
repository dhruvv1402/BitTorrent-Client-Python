import asyncio
import logging
from rich.progress import Progress
from typing import List

from .torrent import Torrent
from .tracker import Tracker
from .peer import PeerConnection
from .piece_manager import PieceManager

class BitTorrentClient:
    def __init__(self, torrent_path: str):
        self.torrent = Torrent(torrent_path)
        self.tracker = Tracker(self.torrent)
        self.piece_manager = PieceManager(self.torrent)
        self.connections: List[PeerConnection] = []
        self.progress = Progress()

    async def start(self):
        with self.progress:
            task = self.progress.add_task(
                "[cyan]Downloading...", total=self.torrent.total_size)

            peers = await self.tracker.get_peers()
            logging.info(f"Connected to {len(peers)} peers")

            await asyncio.gather(*[
                self._handle_peer(peer, task)
                for peer in peers[:10] 
            ])

    async def _handle_peer(self, peer: tuple, task):
        connection = PeerConnection(peer, self.torrent, self.piece_manager)
        await connection.connect()

        if not connection.connected:
            return

        self.connections.append(connection)
        while not self.download_complete:
            piece_index = self.piece_manager.next_piece(connection.bitfield)
            if piece_index is None:
                break

            data = await connection.download_piece(piece_index)
            if data:
                self.piece_manager.piece_completed(piece_index, data)
                self.progress.update(task, advance=len(data))

    @property
    def download_complete(self) -> bool:
        return self.piece_manager.completed_pieces == len(self.torrent.pieces)
