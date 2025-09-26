import config
import pandas as pd
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim

# Importa as funções dos provedores
from provedores.portal_inmet import obter_dados_portal_inmet # ATUALIZADO
from provedores.openweathermap import obter_dados_openweathermap
from provedores.stormglass import obter_dados_stormglass
from provedores.visualcrossing import obter_dados_visualcrossing
from provedores.wolfram import obter_dados_wolfram

def obter_entradas_usuario():
    """Solicita o intervalo de datas e o local ao usuário."""
    while True:
        try:
            local_str = input("Digite a cidade e estado (ex: Toledo, Parana): ")
            data_inicio_str = input("Digite a data de início (DD/MM/AAAA): ")
            data_fim_str = input("Digite a data de fim (DD/MM/AAAA): ")
            
            data_inicio = datetime.strptime(data_inicio_str, "%d/%m/%Y")
            data_fim = datetime.strptime(data_fim_str, "%d/%m/%Y")
            
            if data_inicio > data_fim:
                print("A data de início não pode ser posterior à data de fim.")
                continue
            
            # Adiciona 1 dia ao final para incluir o dia inteiro na busca
            data_fim_ajustada = data_fim + timedelta(days=1)
            return local_str, data_inicio, data_fim_ajustada
        except ValueError:
            print("Formato de data inválido. Por favor, use DD/MM/AAAA.")
        except Exception as e:
            print(f"Ocorreu um erro na entrada de dados: {e}")

def get_coords_from_location(location_name):
    """Obtém latitude e longitude a partir do nome de um local."""
    try:
        # Aumentei o timeout para evitar erros em redes lentas
        geolocator = Nominatim(user_agent="clima_app_agent", timeout=20)
        location = geolocator.geocode(location_name)
        if location:
            print(f"Coordenadas encontradas para '{location_name}': ({location.latitude:.4f}, {location.longitude:.4f})")
            return location.latitude, location.longitude
    except Exception as e:
        print(f"Não foi possível obter coordenadas para '{location_name}'. Usando valores padrão. Erro: {e}")
    return float(config.LATITUDE), float(config.LONGITUDE) # Retorna padrão em caso de falha

def salvar_dados_consolidados(dados_por_provedor, local):
    """Processa, mescla e salva os dados de todos os provedores em um único CSV."""
    if not any(dados_por_provedor.values()):
        print("\nNenhum dado foi coletado para salvar.")
        return

    lista_dfs = []
    for provedor, dados in dados_por_provedor.items():
        if not dados:
            continue
        
        df = pd.DataFrame(dados)
        # Identifica a coluna de data/hora, que pode ter nomes diferentes
        date_col = 'data_hora' if 'data_hora' in df.columns else 'data_consulta'
        if date_col not in df.columns:
            continue

        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        # PADRONIZA PARA 'NAIVE': Remove informações de fuso horário (timezone)
        # para evitar erros ao juntar DataFrames de APIs com e sem essa informação.
        df[date_col] = df[date_col].dt.tz_localize(None)
        df = df.dropna(subset=[date_col])
        df = df.set_index(date_col)

        # Renomeia todas as colunas de dados com o sufixo do provedor
        colunas_renomear = {col: f"{col}_{provedor.replace(' ', '')}" for col in df.columns if col not in ['provedor']}
        df = df.rename(columns=colunas_renomear)
        
        # Remove colunas que são apenas do provedor (já temos no nome da coluna)
        if 'provedor' in df.columns:
            df = df.drop(columns=['provedor'])
        
        lista_dfs.append(df)

    if not lista_dfs:
        print("\nNenhum dado válido para processar após a limpeza.")
        return

    # Concatena todos os DataFrames
    df_final = pd.concat(lista_dfs, axis=1)
    
    # Reamostra para frequência horária, calculando a média
    # Isso garante que todos os dados estejam alinhados de hora em hora.

    df_final = df_final.resample('h').mean().round(2)
    df_final.reset_index(inplace=True)

    nome_arquivo = f"dados_climaticos_{local.replace(', ', '_').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv"
    # Salva o DataFrame final em um arquivo CSV
    df_final.to_csv(nome_arquivo, index=False, encoding='utf-8-sig')
    print(f"\nDados consolidados e formatados salvos com sucesso em: {nome_arquivo}")

def main():
    """Função principal para orquestrar a coleta de dados."""
    local_nome, data_inicio, data_fim = obter_entradas_usuario()
    latitude, longitude = get_coords_from_location(local_nome)
    
    print(f"\nIniciando coleta de dados para '{local_nome}' de {data_inicio.strftime('%d/%m/%Y')} a {(data_fim - timedelta(days=1)).strftime('%d/%m/%Y')}...\n")

    dados_coletados = {}

    # Executa cada provedor e armazena os dados em um dicionário
    dados_coletados['PortalINMET'] = obter_dados_portal_inmet(data_inicio, data_fim, latitude, longitude)
    dados_coletados['OpenWeatherMap'] = obter_dados_openweathermap(config.OPENWEATHERMAP_API_KEY, data_inicio, data_fim, latitude, longitude)
    dados_coletados['StormGlass'] = obter_dados_stormglass(config.STORMGLASS_API_KEY, data_inicio, data_fim, latitude, longitude)
    dados_coletados['VisualCrossing'] = obter_dados_visualcrossing(config.VISUALCROSSING_API_KEY, data_inicio, data_fim, local_nome)
    
    # O WolframAlpha é consultado dia a dia
    dados_wolfram = []
    dias_no_intervalo = (data_fim - data_inicio).days
    for i in range(dias_no_intervalo):
        data_consulta = data_inicio + timedelta(days=i)
        dados_wolfram.extend(obter_dados_wolfram(config.WOLFRAM_API_KEY, data_consulta, local_nome))
    dados_coletados['WolframAlpha'] = dados_wolfram

    salvar_dados_consolidados(dados_coletados, local_nome)

if __name__ == "__main__":
    main()