import config
import pandas as pd
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
import os
import json
from relatorio_melhorado import gerar_relatorio_historico_obras

# Importa as funções dos provedores
from provedores.portal_inmet import obter_dados_portal_inmet
from provedores.openweathermap import obter_dados_openweathermap
from provedores.stormglass import obter_dados_stormglass
from provedores.visualcrossing import obter_dados_visualcrossing
from provedores.wolfram import obter_dados_wolfram

def obter_entradas_usuario():
    """Solicita ao usuário a cidade, o período de análise e o número de anos para o histórico."""
    print("--- Análise Climática Histórica para Construção Civil ---")
    while True:
        try:
            local_str = input("Digite a cidade e estado (ex: Toledo, Parana): ")
            data_inicio_str = input("Digite a data de início (DD/MM): ")
            data_fim_str = input("Digite a data de fim (DD/MM): ")
            num_anos_str = input("Digite o número de anos para analisar (ex: 10): ")
            
            dia_inicio, mes_inicio = map(int, data_inicio_str.split('/'))
            dia_fim, mes_fim = map(int, data_fim_str.split('/'))
            num_anos = int(num_anos_str)
            
            if num_anos <= 0:
                print("O número de anos deve ser pelo menos 1.")
                continue
            
            return local_str, (dia_inicio, mes_inicio), (dia_fim, mes_fim), num_anos

        except ValueError:
            print("Formato de data inválido. Por favor, use DD/MM para datas e um numero inteiro para anos.")
        except Exception as e:
            print(f"Ocorreu um erro inesperado durante a entrada de dados: {e}")

def get_coords_from_location(location_name):
    """Obtém latitude e longitude a partir do nome de um local."""
    try:
        geolocator = Nominatim(user_agent="clima_app_agent", timeout=20)
        location = geolocator.geocode(location_name)
        if location:
            print(f"Coordenadas encontradas para '{location_name}': ({location.latitude:.4f}, {location.longitude:.4f})")
            return location.latitude, location.longitude
    except Exception as e:
        print(f"Não foi possível obter coordenadas para '{location_name}'. Usando valores padrão. Erro: {e}")
    return float(config.LATITUDE), float(config.LONGITUDE)

def salvar_dados_consolidados(todos_os_dados_por_provedor, local):
    """Processa, mescla e salva os dados de todos os provedores e anos em um único CSV."""
    if not todos_os_dados_por_provedor:
        print("\nNenhum dado foi coletado para salvar.")
        return None, None

    dados_agregados = {}
    for dados_ano in todos_os_dados_por_provedor:
        for provedor, dados in dados_ano.items():
            if provedor not in dados_agregados:
                dados_agregados[provedor] = []
            if dados:
                dados_agregados[provedor].extend(dados)

    lista_dfs = []
    for provedor, dados in dados_agregados.items():
        if not dados:
            continue
        
        df = pd.DataFrame(dados)
        df['data_hora'] = pd.to_datetime(df['data_hora'], errors='coerce')
        
        # Remove timezone para evitar conflitos na concatenação
        if df['data_hora'].dt.tz is not None:
            df['data_hora'] = df['data_hora'].dt.tz_localize(None)
            
        df = df.dropna(subset=['data_hora'])
        df = df.set_index('data_hora')

        colunas_renomear = {col: f"{col}_{provedor.replace(' ', '')}" for col in df.columns if col != 'provedor'}
        df = df.rename(columns=colunas_renomear)
        
        if 'provedor' in df.columns:
            df = df.drop(columns=['provedor'])
        
        lista_dfs.append(df)

    if not lista_dfs:
        print("\nNenhum dado válido para processar após a limpeza.")
        return None, None

    df_final = pd.concat(lista_dfs, axis=1)
    df_final = df_final.sort_index()
    df_final.dropna(how='all', inplace=True)
    df_final.reset_index(inplace=True)

    nome_arquivo = f"dados_climaticos_{local.replace(', ', '_').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv"
    
    df_final.to_csv(nome_arquivo, index=False, encoding='utf-8-sig')
    print(f"\nDados consolidados e formatados salvos com sucesso em: {nome_arquivo}")

    return df_final, nome_arquivo

