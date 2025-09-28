# 🌦️ Sistema de Análise Climática para Construção Civil

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Executável](https://img.shields.io/badge/Executável-.exe-brightgreen.svg)]()
[![GUI](https://img.shields.io/badge/Interface-Tkinter-orange.svg)]()

## 📋 Descrição

Sistema profissional de análise climática histórica desenvolvido especificamente para **planejamento de obras civis**. Coleta dados de múltiplos provedores meteorológicos e gera relatórios detalhados com probabilidades diárias de chuva e recomendações específicas para diferentes tipos de obra.

### 🎯 **PARA USUÁRIOS FINAIS:**

**📦 Baixe apenas o arquivo `.exe` e execute diretamente no Windows - não precisa instalar Python ou programas de programação!**

### 👥 Público-Alvo

- **Engenheiros Civis** 	(sem conhecimento de programação)
- **Arquitetos** 			(usuários finais)
- **Mestres de Obra** 		(operação simples)
- **Gerentes de Projeto** 	(relatórios prontos)

## 🚀 **DUAS FORMAS DE USO:**

### 📦 **1. EXECUTÁVEL (.exe) - RECOMENDADO PARA USUÁRIOS FINAIS**

#### Como usar:

```
1. 📥 Baixe: ClimaObras.exe
2. 🖱️ Execute: Clique duas vezes no arquivo
3. ⚙️ Configure: Suas chaves de API na interface
4. 📊 Analise: Seus dados sem programação!
```

#### ✅ **VANTAGENS:**

- ✅ Não precisa instalar Python
- ✅ Interface gráfica amigável
- ✅ Funciona em qualquer Windows
- ✅ Um clique para executar
- ✅ Configuração visual das APIs
- ✅ Barra de progresso em tempo real

### 💻 **2. CÓDIGO FONTE - PARA DESENVOLVEDORES**

#### Instalação:

```bash
# Clone o repositório
git clone https://github.com/josuekaju/Dados-Climaticos.git
cd Dados-Climaticos

# Crie ambiente virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Instale dependências
pip install -r requirements.txt
```

#### Executar:

```bash
python gui.py    # Interface gráfica
python main.py   # Linha de comando
```

## 🔧 **CRIAR EXECUTÁVEL (.exe)**

Para desenvolvedores que querem distribuir:

```bash
# Instale PyInstaller
pip install pyinstaller

# Gere o executável
pyinstaller --onefile --windowed --name="ClimaObras" gui.py

# Arquivo gerado em: dist/ClimaObras.exe
```

**Opções do PyInstaller:**

- `--onefile`: Arquivo único
- `--windowed`: Sem console (interface gráfica)
- `--name`: Nome do executável

## ✨ **FUNCIONALIDADES**

### 🔍 **Coleta Multi-Provedor:**

- **Portal INMET** (dados oficiais Brasil)
- **OpenWeatherMap** (histórico global - múltiplas fontes)
- **StormGlass** (dados oceânicos e climatológicos)
- **Visual Crossing** (dados detalhados - boa API gratuita)
- **Wolfram Alpha** (análises computacionais - múltiplas fontes)

### 📊 **Análises:**

- ✅ Probabilidades diárias de chuva
- ✅ Análise de consistência entre anos
- ✅ Métricas de intensidade e volume
- ✅ Sequências consecutivas de chuva
- ✅ Análise de temperatura e vento
- ✅ Indicadores de umidade alta (≥90%)

### 🏗️📄 **Relatórios:**

- 📄 Relatórios estruturados em `.txt`
- 🎯 Recomendações por tipo de obra
- ⚠️ Disclaimers legais importantes
- 📈 Classificação de risco por dia
- 🔧 Orientações específicas para construção

### 💾 **Sistema de Cache Inteligente:**

- Cache automático por provedor/ano
- Evita requisições desnecessárias
- Dados salvos em formato JSON
- Otimização de performance

## 🔑 **CONFIGURAÇÃO DE APIs**

### **Na Interface Gráfica (Recomendado):**

1. Abra o programa
2. Clique em "⚙️ Configurar APIs"
3. Cole suas chaves nos campos
4. Clique em "💾 Salvar"

### **No Código (config.py):**

```python
OPENWEATHERMAP_API_KEY = "sua_chave"
STORMGLASS_API_KEY = "sua_chave"
VISUALCROSSING_API_KEY = "sua_chave"
WOLFRAM_API_KEY = "sua_chave"  
```

### **Obter Chaves Gratuitas:**

| Provedor                  | Link                                                                      | Plano Gratuito   | Observações                  |
| ------------------------- | ------------------------------------------------------------------------- | ---------------- | ------------------------------ |
| **OpenWeatherMap**  | [openweathermap.org/api](https://openweathermap.org/api)                     | 1.000 calls/dia  | Requer cartão para histórico |
| **StormGlass**      | [stormglass.io](https://stormglass.io/)                                      | 50 calls/dia     | Funciona bem                   |
| **Visual Crossing** | [visualcrossing.com/weather-api](https://www.visualcrossing.com/weather-api) | 1.000 calls/dia  | Recomendado                    |
| **Wolfram Alpha**   | [developer.wolframalpha.com](https://developer.wolframalpha.com/)            | 2.000 calls/mês | Opcional                       |

## 📁 **ESTRUTURA DO PROJETO**

```
clima-obras/
├── 📄 main.py                 # CLI principal
├── 🖥️ gui.py                  # Interface gráfica
├── 📊 relatorio_melhorado.py  # Geração de relatórios
├── ⚙️ config.py               # Configurações
├── 📋 requirements.txt        # Dependências
├── 📖 README.md              # Este arquivo
├── 📂 provedores/            # Módulos de APIs
│   ├── portal_inmet.py
│   ├── openweathermap.py
│   ├── stormglass.py
│   ├── visualcrossing.py
│   └── wolfram.py
├── 📂 cache/                 # Cache automático
└── 📂 dist/                  # Executável gerado
```

## 📖 **EXEMPLO DE USO**

### **Interface Gráfica:**

1. Execute `ClimaObras.exe` ou `python gui.py`
2. Preencha os campos:
   - **Cidade:** Toledo, Parana
   - **Data início:** 23/09
   - **Data fim:** 26/09
   - **Anos:** 5
3. Clique em "📊 Iniciar Análise"
4. Aguarde a barra de progresso
5. Clique em "📄 Abrir Relatório"

### **Linha de Comando:**

```bash
python main.py (python gui.py para interface grafica)
```

**Entrada:**

```
Cidade: Toledo, Parana
Data início: 23/09
Data fim: 26/09
Anos: 5
```

**Saída:**

- `dados_climaticos_Toledo_Parana_20250927.csv`
- `dados_climaticos_Toledo_Parana_20250927_relatorio_historico.txt`

## 📊 **EXEMPLO DE RELATÓRIO GERADO**

```
================================================================================
RELATÓRIO HISTÓRICO CLIMÁTICO PARA PLANEJAMENTO DE OBRAS resumido
================================================================================

⚠️  IMPORTANTE: Dados históricos - NÃO constitui previsão meteorológica

📅 Data de geração: 27/09/2025 às 17:04

🏗️  RESUMO EXECUTIVO PARA OBRAS:
• Período analisado: de 23/09 a 26/09
• Total de dias no histórico: 28 (7 anos)
• Probabilidade geral de chuva: 65.0%
• Dias com precipitação: 18 de 28 dias
• Dias com umidade > 90%: 12 de 28 dias
• Consistência entre anos: 94.0%

🌡️  ANÁLISE DE TEMPERATURA E VENTO:
----------------------------------------
• Temperatura Média: 23.5°C (Min: 8.6°C, Max: 39.0°C)
• Dias com calor (> 30°C): 12 dias
• Dias com frio (< 10°C): 4 dias
• Velocidade Média do Vento: 3.0 m/s
• Rajada Máxima de Vento: 16.7 m/s

📅 PROBABILIDADES DIÁRIAS PARA PLANEJAMENTO:
 23/09 |  80.0% | 🔴 ALTO - Evitar atividades externas
 24/09 |  20.0% | 🟡 MÉDIO - Planejar cobertura
 25/09 |  10.0% | ✅ FAVORÁVEL - Condições adequadas
 26/09 |  16.7% | 🟢 BAIXO - Monitorar previsão

🔧 RECOMENDAÇÕES POR TIPO DE OBRA:
• CONCRETO: Evitar concretagem com prob. > 20%
• PINTURA: Não pintar com umidade > 85% ou prob. > 15%
• ALVENARIA: Proteger materiais com prob. > 25%
• TERRAPLANAGEM: Suspender com prob. > 30%
• COBERTURA: Priorizar em dias com prob. < 10%
```

## 🛠️ **DEPENDÊNCIAS**

```txt
pandas>=1.5.0
geopy>=2.3.0
requests>=2.28.0
wolframalpha>=5.0.0
urllib3>=1.26.0
```


## ⚠️ **AVISOS IMPORTANTES:**

- ⚠️ **Dados Históricos:** NÃO constitui previsão meteorológica oficial
- ⚠️ **APIs Gratuitas:** Limitações de requisições diárias
- ⚠️ **Precisão:** Varia conforme disponibilidade de dados regionais

### **Recomendações:**

- ✅ Use sempre em conjunto com previsão meteorológica atual
- ✅ Consulte profissionais especializados para decisões críticas
- ✅ Mantenha as chaves de API atualizadas
- ✅ Verifique os limites diários das APIs

### **Próximas Versões:**

- 🔄 Suporte a mais provedores
- 🔄 Análises estatísticas avançadas
- 🔄 Exportação para Excel
- 🔄 Gráficos interativos

## 📄 **LICENÇA**

MIT License - veja [LICENSE](LICENSE) para detalhes.

**🇧🇷 Desenvolvido para a comunidade da construção civil brasileira**

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/josuekaju/Dados-Climaticos)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
