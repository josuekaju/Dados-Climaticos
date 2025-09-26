"""
Módulo de Configuração.

Este arquivo carrega as variáveis de ambiente definidas no arquivo `.env`.
Ele centraliza o acesso a todas as chaves de API e outras configurações,
permitindo que o resto do programa as acesse de forma consistente.

IMPORTANTE: O arquivo `.env` é privado e não deve ser enviado para o GitHub.
Ele contém informações sensíveis (chaves de API).
"""
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env para o ambiente do sistema
load_dotenv()

# --- Chaves de API ---
# Carrega as chaves de API do ambiente. Retorna None se não forem encontradas.
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
STORMGLASS_API_KEY = os.getenv("STORMGLASS_API_KEY")
VISUALCROSSING_API_KEY = os.getenv("VISUALCROSSING_API_KEY")
WOLFRAM_API_KEY = os.getenv("WOLFRAM_API_KEY")

# --- Configurações Padrão ---
# Coordenadas padrão (usadas como fallback caso a geocodificação falhe)
LATITUDE = os.getenv("LATITUDE", "-24.73")
LONGITUDE = os.getenv("LONGITUDE", "-53.74")
