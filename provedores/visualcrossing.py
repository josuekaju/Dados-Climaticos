import urllib.request
import urllib.parse
import csv
import codecs
import json
from datetime import datetime

def obter_dados_visualcrossing(api_key, data_inicio, data_fim, local):
    """
    Busca dados históricos do Visual Crossing para um período e local.

    Args:
        api_key (str): Chave da API do Visual Crossing.
        data_inicio (datetime): Data de início da busca.
        data_fim (datetime): Data de fim da busca.
        local (str): Nome do local (ex: "Toledo, PR").

    Returns:
        list: Uma lista de dicionários com os dados climaticos horários.
    """
    print("--- Executando Visual Crossing ---")
    if not api_key:
        print("Chave de API do Visual Crossing não configurada. Pulando...")
        return []

    start_date_str = data_inicio.strftime('%Y-%m-%d')
    end_date_str = data_fim.strftime('%Y-%m-%d')
    encoded_location = urllib.parse.quote(local)

    # Usaremos JSON para facilitar o parsing, em vez de CSV
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{encoded_location}/{start_date_str}/{end_date_str}?unitGroup=metric&include=hours&key={api_key}&contentType=json"

    dados_coletados = []
    try:
        response = urllib.request.urlopen(url)
        data = json.loads(response.read().decode('utf-8'))

        if 'days' in data:
            for day in data['days']:
                for hour in day.get('hours', []):
                    # Converte a data e a hora para um formato padrão
                    data_hora_str = f"{day['datetime']} {hour['datetime']}"
                    data_hora_obj = datetime.strptime(data_hora_str, '%Y-%m-%d %H:%M:%S')
                    
                    dados_coletados.append({
                        'provedor': 'VisualCrossing',
                        'data_hora': data_hora_obj.strftime('%Y-%m-%d %H:%M:%S'),
                        'temperatura_c': hour.get('temp'),
                        'umidade_relativa': hour.get('humidity'),
                        'pressao_hpa': hour.get('pressure'),
                        # A API retorna em km/h, convertemos para m/s para padronizar
                        'velocidade_vento_ms': float(hour.get('windspeed', 0)) / 3.6 if hour.get('windspeed') is not None else None,
                        'radiacao_solar_w_m2': hour.get('solarradiation')
                    })

        print(f"Visual Crossing: {len(dados_coletados)} registros encontrados.")
        return dados_coletados

    except urllib.error.HTTPError as e:
        error_info = e.read().decode()
        print(f'  - Erro na requisição ao Visual Crossing: {e.code} - {error_info}')
        return []
    except Exception as e:
        print(f"  - Ocorreu um erro inesperado no Visual Crossing: {e}")
        return []

# Bloco de teste
if __name__ == '__main__':
    from dotenv import load_dotenv
    import os
    from datetime import datetime

    load_dotenv()
    API_KEY_TESTE = os.getenv("VISUALCROSSING_API_KEY")
    LOCAL_TESTE = "Toledo, Parana"
    DATA_INICIO_TESTE = datetime(2024, 7, 20)
    DATA_FIM_TESTE = datetime(2024, 7, 21)

    if API_KEY_TESTE:
        resultados_vc = obter_dados_visualcrossing(API_KEY_TESTE, DATA_INICIO_TESTE, DATA_FIM_TESTE, LOCAL_TESTE)
        if resultados_vc:
            print(f"\nTotal de {len(resultados_vc)} registros do Visual Crossing encontrados.")
            print("Primeiro registro:", resultados_vc[0])
            print("Último registro:", resultados_vc[-1])
    else:
        print("\nChave de API 'VISUALCROSSING_API_KEY' não encontrada no arquivo .env para teste.")
