import requests
from datetime import datetime, timezone
import time
import pytz

def _date_to_unix_timestamp(dt_obj_local):
    """Converte um objeto datetime local para um timestamp Unix UTC."""
    # Garante que o objeto datetime tenha informação de fuso horário
    if dt_obj_local.tzinfo is None:
        tz = pytz.timezone('America/Sao_Paulo') # Fuso horário de referência
        dt_obj_local = tz.localize(dt_obj_local)
    
    # Converte para UTC e depois para timestamp
    dt_obj_utc = dt_obj_local.astimezone(timezone.utc)
    return int(dt_obj_utc.timestamp())

def obter_dados_openweathermap(api_key, data_inicio, data_fim, latitude, longitude):
    """
    Busca dados históricos do OpenWeatherMap para um período e local.

    Args:
        api_key (str): Chave da API do OpenWeatherMap.
        data_inicio (datetime): Data de início da busca.
        data_fim (datetime): Data de fim da busca.
        latitude (float): Latitude do local.
        longitude (float): Longitude do local.

    Returns:
        list: Uma lista de dicionários com os dados coletados.
    """
    print("--- Executando OpenWeatherMap ---")
    if not api_key:
        print("Chave de API do OpenWeatherMap não configurada. Pulando...")
        return []

    base_url = "https://history.openweathermap.org/data/2.5/history/city"
    dados_coletados = []

    start_timestamp = _date_to_unix_timestamp(data_inicio)
    end_timestamp = _date_to_unix_timestamp(data_fim)

    current_start = start_timestamp
    while current_start < end_timestamp:
        current_end = min(current_start + (7 * 24 * 60 * 60), end_timestamp)

        params = {
            "lat": latitude,
            "lon": longitude,
            "type": "hour",
            "start": current_start,
            "end": current_end,
            "appid": api_key
        }

        try:
            response = requests.get(base_url, params=params, timeout=20)
            response.raise_for_status()
            data = response.json()

            if 'list' in data:
                for item in data['list']:
                    dados_coletados.append({
                        'provedor': 'OpenWeatherMap',
                        'data_hora': datetime.fromtimestamp(item['dt'], tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
                        'temperatura_c': item.get('main', {}).get('temp', None) - 273.15 if item.get('main', {}).get('temp') else None,
                        'umidade_relativa': item.get('main', {}).get('humidity'),
                        'pressao_hpa': item.get('main', {}).get('pressure'),
                        'velocidade_vento_ms': item.get('wind', {}).get('speed'),
                    })
            else:
                print(f"  - Aviso: Chave 'list' não encontrada na resposta para o período {current_start} - {current_end}")
        
        except requests.exceptions.HTTPError as e:
            # A API do OWM retorna 400 para períodos sem dados, então tratamos isso de forma mais branda
            if e.response.status_code == 400:
                 print(f"  - Nenhum dado encontrado no OpenWeatherMap para o período solicitado.")
            else:
                print(f"  - Erro na requisição: {e.response.status_code} para o período {current_start} - {current_end}")
            # Não interrompe o loop, apenas continua para o próximo período
        except requests.exceptions.RequestException as e:
            print(f"  - Erro de conexão: {e}")
            # Pára a execução para este provedor em caso de falha de conexão
            break
        except json.JSONDecodeError:
            print("  - Erro ao decodificar a resposta JSON do OpenWeatherMap.")

        current_start = current_end
        time.sleep(1) # Delay para não sobrecarregar a API

    print(f"OpenWeatherMap: {len(dados_coletados)} registros encontrados.")
    return dados_coletados

# Bloco de teste
if __name__ == '__main__':
    # Para testar este módulo individualmente
    from dotenv import load_dotenv
    import os

    load_dotenv() # Carrega o .env do diretório do projeto
    API_KEY_TESTE = os.getenv("OPENWEATHERMAP_API_KEY")
    LAT_TESTE = -24.73
    LON_TESTE = -53.74
    # Período de 1 dia
    DATA_INICIO_TESTE = datetime(2024, 7, 20, 0, 0, 0)
    DATA_FIM_TESTE = datetime(2024, 7, 21, 0, 0, 0)

    if API_KEY_TESTE:
        resultados_owm = obter_dados_openweathermap(API_KEY_TESTE, DATA_INICIO_TESTE, DATA_FIM_TESTE, LAT_TESTE, LON_TESTE)
        if resultados_owm:
            print(f"\nTotal de {len(resultados_owm)} registros do OpenWeatherMap encontrados.")
            print("Primeiro registro:", resultados_owm[0])
            print("Último registro:", resultados_owm[-1])
    else:
        print("\nChave de API 'OPENWEATHERMAP_API_KEY' não encontrada no arquivo .env para teste.")
