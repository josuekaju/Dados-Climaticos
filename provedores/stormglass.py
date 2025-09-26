import requests
from datetime import datetime, timezone

def obter_dados_stormglass(api_key, data_inicio, data_fim, latitude, longitude):
    """
    Busca dados históricos do StormGlass para um período e local.

    Args:
        api_key (str): Chave da API do StormGlass.
        data_inicio (datetime): Data de início da busca (objeto datetime com timezone).
        data_fim (datetime): Data de fim da busca (objeto datetime com timezone).
        latitude (float): Latitude do local.
        longitude (float): Longitude do local.

    Returns:
        list: Uma lista de dicionários com os dados coletados.
    """
    print("--- Executando StormGlass ---")
    if not api_key:
        print("Chave de API do StormGlass não configurada. Pulando...")
        return []

    base_url = "https://api.stormglass.io/v2/weather/point"
    headers = {
        "Authorization": api_key
    }
    
    # Converte datetimes para o formato ISO 8601 com 'Z' (UTC)
    start_utc = data_inicio.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')
    end_utc = data_fim.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')

    params_to_fetch = ["airTemperature", "humidity", "pressure", "windSpeed"]

    query_params = {
        "lat": latitude,
        "lng": longitude,
        "params": ",".join(params_to_fetch),
        "start": start_utc,
        "end": end_utc,
        "source": "noaa" # Fonte de dados comum
    }

    try:
        response = requests.get(base_url, headers=headers, params=query_params)
        response.raise_for_status()
        data = response.json()

        dados_coletados = []
        if 'hours' in data:
            for item in data['hours']:
                dados_coletados.append({
                    'provedor': 'StormGlass',
                    'data_hora': item.get('time'),
                    'temperatura_c': item.get('airTemperature', {}).get('noaa'),
                    'umidade_relativa': item.get('humidity', {}).get('noaa'),
                    'pressao_hpa': item.get('pressure', {}).get('noaa'),
                    'velocidade_vento_ms': item.get('windSpeed', {}).get('noaa'),
                })
        
        print(f"StormGlass: {len(dados_coletados)} registros encontrados.")
        return dados_coletados

    except requests.exceptions.HTTPError as e:
        # O plano gratuito do StormGlass tem um limite baixo (ex: 10 requisições/dia).
        # Erros de conexão ou status (como 402 - Payment Required) podem ocorrer se o limite for excedido.
        if e.response.status_code == 402:
            print("  - Limite diário do StormGlass excedido. Pulando...")
            return []
        print(f"  - Erro na requisição ao StormGlass: {e.response.status_code} - {e.response.text}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"  - Erro de conexão com o StormGlass: {e}")
        return []
    except Exception as e:
        print(f"  - Ocorreu um erro inesperado no StormGlass: {e}")
        return []

# Bloco de teste
if __name__ == '__main__':
    from dotenv import load_dotenv
    import os
    import pytz

    load_dotenv()
    API_KEY_TESTE = os.getenv("STORMGLASS_API_KEY")
    LAT_TESTE = -24.73
    LON_TESTE = -53.74
    
    # Define o fuso horário
    tz = pytz.timezone('America/Sao_Paulo')
    DATA_INICIO_TESTE = tz.localize(datetime(2024, 7, 20, 0, 0, 0))
    DATA_FIM_TESTE = tz.localize(datetime(2024, 7, 21, 0, 0, 0))

    if API_KEY_TESTE:
        resultados_sg = obter_dados_stormglass(API_KEY_TESTE, DATA_INICIO_TESTE, DATA_FIM_TESTE, LAT_TESTE, LON_TESTE)
        if resultados_sg:
            print(f"\nTotal de {len(resultados_sg)} registros do StormGlass encontrados.")
            print("Primeiro registro:", resultados_sg[0])
            print("Último registro:", resultados_sg[-1])
    else:
        print("\nChave de API 'STORMGLASS_API_KEY' não encontrada no arquivo .env para teste.")
