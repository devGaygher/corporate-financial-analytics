from pathlib import Path
from zipfile import ZipFile

# caminhos do projeto
BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / 'docs'

METADATA_FILE = DOCS_DIR / "meta_dfp_cia_aberta_txt.zip"

# docs selecionados
EXPECTED_METADATA = [
    "meta_dfp_cia_aberta.txt", 
    "meta_dfp_cia_aberta_BPA.txt",
    "meta_dfp_cia_aberta_BPP.txt",
    "meta_dfp_cia_aberta_DRE.txt",
    "meta_dfp_cia_aberta_DFC_MI.txt",
    "meta_dfp_cia_aberta_DFC_MD.txt",
]

def inspect_metadata():
    """realiza a leitura do dicionario oficial da CVM"""

    if not METADATA_FILE.is_file():
        print("Dicionário de dados não encontrado")
        return

    with ZipFile(METADATA_FILE, "r") as zip_file:
        available_files = zip_file.namelist()

        for file_name in EXPECTED_METADATA:

            print("\n" + "=" * 80)
            print(f"Documento: {file_name}")
            print("\n" + "=" * 80)

            if file_name not in available_files:
                print("Documento não encontrado.")
                continue
        
            content = zip_file.read(file_name).decode("latin-1")

            fields = [
                line.split(":", 1)[1].strip()
                for line in content.splitlines()
                if line.strip().startswith("Campo:")
            ]

            print(f"Quantidade de campos: {len(fields)}")
            print(f"Campos: {', '.join(fields)}")
            print("\nDicionário de dados:\n")
            print(content)


def main():
    print("=" * 80)
    print("CORPORATE FINANCIAL ANALYTICS")
    print("CVM METADATA INSPECTION")
    print("=" * 80)

    inspect_metadata()

    print("\n" + "=" * 80)
    print("Inspetor de metadados finalizada")
    print("=" * 80)

if __name__ == "__main__":
    main()