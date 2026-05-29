import subprocess
import time
import os

FILE = "shared/file_10MB.bin"

SEEDER_PORT = 5050
LEECHER_PORT = 5051

print(f"Executando teste para: {FILE}")

seeder = subprocess.Popen(
    [
        "python3",
        "peer.py",
        "--port",
        str(SEEDER_PORT),
        "--file",
        FILE,
        "--seed"
    ]
)

time.sleep(2)

leecher = subprocess.Popen(
    [
        "python3",
        "peer.py",
        "--port",
        str(LEECHER_PORT),
        "--neighbors",
        f"127.0.0.1:{SEEDER_PORT}",
        "--file",
        os.path.basename(FILE)
    ]
)

leecher.wait()

print("\nTeste concluído.")
print("Pressione Ctrl+C para encerrar o Seeder.")