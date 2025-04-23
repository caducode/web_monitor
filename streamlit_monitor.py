import streamlit as st
from seleniumwire import webdriver  # diferente do selenium comum
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
import json
import time
import gzip
from io import BytesIO



st.header("Monitoria dos carrosséis de recomendação")

config_names = []
status_value = []

# # Inicializa o driver com selenium-wire
chrome_options = Options()
# Adicione outras opções conforme necessário
chrome_options.add_argument("--start-maximized")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

try:
    # Acessa o site principal
    driver.get("https://www.arezzo.com.br/")
    time.sleep(5)  # aguarda carregar e disparar as requests

    # Procura a request desejada
    target_url = "https://www.arezzo.com.br/arezzocoocc/v2/arezzo/web-parameters"

    carrossel_logic = ['user_personalization','complement_items', 'related_look']

    for request in driver.requests:
        if request.url.startswith(target_url):
            encoding = request.response.headers.get("Content-Encoding", "")
            raw_data = request.response.body

            if "gzip" in encoding:
                # Descompacta
                buf = BytesIO(raw_data)
                with gzip.GzipFile(fileobj=buf) as f:
                    decoded_data = f.read().decode("utf-8")
            else:
                decoded_data = raw_data.decode("utf-8")
            
            json_data = json.loads(decoded_data)
            parameters = json_data.get("parameters")
            for item in parameters:
                if item['code'].endswith(tuple(carrossel_logic)):
                    config_names.append(item['code']) 
                    status_value.append(item['value'])
                
finally:
    driver.quit()

data_obj = {
                'nome_config': config_names,
                'status_config': status_value
            }

df_configs = pd.DataFrame(data_obj)
st.write(df_configs)
