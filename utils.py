import hashlib
import os


def calculate_sha256(filepath):
    sha256 = hashlib.sha256()

    with open(filepath, "rb") as file:
        while chunk := file.read(4096):
            sha256.update(chunk)

    return sha256.hexdigest()



def ensure_directories():
    directories = [
        "shared",
        "downloads",
        "chunks",
        "metadata"
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)