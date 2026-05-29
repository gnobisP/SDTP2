import socket
import base64
import time
import os

from protocol import encode_message, decode_message
from config import BUFFER_SIZE


class PeerClient:

    def __init__(
        self,
        host,
        port,
        neighbors,
        filename,
        metadata,
        chunks_owned
    ):
        self.host = host
        self.port = port
        self.neighbors = neighbors
        self.filename = filename
        self.metadata = metadata
        self.chunks_owned = chunks_owned

    def request_chunk_list(
        self,
        neighbor_host,
        neighbor_port
    ):
        try:

            client_socket = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            client_socket.connect(
                (neighbor_host, neighbor_port)
            )

            request = {
                "type": "HAVE"
            }

            client_socket.send(
                encode_message(request)
            )

            response = decode_message(
                client_socket.recv(
                    BUFFER_SIZE
                )
            )

            client_socket.close()

            total_chunks = response[
                "total_chunks"
            ]

            return [True] * total_chunks

        except Exception as error:

            print(
                f"Erro ao consultar peer: "
                f"{error}"
            )

            return None

    def download_chunk(
        self,
        neighbor_host,
        neighbor_port,
        chunk_index
    ):
        try:

            client_socket = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            client_socket.connect(
                (neighbor_host, neighbor_port)
            )

            request = {
                "type": "GET",
                "filename": self.filename,
                "chunk": chunk_index
            }

            client_socket.send(
                encode_message(request)
            )

            response = decode_message(
                client_socket.recv(
                    BUFFER_SIZE * 10
                )
            )

            if response["type"] == "DATA":

                chunk_data = (
                    base64.b64decode(
                        response["data"]
                    )
                )

                chunk_path = (
                    f"chunks/"
                    f"{self.filename}"
                    f".part{chunk_index}"
                )

                with open(
                    chunk_path,
                    "wb"
                ) as chunk_file:

                    chunk_file.write(
                        chunk_data
                    )

                self.chunks_owned[
                    chunk_index
                ] = True

                print(
                    f"[DOWNLOAD] "
                    f"Bloco {chunk_index} "
                    f"recebido de "
                    f"{neighbor_host}:"
                    f"{neighbor_port}"
                )

            client_socket.close()

        except Exception as error:

            print(
                f"Erro ao baixar bloco: "
                f"{error}"
            )

    def save_metrics(
        self,
        elapsed_time
    ):

        filesize = self.metadata[
            "filesize"
        ]

        throughput = (
            filesize /
            elapsed_time
        )

        throughput_mb = (
            throughput /
            (1024 * 1024)
        )

        file_exists = (
            os.path.exists(
                "results.csv"
            )
        )

        with open(
            "results.csv",
            "a"
        ) as file:

            if not file_exists:

                file.write(
                    "filename,"
                    "filesize,"
                    "chunk_size,"
                    "total_chunks,"
                    "download_time,"
                    "throughput_mb\n"
                )

            file.write(
                f"{self.filename},"
                f"{filesize},"
                f"{self.metadata['chunk_size']},"
                f"{self.metadata['total_chunks']},"
                f"{elapsed_time:.6f},"
                f"{throughput_mb:.6f}\n"
            )

        print(
            f"\nTempo total: "
            f"{elapsed_time:.3f} s"
        )

        print(
            f"Throughput: "
            f"{throughput_mb:.3f} MB/s"
        )

    def start_download(self):

        total_chunks = (
            self.metadata[
                "total_chunks"
            ]
        )

        start_time = time.time()

        while not all(
            self.chunks_owned
        ):

            for (
                neighbor_host,
                neighbor_port
            ) in self.neighbors:

                neighbor_chunks = (
                    self.request_chunk_list(
                        neighbor_host,
                        neighbor_port
                    )
                )

                if neighbor_chunks is None:
                    continue

                for chunk_index in range(
                    total_chunks
                ):

                    if (
                        not self.chunks_owned[
                            chunk_index
                        ]
                        and
                        neighbor_chunks[
                            chunk_index
                        ]
                    ):

                        self.download_chunk(
                            neighbor_host,
                            neighbor_port,
                            chunk_index
                        )

            time.sleep(0.01)

        end_time = time.time()

        elapsed_time = (
            end_time -
            start_time
        )

        self.save_metrics(
            elapsed_time
        )