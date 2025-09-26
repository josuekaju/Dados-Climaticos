# Dados-Climaticos
Coletor de dados climáticos para múltiplas APIs
# Coletor de Dados Climáticos Multi-Provedor

Este projeto é um script em Python robusto e modular, projetado para coletar dados meteorológicos históricos de múltiplas fontes (APIs), consolidar as informações em um formato consistente e salvar o resultado em um único arquivo CSV. Ele foi desenvolvido para ser flexível, permitindo que o usuário especifique a cidade e o intervalo de datas desejado para a coleta.

## Funcionalidades Principais

- **Múltiplos Provedores:** Coleta dados de diversas fontes para garantir a maior quantidade de informação possível.
- **Entrada de Usuário Flexível:** Solicita ao usuário a cidade, estado e o intervalo de datas (início e fim) para a busca.
- **Geocodificação Automática:** Converte o nome da cidade em coordenadas (latitude e longitude) para as APIs que as exigem.
- **Consolidação Inteligente:** Agrega todos os dados coletados em uma única tabela, com os seguintes tratamentos:
  - Os dados são reamostrados e alinhados em intervalos de 1 hora.
  - Cada coluna de dado recebe um sufixo com o nome do provedor (ex: `temperatura_c_VisualCrossing`).
  - O resultado final é salvo em um arquivo `.csv` nomeado com o local e a data da coleta.
- **Estrutura Modular:** O código é organizado com um provedor por arquivo, facilitando a manutenção e a adição de novas fontes de dados.

## Estrutura do Projeto

A organização dos arquivos e diretórios do projeto é a seguinte:

```
clima/
├── .venv/                   # Diretório do ambiente virtual Python
├── provedores/                # Módulos para cada fonte de dados
│   ├── __init__.py
│   ├── portal_inmet.py
│   ├── openweathermap.py
│   ├── stormglass.py
│   ├── visualcrossing.py
│   └── wolfram.py
├── .env                       # Arquivo para armazenar as chaves de API (NÃO ENVIAR PARA O GITHUB)
├── config.py                # Carrega as configurações e chaves do arquivo .env
├── main.py                  # Script principal que orquestra a execução
├── requirements.txt         # Lista de dependências do projeto
└── README.md                # 
```

## Como Usar

### 1. Pré-requisitos

- Python 3.8 ou superior.

### 2. Instalação

1. **Clone o repositório:**

   ```bash
   git clone <url-do-seu-repositorio>
   cd clima
   ```
2. **Crie e ative um ambiente virtual:**

   ```bash
   # Criar o ambiente
   python -m venv .venv

   # Ativar no Windows
   .venv\Scripts\activate
   ```
3. **Instale as dependências:**

   ```bash
   pip install -r requirements.txt
   ```

### 3. Configuração das Chaves de API

O projeto requer chaves de API para funcionar. Você precisará criá-las nos sites dos respectivos provedores.

1. Na raiz do projeto, crie um arquivo chamado `.env`.
2. Adicione as seguintes linhas ao arquivo `.env`, substituindo `sua_chave_aqui` pelas chaves que você obteve:

   ```
   OPENWEATHERMAP_API_KEY="sua_chave_aqui"
   STORMGLASS_API_KEY="sua_chave_aqui"
   VISUALCROSSING_API_KEY="sua_chave_aqui"
   WOLFRAM_API_KEY="sua_chave_aqui"
   ```
3. **Links para obter as chaves de API:**

   - **Visual Crossing:** [Weather Data Services](https://www.visualcrossing.com/weather-api) (Plano gratuito mais generoso)
   - **StormGlass:** [Storm Glass API](https://stormglass.io/) (Clique em "Get Free API Key")
   - **OpenWeatherMap:** [OpenWeatherMap APIs](https://openweathermap.org/api) (Requer assinatura com cartão para dados históricos)
   - **WolframAlpha:** [Wolfram|Alpha Developer Portal](https://products.wolframalpha.com/api)

### 4. Execução

Com o ambiente virtual ativado, execute o script principal:

```bash
python main.py
```

O programa solicitará a cidade, data de início e data de fim, e ao final da execução, gerará um arquivo CSV com os dados consolidados.

## Resumo da Situação dos Provedores

| Provedor                  | Funciona?               | Motivo                                                                    |
| :------------------------ | :-------------------------------- | :------------------------------------------------------------------------ |
| **Visual Crossing** | **Sim, perfeitamente.**     | Plano gratuito generoso (1.000 resultados/dia) e API robusta.             |
| **StormGlass**      | **Sim, mas com limites.**   | Funciona bem, mas limitado a 10 chamadas por dia.                         |
| **INMET**           | **Parcialmente.**           | Funciona, mas apenas para estações do próprio INMET, nao cobre todo territorio nacional.                   |
| **OpenWeatherMap**  | **Não (para histórico).** | O plano gratuito exige assinatura com cartão para dados históricos.     |
| **WolframAlpha**    | **Não.**                   | API faz a busca mas Não retorna dados, funcionava a alguns meses atrás. |