def orquestrar_coleta_e_analise(local_nome, dia_inicio, mes_inicio, dia_fim, mes_fim, num_anos, api_keys, progress_callback=None, preset_obra=None):
    """
    Função central que orquestra toda a coleta, processamento e análise de dados.
    Pode ser chamada tanto pelo main.py (CLI) quanto pelo gui.py (GUI).
    """
    latitude, longitude = get_coords_from_location(local_nome)
    local_info = {"nome": local_nome, "lat": latitude, "lon": longitude}

    ano_atual = datetime.now().year
    ano_inicial_loop = ano_atual

    hoje = datetime.now()
    data_fim_periodo_neste_ano = datetime(ano_atual, mes_fim, dia_fim)
    if data_fim_periodo_neste_ano > hoje:
        if progress_callback:
            progress_callback(f"AVISO: Período em {ano_atual} ainda não ocorreu. Análise iniciará em {ano_atual - 1}.")
        ano_inicial_loop = ano_atual - 1

    todos_os_dados_por_provedor = []

    for i in range(num_anos):
        ano_alvo = ano_inicial_loop - i
        if progress_callback:
            progress_callback(f"Coletando dados para {ano_alvo}... ({i+1}/{num_anos})")
        else:
            print(f"--- Buscando dados para o ano de {ano_alvo} ---")

        try:
            data_inicio = datetime(ano_alvo, mes_inicio, dia_inicio)
            data_fim = datetime(ano_alvo, mes_fim, dia_fim)
            
            if data_inicio > data_fim:
                data_fim = datetime(ano_alvo + 1, mes_fim, dia_fim)

        except ValueError as e:
            msg = f"  - Data inválida para o ano {ano_alvo} (ex: 29/02). Pulando... Erro: {e}"
            if progress_callback: progress_callback(msg)
            else: print(msg)
            continue

        dados_coletados_ano = {}
        provedores = {
            'PortalINMET': lambda: obter_dados_portal_inmet(data_inicio, data_fim, latitude, longitude),
            'OpenWeatherMap': lambda: obter_dados_openweathermap(api_keys.get('openweathermap'), data_inicio, data_fim, latitude, longitude),
            'StormGlass': lambda: obter_dados_stormglass(api_keys.get('stormglass'), data_inicio, data_fim, latitude, longitude),
            'VisualCrossing': lambda: obter_dados_visualcrossing(api_keys.get('visualcrossing'), data_inicio, data_fim, local_nome),
            'Wolfram': lambda: obter_dados_wolfram(api_keys.get('wolfram'), data_inicio, local_nome) if api_keys.get('wolfram') else []
        }

        for nome_provedor, funcao_provedor in provedores.items():
            cache_filename = f"cache/{nome_provedor}_{local_nome.replace(', ', '_')}_{ano_alvo}.json"
            
            if os.path.exists(cache_filename):
                msg = f"  - Lendo dados do {nome_provedor} do cache..."
                if not progress_callback: print(msg)
                with open(cache_filename, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                dados_coletados_ano[nome_provedor] = dados
            else:
                dados = funcao_provedor()
                dados_coletados_ano[nome_provedor] = dados
                if dados:
                    with open(cache_filename, 'w', encoding='utf-8') as f:
                        json.dump(dados, f, ensure_ascii=False, indent=4)
        
        todos_os_dados_por_provedor.append(dados_coletados_ano)

    if progress_callback:
        progress_callback("Processando e salvando dados...")
    df_final, nome_arquivo_csv = salvar_dados_consolidados(todos_os_dados_por_provedor, local_nome)

    if df_final is not None and not df_final.empty:
        if progress_callback:
            progress_callback("Gerando relatório contextual...")
        gerar_relatorio_historico_obras(df_final, nome_arquivo_csv, local_info, preset_obra)
        return True, nome_arquivo_csv
    else:
        return False, "Nenhum dado foi coletado para análise."

def main():
    """Função principal para orquestrar a coleta de dados históricos via CLI."""
    if not os.path.exists('cache'):
        os.makedirs('cache')

    local_nome, (dia_inicio, mes_inicio), (dia_fim, mes_fim), num_anos = obter_entradas_usuario()
    
    print(f"\nIniciando coleta de dados para '{local_nome}' para o período de {dia_inicio:02d}/{mes_inicio:02d} a {dia_fim:02d}/{mes_fim:02d} nos últimos {num_anos} anos...\n")

    api_keys_cli = {
        "openweathermap": config.OPENWEATHERMAP_API_KEY,
        "stormglass": config.STORMGLASS_API_KEY,
        "visualcrossing": config.VISUALCROSSING_API_KEY,
        "wolfram": config.WOLFRAM_API_KEY
    }

    sucesso, resultado = orquestrar_coleta_e_analise(local_nome, dia_inicio, mes_inicio, dia_fim, mes_fim, num_anos, api_keys_cli)
    if not sucesso:
        print(f"\nAVISO: {resultado}")

if __name__ == "__main__":
    main() 
