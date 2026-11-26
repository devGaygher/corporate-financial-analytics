from pathlib import Path
from zipfile import ZipFile, BadZipFile
import hashlib
# caminhos do projeto
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / 'data' / 'raw'
DOCS_DIR = BASE_DIR / 'docs'

# arquivos esperados
EXPECTED_FILES = [
    RAW_DIR / "cad_cia_aberta.csv",
    RAW_DIR / "dfp_cia_aberta_2021.zip",
    RAW_DIR / "dfp_cia_aberta_2022.zip",
    RAW_DIR / "dfp_cia_aberta_2023.zip",
    RAW_DIR / "dfp_cia_aberta_2024.zip",
    RAW_DIR / "dfp_cia_aberta_2025.zip",
    DOCS_DIR / "meta_dfp_cia_aberta_txt.zip",   
]

def calculate_sha256(file_path):
    """Calcula o hash SHA256 de um arquivo."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 ** 2), b""):
            sha256_hash.update(chunk)

    return sha256_hash.hexdigest()

def inspect_zip(file_path):
    """verifica a integridade do arquivo e lista o conteudo"""

    try:
        with ZipFile(file_path, "r") as zip_file:
            files = zip_file.infolist()
            print(f"Arquivos internos: {len(files)}")

            corrupted_file = zip_file.testzip()
            if corrupted_file is None:
                print("Integridade OK")
            else:
                print(f"Arquivo corrompido: {corrupted_file}")

            print("\nConteúdo do zip:")

            for item in files:
                size_mb = item.file_size / (1024 ** 2)

                print (
                    f"{item.filename}"
                    f"|{size_mb : .2f} MB"
                )

    except BadZipFile:
        print("Arquivo zip corrompido ou inválido.")

def inspect_file(file_path):
    """apresenta infos sobre um arquivo de origem"""

    print(f"\n" + "=" * 80)
    print(f"Arquivo: {file_path.name}")

    if not file_path.is_file():
        print(f"status: não encontrado")
        return

    size_mb = file_path.stat().st_size / (1024 ** 2)
    print(f"status: encontrado")
    print(f"Tamanho: {size_mb : .2f} MB")
    print(f"SHA256: {calculate_sha256(file_path)}")

    if file_path.suffix.lower() == ".zip":
        inspect_zip(file_path)

def main():
    print("=" * 80)
    print("CORPORATE FINANCIAL ANALYTICS")
    print("SOURCE DATA INVENTORY")
    print("=" * 80)

    for file_path in EXPECTED_FILES:
        inspect_file(file_path)

    print("\n" + "=" * 80)
    print("inventario finalizado")
    print("=" * 80)

if __name__ == "__main__":
    main()