import wolframalpha
from datetime import datetime

def obter_dados_wolfram(api_key, data, local):
    """
    Busca dados de clima no WolframAlpha para uma data e local específicos.

    Args:
        api_key (str): Chave da API do WolframAlpha.
        data (datetime): A data para a consulta.
        local (str): O nome do local (ex: "Toledo, Brazil").

    Returns:
        list: Uma lista contendo um dicionário com a informação de clima encontrada.
    """
    print("--- Executando WolframAlpha ---")
    if not api_key:
        print("Chave de API do WolframAlpha não configurada. Pulando...")
        return []

    try:
        cliente = wolframalpha.Client(api_key)
        data_str = data.strftime("%B %d, %Y")
        consulta = f"weather in {local} on {data_str}"
        print(f"  - Consultando WolframAlpha com: '{consulta}'")
 
        resposta = cliente.query(consulta)
        print(f"Resposta do WolframAlpha: {resposta}")

        dados_coletados = []
        for pod in resposta.pods:
            pod_title_lower = pod.title.lower()
            # Lógica combinada: procura por 'weather', 'forecast' ou 'temperature'
            if ("weather" in pod_title_lower or "forecast" in pod_title_lower or "temperature" in pod_title_lower) and ("current" not in pod_title_lower):
                dados_coletados.append({
                    'improvedor': 'WolframAlpha',
                    'data_consulta': data.strftime('%Y-%m-%d'),
                    'titulo': pod.title,
                    'texto_resultado': pod.text
                })
        
        if not dados_coletados:
            print("  - Nenhuma informação de clima relevante encontrada no WolframAlpha.")
        else:
            print(f"WolframAlpha: {len(dados_coletados)} seções de informação encontradas.")
            
        return dados_coletados

    except StopIteration:
        print(f"  - WolframAlpha não retornou resultados para a consulta.")
        return []
    except Exception as e:
          # A biblioteca do WolframAlpha pode falhar silenciosamente ou retornar um erro vazio
          # mesmo com uma chave de API válida, possivelmente devido a uma incompatibilidade
          # ou por não encontrar dados para a consulta específica.
        print(f"  - Erro na requisição ao WolframAlpha: {e}")
        return []

# Bloco de teste, essa parte é apenas para teste executando diretamente esse código, essa parte é ignorada ao rodar o main.py
if __name__ == '__main__':
    from dotenv import load_dotenv
    import os

    load_dotenv()
    API_KEY_TESTE = os.getenv("WOLFRAM_API_KEY")
    LOCAL_TESTE = "Toledo, Parana"
    DATA_TESTE = datetime(2024, 7, 20)

    if API_KEY_TESTE:
        resultados_wolfram = obter_dados_wolfram(API_KEY_TESTE, DATA_TESTE, LOCAL_TESTE)
        if resultados_wolfram:
            print("\nResultados do WolframAlpha:")
            for res in resultados_wolfram:
                print(res)
    else:
        print("\nChave de API 'WOLFRAM_API_KEY' não encontrada no arquivo .env para teste.")
