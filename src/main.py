from modules import sti_module, plan_module, request_module
from time import sleep
import pandas as pd
import logging # Implementar

def mainloop():

    sti_df = sti_module()
    plan_df = plan_module()

    df = pd.merge(sti_df, plan_df, on="Veiculo", how="outer")
    df = df.iloc[:, 0:]


    df.to_excel("results.xlsx")

    request_module(df)

if __name__ == "__main__":
    while True:
        try:
            mainloop()
            sleep(30)
        
        except Exception as e:
            print(f"Erro no loop principal: {e}")
