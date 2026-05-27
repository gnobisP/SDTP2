import os
import json
from SDTP2.config import CHUNK_SIZE
from SDTP2.utils import calculate_sha256



def create_metadata(filepath):
    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)

    total_chunks = (filesize + CHUNK_SIZE - 1) // CHUNK_SIZE

    metadata = {
        "filename": filename,
        "filesize": filesize,
        "chunk_size": CHUNK_SIZE,
        "total_chunks": total_chunks,
        "sha256": calculate_sha256(filepath)
    }

    metadata_path = f"metadata/{filename}.meta"

    with open(metadata_path, "w") as meta_file:
        json.dump(metadata, meta_file, indent=4)

    return metadata



def load_metadata(filename):
    metadata_path = f"metadata/{filename}.meta"

    with open(metadata_path, "r") as meta_file:
        return json.load(meta_file)



def split_file(filepath):
    metadata = create_metadata(filepath)

    filename = metadata["filename"]

    with open(filepath, "rb") as file:
        chunk_index = 0

        while chunk := file.read(CHUNK_SIZE):
            chunk_path = f"chunks/{filename}.part{chunk_index}"

            with open(chunk_path, "wb") as chunk_file:
                chunk_file.write(chunk)

            chunk_index += 1

    print(f"Arquivo fragmentado em {chunk_index} blocos.")



def assemble_file(filename):
    metadata = load_metadata(filename)

    total_chunks = metadata["total_chunks"]

    output_path = f"downloads/{filename}"

    with open(output_path, "wb") as output_file:
        for chunk_index in range(total_chunks):
            chunk_path = f"chunks/{filename}.part{chunk_index}"

            with open(chunk_path, "rb") as chunk_file:
                output_file.write(chunk_file.read())

    print("Arquivo remontado com sucesso.")

    original_hash = metadata["sha256"]
    downloaded_hash = calculate_sha256(output_path)

    print(f"SHA Original:   {original_hash}")
    print(f"SHA Download:  {downloaded_hash}")

    if original_hash == downloaded_hash:
        print("Integridade verificada com sucesso.")
    else:
        print("ERRO: arquivo corrompido.")