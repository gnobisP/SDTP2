import socket
import base64
import time

from SDTP2.protocol import encode_message, decode_message
from SDTP2.config import BUFFER_SIZE


class PeerClient:
    def __init__(self, host, port, neighbors, filename, metadata, chunks_owned):
        self.host = host
        self.port = port
        self.neighbors = neighbors
        self.filename = filename
        self.metadata = metadata
        self.chunks_owned = chunks_owned

    def request_chunk_list(self, neighbor_host, neighbor_port):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((neighbor_host, neighbor_port))

            request = {
                "type": "HAVE"
            }

            client_socket.send(encode_message(request))

            response = decode_message(client_socket.recv(BUFFER_SIZE))

            client_socket.close()

            return response["chunks"]

        except Exception:
            return None

    def download_chunk(self, neighbor_host, neighbor_port, chunk_index):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((neighbor_host, neighbor_port))

            request = {
                "type": "GET",
                "filename": self.filename,
                "chunk": chunk_index
            }

            client_socket.send(encode_message(request))

            response = decode_message(client_socket.recv(BUFFER_SIZE * 10))

            if response["type"] == "DATA":
                chunk_data = base64.b64decode(response["data"])

                chunk_path = f"chunks/{self.filename}.part{chunk_index}"

                with open(chunk_path, "wb") as chunk_file:
                    chunk_file.write(chunk_data)

                self.chunks_owned[chunk_index] = True

                print(
                    f"[DOWNLOAD] Recebeu bloco {chunk_index} de {neighbor_host}:{neighbor_port}"
                )

            client_socket.close()

        except Exception as error:
            print(f"Erro ao baixar bloco: {error}")

    def start_download(self):
        total_chunks = self.metadata["total_chunks"]

        while not all(self.chunks_owned):
            for neighbor_host, neighbor_port in self.neighbors:
                neighbor_chunks = self.request_chunk_list(
                    neighbor_host,
                    neighbor_port
                )

                if neighbor_chunks is None:
                    continue

                for chunk_index in range(total_chunks):
                    if (
                        not self.chunks_owned[chunk_index]
                        and neighbor_chunks[chunk_index]
                    ):
                        self.download_chunk(
                            neighbor_host,
                            neighbor_port,
                            chunk_index
                        )

            time.sleep(1)