import requests
import json
from datetime import datetime
from geopy.distance import geodesic

def obter_dados_inmet(data_inicio, data_fim, latitude, longitude):
    """
    Busca dados de estações meteorológicas do INMET próximas a uma coordenada para um período.

    Args:
        data_inicio (datetime): Data de início da busca.
        data_fim (datetime): Data de fim da busca.
        latitude (float): Latitude do local.
        longitude (float): Longitude do local.

    Returns:
        list: Uma lista de dicionários com os dados coletados.
    """
    print("--- Executando INMET ---")
    try:
        # 1. Obter a lista de todas as estações automáticas
        url_estacoes = "https://apitempo.inmet.gov.br/estacoes/T"
        response = requests.get(url_estacoes)
        response.raise_for_status()  # Lança exceção para erros HTTP
        estacoes = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar estações do INMET: {e}")
        return []
    except json.JSONDecodeError:
        print("Erro ao decodificar a resposta JSON das estações do INMET.")
        return []

    # 2. Filtrar estações próximas
    coordenadas_local = (latitude, longitude)
    estacoes_proximas = []
    for estacao in estacoes:
        try:
            lat_estacao = float(estacao['VL_LATITUDE'])
            lon_estacao = float(estacao['VL_LONGITUDE'])
            estacao_coords = (lat_estacao, lon_estacao)

            distancia_km = geodesic(coordenadas_local, estacao_coords).km

            if distancia_km < 100:  # Aumentei o raio para 100 km para garantir mais resultados
                estacoes_proximas.append(estacao)
        except (ValueError, TypeError, KeyError):
            continue

    if not estacoes_proximas:
        print("Nenhuma estação do INMET encontrada em um raio de 100 km.")
        return []

    # 3. Buscar e retornar dados das estações próximas
    dados_coletados = []
    for estacao in estacoes_proximas:
        codigo_estacao = estacao['CD_ESTACAO']
        url_dados = f"https://apitempo.inmet.gov.br/estacao/{data_inicio.strftime('%Y-%m-%d')}/{data_fim.strftime('%Y-%m-%d')}/{codigo_estacao}"

        try:
            response_dados = requests.get(url_dados)
            if response_dados.status_code == 200:
                dados = response_dados.json()
                if dados:
                    print(f"  - Estação {codigo_estacao} ({estacao.get('DC_NOME', 'N/A')}) tem dados.")
                    for item in dados:
                        dados_coletados.append({
                            'provedor': 'INMET',
                            'estacao_codigo': codigo_estacao,
                            'estacao_nome': estacao.get('DC_NOME', 'N/A'),
                            'data_hora': f"{item.get('DT_MEDICAO')} {item.get('HR_MEDICAO')}",
                            'temperatura_c': item.get('TEMP_INS'),
                            'umidade_relativa': item.get('UMID_INS'),
                            'pressao_hpa': item.get('PRES_INS'),
                            'velocidade_vento_ms': item.get('VETO_VEL'),
                        })
            else:
                # Silencioso para não poluir a saída com estações sem dados
                pass
        except (requests.exceptions.RequestException, json.JSONDecodeError):
            # Ignora erros de requisição ou JSON para uma única estação
            continue
            
    print(f"INMET: {len(dados_coletados)} registros encontrados.")
    return dados_coletados

# Bloco de teste
if __name__ == '__main__':
    # Para testar este módulo individualmente
    lat_teste = -24.73
    lon_teste = -53.74
    data_inicio_teste = datetime(2024, 7, 20)
    data_fim_teste = datetime(2024, 7, 21)

    resultados_inmet = obter_dados_inmet(data_inicio_teste, data_fim_teste, lat_teste, lon_teste)

    if resultados_inmet:
        print(f"\nTotal de {len(resultados_inmet)} registros do INMET encontrados.")
        # Imprime o primeiro e o último registro como exemplo
        print("Primeiro registro:", resultados_inmet[0])
        print("Último registro:", resultados_inmet[-1])
