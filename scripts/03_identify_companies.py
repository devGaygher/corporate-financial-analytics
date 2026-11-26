from pathlib import Path
import pandas as pd

# caminhos do projeto
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / 'data' / 'raw'

REGISTRY_FILE = RAW_DIR / "cad_cia_aberta.csv"

def load_registry():
    """carrega o cadastro de companhias abertas da CVM"""

    df = pd.read_csv(
        REGISTRY_FILE,
        sep=";",
        encoding="latin-1",
        dtype=str
    )
    return df

def profile_registy(df):
    """ realiza o profiling inicia do cadastro"""

    print("\n" + "=" * 80)
    print("REGISTRY DATA PROFILING")
    print( "=" * 80)

    print("\nDimensões da base:")
    print(f"Linhas: {df.shape[0]}")
    print(f"Colunas: {df.shape[1]}")

    print("\nNomes das colunas:")
    print(df.columns.tolist())

    print("\nPrimeiros cinco registros:")
    print(df.head().to_string())

    print("\nInformações gerais:")
    df.info()

    print("\nTipos de dados:")
    print(df.dtypes)

    print("\nValores ausentes por coluna:")
    print(df.isnull().sum())

    print("\nQuantidade de linhas duplicadas:")
    print(df.duplicated().sum())

def validate_identifiers(df):
    """investiga a qualidade dos identificadores"""

    print("\n" + "=" * 80)
    print("IDENTIFIER VALIDATION")
    print("=" * 80)

    for column in ["CD_CVM", "CNPJ_CIA"]:

        print(f"\nCampo: {column}")
        print(f"Registros: {len(df)}")
        print(f"VAlores ausentes: {df[column].isna().sum()}")
        print(f"Valores únicos: {df[column].nunique()}")
        print(f"Duplicados: {df[column].duplicated().sum()}")

def identify_companies(df):
    """Localiza possiveis empresas de interesse."""

    print("\n" + "=" * 80)
    print("TARGET COMPANY IDENTIFICATION")
    print("=" * 80)

    search_terms = [
        "GERDAU",
        "USIMINAS",
        "USINAS SIDER",
        "SIDERÚRGICA NACIONAL",
        "SIDERURGICA NACIONAL",
        "CSN"
    ]

    selected_columns = [
        "CD_CVM",
        "CNPJ_CIA",
        "DENOM_SOCIAL",
        "DENOM_COMERC",
        "SETOR_ATIV",
        "SIT",
        "CATEG_REG",
        "SIT_EMISSOR"
    ]

    pattern = "|".join(search_terms)

    mask = (
        df["DENOM_COMERC"].str.contains(
            pattern,
            case = False,
            na=False
        )
    )

    df_cadidates = df.loc[
        mask,
        selected_columns
    ].sort_values("DENOM_SOCIAL")

    print(f"\nEmpresas candidatas: {len(df_cadidates)}")
    print(df_cadidates.to_string(index=False))
    return df_cadidates

def inspect_target_duplicates(df):
    """Investiga diferenças entre registrros das empresas selecionadas."""

    print("\n" + "=" * 80)
    print("TARGET COMPANY DUPLICATE INSPECTION")
    print("=" * 80)

    target_codes = ["3980", "14320", "4030"]

    df_targets = df.loc[
        df["CD_CVM"].isin(target_codes)
    ]

    for code in target_codes:

        df_company = df_targets.loc[
            df_targets["CD_CVM"] == code
        ]
        print(f"\nCódigo CVM: {code}")
        print(f"Quantidade de registros: {len(df_company)}")

        if len(df_company) <= 1:
            print("Não há registros duplicados para esta empresa")
            continue

        different_columns = [
        column
        for column in df_company.columns
        if df_company[column].nunique(dropna=False) > 1
        ]

        print(f"Colunas divergentes: {len(different_columns)}")
        print(different_columns)

        print(
            df_company[different_columns].to_string(index=False)
        )



def main():
    print("=" * 80)
    print("CORPORATE FINANCIAL ANALYTICS")
    print("COMPANY REGISTRY INSPECTION")
    print("=" * 80)

    if not REGISTRY_FILE.is_file():
        print("Arquivo de cadastro não encontrado")
        return

    df_registry = load_registry()

    profile_registy(df_registry)

    validate_identifiers(df_registry)

    identify_companies(df_registry)

    inspect_target_duplicates(df_registry)

    print("\n" + "=" * 80)
    print("Profiling inicial finalizado")
    print("=" * 80)

if __name__ == "__main__":
    main()  