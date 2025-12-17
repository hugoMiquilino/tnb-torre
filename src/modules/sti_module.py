from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from datetime import datetime, timedelta
from dotenv import load_dotenv
from time import sleep
import pandas as pd
import json
import os


def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def setup():

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

    service = Service(log_path=os.devnull)

    return webdriver.Chrome(service=service, options=chrome_options)


def teardown(driver):
    driver.quit()


def collector():

    driver = setup()

    load_dotenv()

    user = os.getenv("USER")
    passwd = os.getenv("PASSWD")

    try:
        driver.get("https://serverca1.serveirc.com/Portal/Login")
        # assert "STI - Segurança, Logística e Telemetria" in driver.title
        sleep(1)
        driver.find_element(By.XPATH, '//*[@id="usuario"]').send_keys(user), sleep(0.2)
        driver.find_element(By.XPATH, '//*[@id="senha"]').send_keys(passwd, Keys.RETURN)

        sleep(1)
        driver.find_element(
            By.XPATH, "/html/body/div[6]/div[1]/div/div/div[1]/div/div[2]/div/a[1]"
        ).click()

        # assert "STI - Posições" in driver.title
        sleep(1)

        Select(driver.find_element(By.ID, "pageLength")).select_by_visible_text("100")

        sleep(3)

        complete_table = []
        rows = driver.find_elements(
            By.XPATH, "/html/body/div[4]/div/div/div[2]/div[2]/div/table/tbody/tr"
        )
        for row in rows:
            columns = [col.text.strip() for col in row.find_elements(By.XPATH, ".//td")]

            if len(columns) > 10:
                try:
                    lg_element = row.find_element(By.XPATH, ".//td[11]/img")
                    alt_value = lg_element.get_attribute("alt")

                    columns[10] = "\U0001f7e2" if alt_value == "Ligada" else "\U0001f518"
                except Exception:
                    columns[10] = "\U0001f518"

            complete_table.append(columns)

        return complete_table

    except Exception as e:
        print(f"Erro ao extrair dados: {e}")

    finally:
        teardown(driver)


def transform_data(data):

    data = data[1:] if len(data) > 1 else data

    if len(data) > 0 and len(data[0]) >= 9:
        df = pd.DataFrame(
            data,
            columns=[
                "-",
                "Conta",
                "Divisão",
                "Veiculo",
                "Operador",
                "Matricula?",
                "Data",
                "Evento",
                "Velocidade",
                "Local",
                "Status",
                "Rota",
                "Hodometro",
                "Horimetro",
                "RPM",
                "Temperatura",
                "Bateria Externa",
                "Bateria Interna",
            ],
        )
        
        # print(df.to_string())

        df = df[["Veiculo", "Data", "Velocidade", "Status", "Local"]]


        df["Veiculo"] = df["Veiculo"].str[:3] + " " + df["Veiculo"].str[3:]
        df["Veiculo"] = df["Veiculo"].str.rstrip("-")

        df["Velocidade"] = (
            df["Velocidade"].str.replace(" km/h", "").str.replace(",", ".").astype(int)
        )

        df["UF"] = df["Local"].apply(
            lambda loc: (
                "RJ"
                if "RJ" in loc.upper() or "RIO DE JANEIRO" in loc.upper()
                else (
                    "SP"
                    if "SP" in loc.upper()
                    or "PAULO" in loc.upper()
                    or "SA, BRASIL" in loc.upper()
                    else (
                        "MG"
                        if "MG" in loc.upper() or "MINAS GERAIS" in loc.upper()
                        else "-"
                    )
                )
            )
        )

        df["Local"] = df["Local"].str.title()

        df = converter(df, load_json("src/docs/conversion_dict.json"))

        df = df.drop_duplicates(subset="Veiculo")

        return df

    else:
        raise Exception(f"Erro: Dados inconsistentes, esperado 18 colunas, mas encontrado {len(data[0])} colunas")


def converter(df, conversion_dict):

    def convert_location(loc):
        loc_normalized = " ".join(loc.split()).lower()
        for key, value in conversion_dict.items():
            key_normalized = " ".join(key.split()).lower()
            if key_normalized in loc_normalized:
                return value
        return loc

    df["Local"] = df["Local"].apply(convert_location)

    return df


def sti_module():
    df = collector()
    df = transform_data(df)

    return df
