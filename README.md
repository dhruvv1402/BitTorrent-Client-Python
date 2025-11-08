---

## BitTorrent Client in Python

Just a small BitTorrent client made in Python. It connects to peers, downloads pieces, checks them, and puts the file back together. Mainly built to get a feel for how torrents actually work under the hood.

## What it does

* Talks to trackers and finds peers
* Downloads file pieces using asyncio
* Checks pieces with SHA-1 before saving
* Works for single or multi-file torrents
* Shows basic progress while downloading

## How to run

```bash
git clone https://github.com/yourusername/bittorrent-client.git
cd bittorrent-client
pip install -r requirements.txt
python main.py yourfile.torrent
```

## Folder layout

```
bittorrent-client/
├── client/
│   ├── torrent.py
│   ├── tracker.py
│   ├── peer.py
│   ├── piece_manager.py
└── main.py
```

## Uses

bencodepy
requests
rich
async-timeout

## License

MIT, do whatever basically.

---
