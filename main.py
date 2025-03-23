import argparse
from client.client import BitTorrentClient
import asyncio


def main():
    parser = argparse.ArgumentParser(description="BitTorrent Client")
    parser.add_argument("torrent", help="Path to torrent file")
    args = parser.parse_args()

    client = BitTorrentClient(args.torrent)
    asyncio.run(client.start())


if __name__ == "__main__":
    main()
