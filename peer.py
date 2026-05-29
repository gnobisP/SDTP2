import threading
import argparse
import os
import time
import sys


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)

if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from SDTP2.utils import ensure_directories
from SDTP2.file_manager import (
    split_file,
    load_metadata,
    assemble_file
)
from SDTP2.server import PeerServer
from SDTP2.client import PeerClient


parser = argparse.ArgumentParser()

parser.add_argument("--host", default="127.0.0.1")
parser.add_argument("--port", type=int, required=True)
parser.add_argument("--neighbors", default="")
parser.add_argument("--file", default="")
parser.add_argument("--seed", action="store_true")

args = parser.parse_args()


ensure_directories()

neighbors = []

if args.neighbors:
    for neighbor in args.neighbors.split(","):
        host, port = neighbor.split(":")
        neighbors.append((host, int(port)))


filename = os.path.basename(args.file)


if args.seed:
    split_file(args.file)


metadata = load_metadata(filename)

total_chunks = metadata["total_chunks"]


chunks_owned = [False] * total_chunks


if args.seed:
    for index in range(total_chunks):
        chunks_owned[index] = True


server = PeerServer(
    args.host,
    args.port,
    chunks_owned
)

server_thread = threading.Thread(target=server.start)
server_thread.daemon = True
server_thread.start()


time.sleep(2)


if not args.seed:
    client = PeerClient(
        args.host,
        args.port,
        neighbors,
        filename,
        metadata,
        chunks_owned
    )

    client.start_download()

    assemble_file(filename)
    print("Download finalizado.")
    exit(0)


while True:
    time.sleep(1)