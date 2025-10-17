from time import sleep
import pandas as pd


def collector():

    data = pd.read_excel(
        "C:/Users/RecepcaoMatriz.TNB/OneDrive/Documentos/RELATORIO DE CAVALOS E CARRETAS.xlsx",
        sheet_name="EM VIAGEM",
        usecols="B,D:F",
        skiprows=2,
    )
    colunas_padrao = ["Motorista", "Veiculo", "Carreta 1", "Carreta 2"]

    data.columns = colunas_padrao
    data = data.fillna("").apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    df = data[~data["Motorista"].isin(["", "Sem Motorista"])]

    print(df.to_string())

    return df


def plan_module():
    df = collector()

    return df
