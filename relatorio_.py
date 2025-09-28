import pandas as pd
from datetime import datetime

def gerar_relatorio_historico_obras(df, caminho_arquivo_csv, local_info, preset_obra=None):
    """Gera relatório histórico profissional focado em planejamento de obras."""
    
    local_nome = local_info.get("nome", "N/A")
    relatorio_linhas = [
        "=" * 80,
        "RELATÓRIO HISTÓRICO CLIMÁTICO PARA PLANEJAMENTO DE OBRAS",
        "=" * 80,
        "",
        "⚠️  IMPORTANTE: Este relatório apresenta análise de dados históricos",
        "baseados em registros de anos anteriores. NÃO constitui previsão",
        "meteorológica e deve ser usado apenas como referência para",
        "planejamento de obras civis.",
        "",
        f"� Localização: {local_nome}",
        f"�📅 Data de geração: {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
        ""
    ]
    
    # Identifica colunas de dados
    coluna_chuva = None
    prioridade_colunas = ['chuva_mm_VisualCrossing', 'chuva_mm_StormGlass', 
                         'chuva_mm_PortalINMET', 'chuva_mm_OpenWeatherMap', 'chuva_mm_Wolfram']
    for col in prioridade_colunas:
        if col in df.columns and df[col].notna().any():
            coluna_chuva = col
            break

    colunas_umidade = [col for col in df.columns if 'umidade' in col.lower() or 'humidity' in col.lower()]
    coluna_umidade = colunas_umidade[0] if colunas_umidade else None

    # Identifica colunas de temperatura e vento
    coluna_temp = next((col for col in df.columns if 'temperatura_c' in col), None)
    coluna_vento = next((col for col in df.columns if 'velocidade_vento_ms' in col), None)
    coluna_rajada = next((col for col in df.columns if 'rajada_vento_ms' in col), None)

    nome_arquivo_relatorio = caminho_arquivo_csv.replace('.csv', '_relatorio_historico.txt')

    if not coluna_chuva:
        relatorio_linhas.extend([
            "❌ AVISO: Dados de precipitação não disponíveis.",
            "Recomenda-se verificar configurações das APIs."
        ])
        with open(nome_arquivo_relatorio, 'w', encoding='utf-8') as f:
            f.write("\n".join(relatorio_linhas))
        return

    relatorio_linhas.extend([
        "📊 FONTE DE DADOS:",
        f"• Precipitação: {coluna_chuva.replace('_', ' ').title()}",
        f"• Umidade: {coluna_umidade.replace('_', ' ').title() if coluna_umidade else 'Não disponível'}",
        ""
    ])

    # Processamento dos dados
    df['data_hora'] = pd.to_datetime(df['data_hora'])
    chuva_diaria = df.set_index('data_hora').resample('D')[coluna_chuva].sum().dropna()

    if chuva_diaria.empty:
        relatorio_linhas.append("❌ Dados insuficientes para análise.")
        with open(nome_arquivo_relatorio, 'w', encoding='utf-8') as f:
            f.write("\n".join(relatorio_linhas))
        return

    # Define o período baseado nos dados reais
    data_inicio_real = chuva_diaria.index.min()
    data_fim_real = chuva_diaria.index.max()
    periodo_sazonal_str = f"de {data_inicio_real.strftime('%d/%m')} a {data_fim_real.strftime('%d/%m')}"

    # Cálculos principais
    total_dias = len(chuva_diaria)
    dias_com_chuva = (chuva_diaria > 0.1).sum()
    prob_geral = (dias_com_chuva / total_dias) * 100 if total_dias > 0 else 0
    
    # Análise de umidade
    dias_umidade_alta = 0
    if coluna_umidade:
        df_umidade = df.set_index('data_hora').resample('D')[coluna_umidade].max().dropna()
        dias_umidade_alta = (df_umidade >= 90).sum()
    
    # Estatísticas detalhadas
    chuva_dias_chuvosos = chuva_diaria[chuva_diaria > 0.1]
    media_mm = chuva_dias_chuvosos.mean() if not chuva_dias_chuvosos.empty else 0
    total_mm = chuva_diaria.sum()
    max_mm = chuva_diaria.max()
    dia_max = chuva_diaria.idxmax().strftime('%d/%m/%Y') if max_mm > 0 else "N/A"
    
    anos_com_chuva = chuva_diaria[chuva_diaria > 0.1].index.year.nunique()
    total_anos = chuva_diaria.index.year.nunique()
    consistencia = (anos_com_chuva / total_anos) * 100 if total_anos > 0 else 0

    # Sequência máxima de dias com chuva
    dias_chuvosos_bool = (chuva_diaria > 0.1)
    blocos = (dias_chuvosos_bool.diff() != 0).cumsum()
    sequencias = dias_chuvosos_bool.groupby(blocos).transform('size')
    max_sequencia_chuva = sequencias[dias_chuvosos_bool].max() if dias_com_chuva > 0 else 0

    # Sequência máxima de dias SEM chuva (NOVA MÉTRICA)
    dias_secos_bool = (chuva_diaria <= 0.1)
    blocos_secos = (dias_secos_bool.diff() != 0).cumsum()
    sequencias_secas = dias_secos_bool.groupby(blocos_secos).transform('size')
    max_sequencia_seca = sequencias_secas[dias_secos_bool].max() if dias_secos_bool.any() else 0

    # Resumo executivo
    relatorio_linhas.extend([
        "🏗️  RESUMO EXECUTIVO PARA OBRAS:",
        "-" * 50,
        f"• Período analisado: {periodo_sazonal_str}",
        f"• Total de dias no histórico: {total_dias} ({total_anos} anos)",
        f"• Probabilidade geral de chuva: {prob_geral:.1f}%",
        f"• Dias com precipitação: {dias_com_chuva}",
        f"• Dias com umidade alta (≥90%): {dias_umidade_alta}" if coluna_umidade else "",
        f"• Consistência entre anos: {consistencia:.1f}%",
        "",
        "📈 MÉTRICAS DE INTENSIDADE:",
        "-" * 35,
        f"• Volume médio (dias chuvosos): {media_mm:.2f} mm",
        f"• Volume total acumulado: {total_mm:.2f} mm", 
        f"• Pico histórico: {max_mm:.2f} mm em {dia_max}",
        f"• Maior sequência de dias com chuva: {max_sequencia_chuva} dias",
        f"• Maior sequência de dias SEM chuva: {max_sequencia_seca} dias (janela de oportunidade)",
        ""
    ])

    # Análise de Temperatura e Vento
    if coluna_temp or coluna_vento:
        relatorio_linhas.extend([
            "🌡️  ANÁLISE DE TEMPERATURA E VENTO:",
            "-" * 40
        ])
        if coluna_temp:
            temp_diaria_media = df.set_index('data_hora').resample('D')[coluna_temp].mean()
            temp_diaria_max = df.set_index('data_hora').resample('D')[coluna_temp].max()
            temp_diaria_min = df.set_index('data_hora').resample('D')[coluna_temp].min()
            relatorio_linhas.append(f"• Temperatura Média: {temp_diaria_media.mean():.1f}°C (Min: {temp_diaria_min.min():.1f}°C, Max: {temp_diaria_max.max():.1f}°C)")
            relatorio_linhas.append(f"• Dias com calor (> 30°C): {(temp_diaria_max > 30).sum()} dias")
            relatorio_linhas.append(f"• Dias com frio (< 10°C): {(temp_diaria_min < 10).sum()} dias")

        if coluna_vento:
            vento_diario_medio = df.set_index('data_hora').resample('D')[coluna_vento].mean()
            relatorio_linhas.append(f"• Velocidade Média do Vento: {vento_diario_medio.mean():.1f} m/s")
        
        if coluna_rajada:
            rajada_max = df[coluna_rajada].max()
            relatorio_linhas.append(f"• Rajada Máxima de Vento: {rajada_max:.1f} m/s")
        
        relatorio_linhas.append("")

    # === ANÁLISE SAZONAL (se o período for longo) ===
    # Calcular duração do período
    duracao_periodo = (data_fim_real - data_inicio_real).days + 1

    # Ativar análise sazonal apenas se >= 45 dias
    if duracao_periodo >= 45:
        relatorio_linhas.extend([
            "🗓️  ANÁLISE SAZONAL (PROBABILIDADE POR MÊS):",
            "-" * 45,
        ])

        # Análise por mês (usa o chuva_diaria que já temos)
        chuva_df_sazonal = chuva_diaria.to_frame('chuva')
        chuva_df_sazonal['mes'] = chuva_df_sazonal.index.month
        chuva_df_sazonal['choveu'] = chuva_df_sazonal['chuva'] > 0.1
        
        analise_mensal = chuva_df_sazonal.groupby('mes').agg(
            total_dias=('choveu', 'count'),
            dias_chuva=('choveu', 'sum')
        )

        meses_nomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                       'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

        for mes_num, dados_mes in analise_mensal.iterrows():
            prob_mes = (dados_mes['dias_chuva'] / dados_mes['total_dias'] * 100) if dados_mes['total_dias'] > 0 else 0
            
            if prob_mes >= 40: status = "🔴 DESFAVORÁVEL"
            elif prob_mes >= 25: status = "🟡 MODERADO"
            else: status = "🟢 FAVORÁVEL"
            
            relatorio_linhas.append(f"• {meses_nomes[mes_num-1]}: {prob_mes:.1f}% de chance de chuva ({status})")
        
        relatorio_linhas.append("")


    # Probabilidades diárias
    chuva_df = chuva_diaria.to_frame('chuva')
    chuva_df['dia_mes'] = chuva_df.index.strftime('%d/%m')
    chuva_df['choveu'] = chuva_df['chuva'] > 0.1
    
    prob_diaria = chuva_df.groupby('dia_mes')['choveu'].agg(['count', 'sum']).reset_index()
    prob_diaria['prob'] = (prob_diaria['sum'] / prob_diaria['count'] * 100).round(1)
    
    relatorio_linhas.extend([
        "📅 PROBABILIDADES DIÁRIAS PARA PLANEJAMENTO:",
        "-" * 55,
        "Dia/Mês | Prob.% | Anos | Recomendação para Obras",
        "-" * 55
    ])

    for _, row in prob_diaria.iterrows():
        dia_mes = row['dia_mes']
        prob = row['prob']
        anos = row['count']
        
        if prob >= 30:
            rec = "🔴 ALTO - Evitar atividades externas"
        elif prob >= 20:
            rec = "🟡 MÉDIO - Planejar cobertura"
        elif prob >= 10:
            rec = "🟢 BAIXO - Monitorar previsão"
        else:
            rec = "✅ FAVORÁVEL - Condições adequadas"
            
        relatorio_linhas.append(f"{dia_mes:>6} | {prob:>5.1f} | {anos:>4} | {rec}")

    # === SEÇÃO DE ANÁLISE POR PRESET DE OBRA ===
    if preset_obra and preset_obra != "Nenhum (Análise Geral)":
        
        regras_preset = {
            "Fundações": {"chuva_max": 25, "umidade_max": 95},
            "Terraplanagem": {"chuva_max": 30, "umidade_max": 95},
            "Alvenaria": {"chuva_max": 25, "umidade_max": 90},
            "Concretagem": {"chuva_max": 20, "temp_min": 5, "temp_max": 32},
            "Cobertura/Telhado": {"chuva_max": 10, "vento_max": 12},
            "Pintura Externa": {"chuva_max": 15, "umidade_max": 85, "vento_max": 8}
        }
        
        regras = regras_preset.get(preset_obra)
        if regras:
            relatorio_linhas.extend([
                "",
                f"🎯 ANÁLISE ESPECÍFICA PARA: {preset_obra.upper()}",
                "-" * (30 + len(preset_obra)),
                f"Para o período de {periodo_sazonal_str} em {local_nome}:",
                ""
            ])
            
            # Análise de Chuva
            if 'chuva_max' in regras:
                dias_risco_chuva = (prob_diaria['prob'] > regras['chuva_max']).sum()
                perc_risco_chuva = (dias_risco_chuva / len(prob_diaria)) * 100
                relatorio_linhas.append(f"• RISCO DE CHUVA (Prob. > {regras['chuva_max']}%): {dias_risco_chuva} de {len(prob_diaria)} dias ({perc_risco_chuva:.1f}%)")
                if perc_risco_chuva > 50:
                    relatorio_linhas.append("  - RECOMENDAÇÃO: Risco ALTO. Período desfavorável. Planeje proteções.")
                elif perc_risco_chuva > 20:
                    relatorio_linhas.append("  - RECOMENDAÇÃO: Risco MODERADO. Monitore a previsão do tempo.")
                else:
                    relatorio_linhas.append("  - RECOMENDAÇÃO: Risco BAIXO. Condições favoráveis.")

            # Análise de Umidade
            if 'umidade_max' in regras and coluna_umidade:
                umidade_diaria_max = df.set_index('data_hora').resample('D')[coluna_umidade].max()
                dias_risco_umidade = (umidade_diaria_max > regras['umidade_max']).sum()
                perc_risco_umidade = (dias_risco_umidade / total_dias) * 100
                relatorio_linhas.append(f"• RISCO DE UMIDADE (Max > {regras['umidade_max']}%): {dias_risco_umidade} de {total_dias} dias ({perc_risco_umidade:.1f}%)")

            # Análise de Temperatura (para Concretagem)
            if 'temp_min' in regras and 'temp_max' in regras and coluna_temp:
                temp_diaria_media = df.set_index('data_hora').resample('D')[coluna_temp].mean()
                dias_risco_temp = ((temp_diaria_media < regras['temp_min']) | (temp_diaria_media > regras['temp_max'])).sum()
                perc_risco_temp = (dias_risco_temp / total_dias) * 100
                relatorio_linhas.append(f"• RISCO DE TEMPERATURA (Fora de {regras['temp_min']}-{regras['temp_max']}°C): {dias_risco_temp} de {total_dias} dias ({perc_risco_temp:.1f}%)")

            # Análise de Vento
            if 'vento_max' in regras and coluna_vento:
                vento_diario_max = df.set_index('data_hora').resample('D')[coluna_vento].max()
                dias_risco_vento = (vento_diario_max > regras['vento_max']).sum()
                perc_risco_vento = (dias_risco_vento / total_dias) * 100
                relatorio_linhas.append(f"• RISCO DE VENTO (Max > {regras['vento_max']} m/s): {dias_risco_vento} de {total_dias} dias ({perc_risco_vento:.1f}%)")

            # Avaliação Geral
            total_risco = sum(p for p in [perc_risco_chuva, perc_risco_umidade if 'umidade_max' in regras else 0] if p is not None)
            if total_risco > 100: avaliacao = "Desfavorável"
            elif total_risco > 40: avaliacao = "Requer Atenção"
            else: avaliacao = "Favorável"
            relatorio_linhas.append(f"\nAVALIAÇÃO GERAL PARA {preset_obra.upper()} NESTE PERÍODO: {avaliacao}")

    # Recomendações específicas
    relatorio_linhas.extend([
        "",
        "🔧 RECOMENDAÇÕES POR TIPO DE OBRA:",
        "-" * 45,
        "• CONCRETO: Evitar concretagem com prob. > 20%",
        "• PINTURA: Não pintar com umidade > 85% ou prob. > 15%", 
        "• ALVENARIA: Proteger materiais com prob. > 25%",
        "• TERRAPLANAGEM: Suspender com prob. > 30%",
        "• COBERTURA: Priorizar em dias com prob. < 10%",
        "",
        "⚖️  DISCLAIMER LEGAL:",
        "-" * 25,
        "Este relatório baseia-se exclusivamente em dados históricos",
        "e não constitui previsão meteorológica oficial. Para decisões",
        "críticas de obra, consulte sempre previsão meteorológica",
        "atualizada e profissionais especializados.",
        "",
        f"📋 Relatório gerado pelo Sistema de Análise Climática v2.0",
        "=" * 80
    ])

    relatorio_final = "\n".join(relatorio_linhas)

    # Salvar arquivo
    try:
        with open(nome_arquivo_relatorio, 'w', encoding='utf-8') as f:
            f.write(relatorio_final)
        print(f"\n📄 Relatório histórico salvo: {nome_arquivo_relatorio}")
        return nome_arquivo_relatorio
    except IOError as e:
        print(f"❌ Erro ao salvar relatório: {e}")
        return None
