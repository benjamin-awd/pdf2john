import subprocess

from pdf2john import PdfHashExtractor


def unlock_pdf(pdf_file_path: str, static_string: str):
    hash_extractor = PdfHashExtractor(pdf_file_path)
    pdf_hash = hash_extractor.parse()

    hash_path = ".hash"
    with open(hash_path, "w", encoding="utf-8") as file:
        file.write(pdf_hash)

    mask_command = [f"john --format=PDF --mask={static_string} {hash_path} --pot=.pot"]
    process = subprocess.run(mask_command, shell=True, check=False)

    if not process.returncode == 0:
        raise ValueError(f"Return code is not 0: {process}")

    show_command = ["john", "--show", hash_path, "--pot=.pot"]
    output = subprocess.run(show_command, capture_output=True, text=True, check=False)

    if not output.returncode == 0:
        raise ValueError(f"Return code is not 0: {output}")

    if "1 password hash cracked, 0 left" not in output.stdout:
        raise ValueError(f"PDF was not unlocked: {output}")

    password = output.stdout.split("\n")[0].split(":")[-1]

    return password
