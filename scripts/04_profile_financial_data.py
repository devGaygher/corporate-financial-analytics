from pathlib import Path
from zipfile import ZipFile
from decimal import Decimal

import pandas as pd

#  caminhos do projeto
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

# Config inicial do profiling
YEAR = 2025
STATEMENT = "DRE"

# Empresas selecionadas
TARGET_CODES = [
    "3980",
    "14320",
    "4030"
]


# Arquivos de origem
ZIP_FILE = RAW_DIR / f"dfp_cia_aberta_{YEAR}.zip"
CSV_FILE = f"dfp_cia_aberta_{STATEMENT}_con_{YEAR}.csv"

def load_financial_data():
    """Carrega uma demonstração financeira da CVM"""
    with ZipFile(ZIP_FILE, "r") as zip_file:

        with zip_file.open(CSV_FILE, "r") as csv_file:
            df = pd.read_csv(
                csv_file,
                sep=";",
                encoding="latin-1",
                dtype=str   
            )
    return df

def filter_target_companies(df):
    """Seleciona as empresas de interesse"""

    normalized_codes = [
    code.zfill(6)
    for code in TARGET_CODES

]
    normalized_column = df["CD_CVM"].str.zfill(6)

    mask = normalized_column.isin(normalized_codes)
    df_targets = df.loc[mask].copy()
    return df_targets

