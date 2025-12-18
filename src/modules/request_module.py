from dotenv import load_dotenv
from time import sleep
import logging
import pandas as pd
import requests
import os

load_dotenv()

logger = logging.getLogger("tnb")

def build_rows(df, mapping):
    rows = []
    for _, row in df.iterrows():
        row_data = {target: row[source] for target, source in mapping.items()}
        rows.append(row_data)
    return rows


def data_modeling(df):
    mappings = {
        os.getenv("APPSHEET_TABLE_NAME_FROTA"): {
            "Motorista": "Motorista",
            "Veiculo": "Veiculo",
            "Carreta 1": "Carreta 1",
            "Carreta 2": "Carreta 2",
        },
        os.getenv("APPSHEET_TABLE_NAME_VEICULOS"): {
            "Placa": "Veiculo",
            "Local": "Local",
            "UF": "UF",
            "Status": "Status",
            "Velocidade": "Velocidade",
            # "Data": "Data"
        },
    }

    modeled_data = {
        table_name: build_rows(df, mapping) for table_name, mapping in mappings.items()
    }

    return modeled_data


def request_module(df):

    APPSHEET_APP_ID = os.getenv("APPSHEET_APP_ID")
    APPSHEET_ACCESS_KEY = os.getenv("APPSHEET_ACCESS_KEY")

    df = df.sort_values(by="Veiculo")
    df = df.where(pd.notnull(df), None)

    modeled_data = data_modeling(df)

    for table_name, rows in modeled_data.items():
        # Cria DataFrame temporário pra filtrar nulos na Key
        temp_df = pd.DataFrame(rows)

        # Detecta se é Frota_Matriz e aplica filtro de Key
        if table_name == os.getenv("APPSHEET_TABLE_NAME_FROTA"):
            key_col = "Motorista"
            before = len(temp_df)
            temp_df = temp_df[temp_df[key_col].notnull()]
            after = len(temp_df)
            logger.info(f"Removidas {before - after} linhas sem '{key_col}' antes do envio a {table_name}.")

        # Converte NaN -> None para JSON
        temp_df = temp_df.where(pd.notnull(temp_df), None)

        # Define a ação (Edit por padrão)
        action = "Edit"

        url = f"https://www.appsheet.com/api/v2/apps/{APPSHEET_APP_ID}/tables/{table_name}/Action"
        headers = {
            "ApplicationAccessKey": APPSHEET_ACCESS_KEY,
            "Content-Type": "application/json",
        }

        payload = {"Action": action, "Rows": temp_df.to_dict(orient="records")}

        logger.info(f"Enviando {len(temp_df)} registros para {table_name}...")

        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            logger.info(f"Dados enviados com sucesso para {table_name}!")
        else:
            logger.warning(f"Erro ao enviar dados para {table_name}: {response.status_code}")
            logger.warning("Resposta da API:", response.text)

        sleep(5)