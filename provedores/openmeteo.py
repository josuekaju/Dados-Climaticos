import requests
import pandas as pd
from datetime import datetime

def obter_dados_openmeteo(data_inicio, data_fim, latitude, longitude):
    """
    Busca dados históricos do Open-Meteo para um período e local.

    Args:
        data_inicio (datetime): Data de início da busca.
        data_fim (datetime): Data de fim da busca.
        latitude (float): Latitude do local.
        longitude (float): Longitude do local.

    Returns:
        list: Uma lista de dicionários com os dados coletados.
    """
    print("--- Executando Open-Meteo ---")
    
    base_url = "https://archive-api.open-meteo.com/v1/archive"
    
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": data_inicio.strftime('%Y-%m-%d'),
        "end_date": data_fim.strftime('%Y-%m-%d'),
        "daily": "precipitation_sum,temperature_2m_mean,relativehumidity_2m_mean,windspeed_10m_mean",
        "timezone": "auto"
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Lança um erro para códigos de status ruins (4xx ou 5xx)
        
        dados_api = response.json()
        
        if 'daily' not in dados_api or not dados_api['daily']['time']:
            print("  - Open-Meteo: Nenhum dado diário retornado.")
            return []

        # Processar os dados em um formato padronizado
        dados_processados = []
        daily_data = dados_api['daily']
        
        for i, time_str in enumerate(daily_data['time']):
            dados_dia = {
                "data_hora": datetime.strptime(time_str, '%Y-%m-%d').isoformat(),
                "chuva_mm": daily_data.get('precipitation_sum', [None]*len(daily_data['time']))[i],
                "temperatura_c": daily_data.get('temperature_2m_mean', [None]*len(daily_data['time']))[i],
                "umidade_relativa_perc": daily_data.get('relativehumidity_2m_mean', [None]*len(daily_data['time']))[i],
                "velocidade_vento_ms": daily_data.get('windspeed_10m_mean', [None]*len(daily_data['time']))[i]
            }
            dados_processados.append(dados_dia)
        
        print(f"  - Open-Meteo: {len(dados_processados)} registros encontrados.")
        return dados_processados

    except requests.exceptions.HTTPError as http_err:
        print(f"  - Erro na requisição ao Open-Meteo (HTTP): {http_err}")
        return []
    except Exception as e:
        print(f"  - Erro inesperado ao processar dados do Open-Meteo: {e}")
        return []