def profile_financial_data(df):
    
    print("\n" + "=" * 80)
    print("FINANCIAL DATA PROFILING")
    print("=" * 80)    

    print(f"\nTotal de registros: {len(df)}")
    
    print("Empresas identificadas:")
    print(df["CD_CVM"].unique())

    print(f"\nRegistros por código CVM:")
    print(df["CD_CVM"].value_counts())

    print("\nValores ausentes:")
    print(df.isna().sum())

    print("\nLinhas integralmente duplicadas:")
    print(df.duplicated().sum())

    profile_columns = [
        "VERSAO",
        "GRUPO_DFP",
        "MOEDA",
        "ESCALA_MOEDA",
        "ORDEM_EXERC",
        "DT_REFER",
        "DT_INI_EXERC",
        "DT_FIM_EXERC",
        "ST_CONTA_FIXA"
    ]
    for column in profile_columns:
        print(f"\nDistribuição: {column}")

        print(df[column].value_counts(dropna=False))

    candidate_key = [
        "CD_CVM",
        "CD_CONTA",
        "DT_REFER",
        "VERSAO",
        "DT_INI_EXERC",
        "DT_FIM_EXERC"
    ]

    print("\nVerificação de chave composta")
    print(f"\nTotal de registros: {len(df)}")
    print(f"\nTotal de chaves distintas: {len(df.drop_duplicates(subset=candidate_key))}")
    print(f"\nDuplicidades na chave: {df.duplicated(subset=candidate_key).sum()}")
        

    print("\nAvaliação da distribuição do ST_CONTA_FIXA:")
    print(df.groupby(["CD_CVM", "ST_CONTA_FIXA"]).size().reset_index(name="Quantidade"))

    print("\nEstrutura das contas contábeis:")
    df_accounts = df[["CD_CONTA", "DS_CONTA", "ST_CONTA_FIXA"]]
    print(df_accounts.drop_duplicates().to_string(index=False))

    print("\nDistribuição por nível hierárquico e tipo de conta:")
    account_level = df["CD_CONTA"].str.count(r"\.") + 1
    df_levels = df.assign(NIVEL_CONTA=account_level)
    print(
        df_levels.groupby(["NIVEL_CONTA", "ST_CONTA_FIXA"])
        .size().reset_index(name="Quantidade"))

    numeric_values = pd.to_numeric(
        df["VL_CONTA"],
        errors="coerce"
    )
    print("\nVerificação de valores numericos")
    print(f"\nTotal de registros: {len(numeric_values)}")

    print(f"\nValores numericamente válidos:")
    print(numeric_values.notna().sum())

    print(f"\nValores numericamente inválidos ou ausentes:")
    print(numeric_values.isna().sum())

    
    print("\nAnálise dos valores monetários:")
    print(f"\nTipo de dado: {numeric_values.dtype}")
    print(f"\nValores negativos: {(numeric_values < 0).sum()}")
    print(f"\nValores iguais a zero: {(numeric_values == 0).sum()}")
    print(f"\nValores com parte fracionária: {(numeric_values.dropna() % 1 != 0).sum()}")

    
    print("\nInvestigação dos valores fracionários:")
    mask = numeric_values.notna() & (numeric_values % 1 != 0)
    columns = [
        "CD_CVM",
        "CD_CONTA",
        "DS_CONTA",
        "VL_CONTA",
        "ESCALA_MOEDA"
    ]
    print(
        df.loc[mask, columns].to_string(index=False)
    )

    print("\nInvestigação das contas de lucro por ação:")
    eps_mask = df["CD_CONTA"].str.startswith("3.99", na=False)
    df_eps = df.loc[eps_mask, columns]
    print(df_eps.to_string(index=False))
    print(f"\nTotal de registros de lucro por ação: {len(df_eps)}")
    print("\nDistribuição por empresa:")
    print(df_eps["CD_CVM"].value_counts())

    print("\nInvestigação da precisão decimal:")
    decimal_places = (
        df["VL_CONTA"]
        .str.split(".", regex=False)
        .str[1]
        .str.len()
        .fillna(0)
        .astype(int)
    )
    print("\nDistribuição das casas decimais:")
    print(decimal_places.value_counts().sort_index())
    print(f"\nMáximo de casas decimais: {decimal_places.max()}")

    df_decimal = df.assign(
    VL_CONTA_DECIMAL=df["VL_CONTA"].map(Decimal)
    )
    
    df_pivot = df_decimal.pivot(
    index=[
        "CD_CVM",
        "DT_REFER",
        "VERSAO",
        "DT_INI_EXERC",
        "DT_FIM_EXERC"
    ],
    columns="CD_CONTA",
    values="VL_CONTA_DECIMAL"
)
    print("\nValidação das relações contábeis da DRE:")

    validation_rules = [
        ("Lucro bruto", "3.01", "3.02", "3.03"),
        ("EBIT", "3.03", "3.04", "3.05"),
        ("Resultado antes dos tributos", "3.05", "3.06", "3.07"),
        ("Resultado das operações continuadas", "3.07", "3.08", "3.09"),
        ("Lucro líquido consolidado", "3.09", "3.10", "3.11")
    ]

    total_validations = 0
    total_approved = 0
    total_failed = 0
    total_missing = 0

    for name, account_a, account_b, account_result in validation_rules:
        calculated = df_pivot[account_a] + df_pivot[account_b]
        reported = df_pivot[account_result]
        difference = calculated - reported
        valid_mask = calculated.notna() & reported.notna()
        approved_mask = valid_mask & difference.eq(Decimal("0"))
        failed_mask = valid_mask & ~approved_mask

        validation = pd.DataFrame({
            "Calculado": calculated,
            "Informado": reported,
            "Diferenca": difference,
            "Aprovado": approved_mask
        })

        approved = approved_mask.sum()
        failed = failed_mask.sum()
        missing = (~valid_mask).sum()

        total_validations += len(validation)
        total_approved += approved
        total_failed += failed
        total_missing += missing

        print(f"\nValidação: {name}")
        print(validation.to_string())

        print(f"\nAprovadas: {approved}")
        print(f"Reprovadas: {failed}")
        print(f"Sem dados suficientes: {missing}")

    print("\n" + "=" * 80)
    print("RESUMO DAS VALIDAÇÕES CONTÁBEIS")
    print("=" * 80)

    print(f"\nTotal de validações: {total_validations}")
    print(f"Validações aprovadas: {total_approved}")
    print(f"Validações reprovadas: {total_failed}")
    print(f"Validações sem dados: {total_missing}")

    if total_validations > 0:
        success_rate = total_approved / total_validations * 100
        print(f"Taxa de aprovação: {success_rate:.2f}%")



def main():
    print("=" * 80)
    print("CORPORATE FINANCIAL ANALYTICS")
    print("FINANCIAL DATA PROFILING")
    print("=" * 80)

    df_financial = load_financial_data()

    print("\nCódigos CVM disponíveis:")
    print(df_financial["CD_CVM"].unique())

    print(f"\nAno do arquivo: {YEAR}")
    print(f"Demonstração: {STATEMENT}")

    print(f"\nRegistros originais: {len(df_financial)}")

    df_targets = filter_target_companies(df_financial)

    print(f"Registros selecionados: {len(df_targets)}")

    profile_financial_data(df_targets)

    print("\n" + "=" * 80)
    print("Profiling financeiro inicial finalizado.")
    print("=" * 80)


if __name__ == "__main__":
    main()