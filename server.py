import socket
import threading
import base64
import os

from SDTP2.protocol import decode_message, encode_message
from SDTP2.config import BUFFER_SIZE


class PeerServer:
    def __init__(self, host, port, chunks_owned):
        self.host = host
        self.port = port
        self.chunks_owned = chunks_owned

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen()

        print(f"[SERVIDOR] Escutando em {self.host}:{self.port}")

        while True:
            client_socket, address = server_socket.accept()

            thread = threading.Thread(
                target=self.handle_client,
                args=(client_socket, address)
            )

            thread.start()

    def handle_client(self, client_socket, address):
        try:
            data = client_socket.recv(BUFFER_SIZE)

            if not data:
                return

            message = decode_message(data)

            message_type = message["type"]

            if message_type == "HAVE":
                response = {
                    "type": "HAVE_RESPONSE",
                    "chunks": self.chunks_owned
                }

                client_socket.send(encode_message(response))

            elif message_type == "GET":
                filename = message["filename"]
                chunk_index = message["chunk"]

                chunk_path = f"chunks/{filename}.part{chunk_index}"

                if os.path.exists(chunk_path):
                    with open(chunk_path, "rb") as chunk_file:
                        chunk_data = chunk_file.read()

                    encoded_chunk = base64.b64encode(chunk_data).decode()

                    response = {
                        "type": "DATA",
                        "chunk": chunk_index,
                        "data": encoded_chunk
                    }

                    client_socket.send(encode_message(response))

                    print(f"[UPLOAD] Enviou bloco {chunk_index} para {address}")

        except Exception as error:
            print(f"Erro no servidor: {error}")

        finally:
            client_socket.close()