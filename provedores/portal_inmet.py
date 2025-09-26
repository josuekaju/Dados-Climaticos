import requests
import json
from datetime import datetime
from geopy.distance import geodesic

# URL da API 'escondida' que lista todas as estações de todas as entidades
URL_TODAS_ESTACOES = "https://apimapas.inmet.gov.br/estacoes"

# URL da API que busca os dados de uma estação específica
URL_DADOS_ESTACAO = "https://apitempo.inmet.gov.br/estacao"

def _get_all_stations():
    """Busca e retorna uma lista plana de todas as estações de todas as entidades."""
    try:
        response = requests.get(URL_TODAS_ESTACOES, timeout=20)
        response.raise_for_status()
        data = response.json()
        
        all_stations = []
        # O JSON é aninhado, precisamos iterar para achatar a lista
        for tipo_estacao in data['estacoes'].values(): # ex: 'automaticas', 'convencionais'
            for regiao in tipo_estacao.values(): # ex: 'N', 'NE', 'S'
                all_stations.extend(regiao)
        return all_stations
    except Exception as e:
        print(f"  - Erro ao buscar a lista completa de estações do portal INMET: {e}")
        return None

def obter_dados_portal_inmet(data_inicio, data_fim, latitude, longitude):
    """
    Busca dados de estações (de todas as entidades) próximas a uma coordenada.
    """
    print("--- Executando Portal INMET  ---")
    
    stations = _get_all_stations()
    if not stations:
        return []

    # Filtra as estações próximas (ex: raio de 100 km)
    coordenadas_local = (latitude, longitude)
    estacoes_proximas = []
    for estacao in stations:
        if estacao.get('entidade') != 'INMET':
            continue

        try:
            lat_estacao = float(estacao['latitude'])
            lon_estacao = float(estacao['longitude'])
            distancia = geodesic(coordenadas_local, (lat_estacao, lon_estacao)).km
            if distancia <= 100:
                estacao['distancia'] = distancia
                estacoes_proximas.append(estacao)
        except (ValueError, TypeError, KeyError):
            continue

    if not estacoes_proximas:
        print("  - Nenhuma estação encontrada em um raio de 100 km.")
        return []

    # Ordena as estações encontradas pela distância (da mais próxima para a mais distante)
    estacoes_proximas.sort(key=lambda x: x['distancia'])
    print(f"  - {len(estacoes_proximas)} estações encontradas. Testando a mais próxima primeiro...")

    # Tenta buscar dados, começando pela estação mais próxima
    dados_coletados = []
    for estacao in estacoes_proximas:
        codigo_estacao = estacao['codigo']
        nome_estacao = estacao['nome']
        entidade = estacao['entidade']
        dist = estacao['distancia']

        url_dados = f"{URL_DADOS_ESTACAO}/{data_inicio.strftime('%Y-%m-%d')}/{data_fim.strftime('%Y-%m-%d')}/{codigo_estacao}"
        
        try:
            response_dados = requests.get(url_dados, timeout=20)
            if response_dados.status_code == 200:
                dados = response_dados.json()
                if dados:
                    print(f"  - SUCESSO! Dados encontrados para a estação {nome_estacao} ({entidade}) a {dist:.1f} km.")
                    for item in dados:
                        dados_coletados.append({
                            'provedor': 'PortalINMET',
                            'estacao_codigo': codigo_estacao,
                            'estacao_nome': nome_estacao,
                            'entidade': entidade,
                            'data_hora': f"{item.get('DT_MEDICAO')} {item.get('HR_MEDICAO')}",
                            'temperatura_c': item.get('TEMP_INS'),
                            'umidade_relativa': item.get('UMID_INS'),
                            'pressao_hpa': item.get('PRES_INS'),
                            'velocidade_vento_ms': item.get('VETO_VEL'),
                            'chuva_mm': item.get('CHUVA'),
                            'radiacao_solar_kj_m2': item.get('RAD_GLO'),
                        })
                    # Se encontramos dados na estação mais próxima, paramos a busca
                    break 
        except requests.exceptions.RequestException as e:
            print(f"  - Falha ao contatar a estação {nome_estacao} ({entidade}): {e}. Tentando a próxima...")
            continue

    print(f"Portal INMET: {len(dados_coletados)} registros encontrados.")
    return dados_coletados

# Bloco de teste
if __name__ == '__main__':
    lat_teste = -24.73
    lon_teste = -53.74
    data_inicio_teste = datetime(2024, 7, 20)
    data_fim_teste = datetime(2024, 7, 21)

    resultados = obter_dados_portal_inmet(data_inicio_teste, data_fim_teste, lat_teste, lon_teste)
    if resultados:
        print(f"\nTotal de {len(resultados)} registros encontrados.")
        df_teste = pd.DataFrame(resultados)
        print(df_teste.head())
