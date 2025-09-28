# GUI Final - Versão Corrigida Completa

import customtkinter as ctk
from tkinter import messagebox
import threading
import webbrowser
import os
import json
import sys
import subprocess
import requests
from functools import lru_cache

from main import orquestrar_coleta_e_analise

# === TOOLTIP CORRIGIDO ===
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<Button-1>", self.on_leave)

    def on_enter(self, event=None):
        if self.tooltip:
            return
        
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25
        
        self.tooltip = ctk.CTkToplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        self.tooltip.attributes('-topmost', True)
        
        frame = ctk.CTkFrame(self.tooltip, corner_radius=8, fg_color=("#2B2B2B", "#1C1C1C"))
        frame.pack(padx=2, pady=2)
        
        label = ctk.CTkLabel(frame, text=self.text, 
                            font=ctk.CTkFont(size=11),
                            text_color=("white", "white"))
        label.pack(padx=8, pady=4)

    def on_leave(self, event=None):
        if self.tooltip:
            try:
                self.tooltip.destroy()
            except:
                pass
            finally:
                self.tooltip = None

# === VALIDAÇÃO VISUAL COMPLETA ===

# Validação REAL de Cidade usando API



class ValidadorReal:
    @staticmethod
    @lru_cache(maxsize=100)  # Cache para evitar muitas requisições
    def verificar_cidade_existe(cidade):
        """Verifica se a cidade realmente existe usando API gratuita"""
        try:
            # API gratuita do OpenStreetMap (Nominatim)
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': cidade,
                'format': 'json',
                'limit': 1,
                'countrycodes': 'br',  # Só Brasil
                'addressdetails': 1
            }
            
            headers = {
                'User-Agent': 'AnaliseClimatica/1.0'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=3)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    # Verifica se é realmente uma cidade/município
                    address = data[0].get('address', {})
                    place_type = data[0].get('type', '')
                    
                    # Tipos válidos para cidades
                    tipos_validos = ['city', 'town', 'village', 'municipality', 'administrative']
                    
                    if (place_type in tipos_validos or 
                        'city' in address or 
                        'town' in address or 
                        'municipality' in address):
                        return True, data[0].get('display_name', '')
            
            return False, None
            
        except Exception as e:
            # Se der erro na API, aceita (não bloqueia o usuário)
            return None, f"Erro na verificação: {str(e)}"
    
    @staticmethod
    def validar_cidade_async(entry_widget, valor, callback=None):
        """Validação assíncrona para não travar a interface"""
        if not valor or len(valor.strip()) < 3:
            entry_widget.configure(border_color=("gray60", "gray30"))
            return
        
        # Validação básica primeiro (instantânea)
        valor = valor.strip()
        
        if valor.isdigit() or len(valor) < 3:
            entry_widget.configure(border_color=("#E74C3C", "#FF6B6B"))
            return
        
        # Cor amarela enquanto verifica
        entry_widget.configure(border_color=("#FFC107", "#FFD54F"))
        
        def verificar():
            existe, info = ValidadorReal.verificar_cidade_existe(valor)
            
            if existe is True:
                # Verde - cidade existe
                entry_widget.configure(border_color=("#28A745", "#34CE57"))
                if callback:
                    callback(True, f"✅ Cidade encontrada: {info}")
            elif existe is False:
                # Vermelho - cidade não existe
                entry_widget.configure(border_color=("#E74C3C", "#FF6B6B"))
                if callback:
                    callback(False, "❌ Cidade não encontrada")
            else:
                # Laranja - erro na verificação, mas aceita
                entry_widget.configure(border_color=("#F39C12", "#FFB84D"))
                if callback:
                    callback(None, f"⚠️ {info}")
        
        # Executa em thread separada
        thread = threading.Thread(target=verificar)
        thread.daemon = True
        thread.start()

class ValidadorVisual:

    @staticmethod
    def validar_dia(entry_widget, valor):
        try:
            if not valor:
                entry_widget.configure(border_color=("gray60", "gray30"))
                return None
            dia = int(valor)
            if 1 <= dia <= 31:
                entry_widget.configure(border_color=("#28A745", "#34CE57"))
                return True
            else:
                entry_widget.configure(border_color=("#E74C3C", "#FF6B6B"))
                return False
        except ValueError:
            entry_widget.configure(border_color=("#E74C3C", "#FF6B6B"))
            return False
    
    @staticmethod
    def validar_mes(entry_widget, valor):
        try:
            if not valor:
                entry_widget.configure(border_color=("gray60", "gray30"))
                return None
            mes = int(valor)
            if 1 <= mes <= 12:
                entry_widget.configure(border_color=("#28A745", "#34CE57"))
                return True
            else:
                entry_widget.configure(border_color=("#E74C3C", "#FF6B6B"))
                return False
        except ValueError:
            entry_widget.configure(border_color=("#E74C3C", "#FF6B6B"))
            return False
    
    @staticmethod
    def validar_anos(entry_widget, valor):
        try:
            if not valor:
                entry_widget.configure(border_color=("gray60", "gray30"))
                return None
            anos = int(valor)
            if 1 <= anos <= 20:
                entry_widget.configure(border_color=("#28A745", "#34CE57"))
                return True
            else:
                entry_widget.configure(border_color=("#E74C3C", "#FF6B6B"))
                return False
        except ValueError:
            entry_widget.configure(border_color=("#E74C3C", "#FF6B6B"))
            return False
    
    @staticmethod
    def validar_cidade(entry_widget, valor):
        """Validação inteligente para cidade"""
        if not valor:
            entry_widget.configure(border_color=("gray60", "gray30"))
            return None
        
        valor = valor.strip()
        
        # 1. Muito curto ou só números = ERRO
        if len(valor) < 3 or valor.isdigit():
            entry_widget.configure(border_color=("#E74C3C", "#FF6B6B"))
            return False
        
        # 2. Formato ideal: "Cidade, Estado" = VERDE
        if ',' in valor:
            partes = valor.split(',')
            if len(partes) == 2:
                cidade, estado = partes[0].strip(), partes[1].strip()
                if len(cidade) >= 2 and len(estado) >= 2 and not any(p.isdigit() for p in partes):
                    entry_widget.configure(border_color=("#28A745", "#34CE57"))
                    return True
        
        # 3. Só nome da cidade = LARANJA (aviso)
        if len(valor) >= 3 and not valor.isdigit() and valor.replace(' ', '').isalpha():
            entry_widget.configure(border_color=("#F39C12", "#FFB84D"))
            return "warning"
        
        # 4. Outros casos = ERRO
        entry_widget.configure(border_color=("#E74C3C", "#FF6B6B"))
        return False

# === CLASSE PRINCIPAL ===
class AnaliseClimaticaGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🌦️ Análise Climática para Construção Civil")
        self.geometry("750x700")  # Aumentei altura para presets
        self.minsize(700, 650)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.api_keys = self.carregar_api_keys()
        self.ultimo_arquivo_csv = None
        self.status_validacao_var = ctk.StringVar(value=' Digite uma cidade para validar..')
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.criar_interface()
        self.center_window()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def criar_interface(self):
        # TÍTULO
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        title_label = ctk.CTkLabel(title_frame, text="🌦️ Análise Climática para Construção Civil",
                                   font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack()

        # FRAME PRINCIPAL
        main_content_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_content_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        main_content_frame.grid_columnconfigure(0, weight=1)
        
        # PARÂMETROS
        params_card = ctk.CTkFrame(main_content_frame, corner_radius=15)
        params_card.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        params_card.grid_columnconfigure(1, weight=1)

        card_title = ctk.CTkLabel(params_card, text="⚙️ Parâmetros da Análise", 
                                  font=ctk.CTkFont(size=18, weight="bold"))
        card_title.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 15))

        # LOCALIZAÇÃO COM VALIDAÇÃO
        ctk.CTkLabel(params_card, text="🏙️ Localização", 
                    font=ctk.CTkFont(size=12, weight="bold")).grid(
                    row=1, column=0, padx=(20, 10), pady=15, sticky="w")
        
        self.cidade_var = ctk.StringVar(value="Toledo, Parana")
        self.cidade_entry = ctk.CTkEntry(params_card, textvariable=self.cidade_var,
                                   placeholder_text="Ex: São Paulo, SP")
        self.cidade_entry.grid(row=1, column=1, padx=(0, 20), pady=15, sticky="ew")
        
        ToolTip(self.cidade_entry, "💡 Digite a cidade e estado\n Ex: Cascavel, parana ou Cascavel, pr\n Certifique que o nome da cidade esta correto (bugado)")
        
        # Validação em tempo real para cidade
        def validar_cidade_callback(*args):
            def resultado_callback(valido, mensagem):
                print(f"🌍 VALIDAÇÃO: {mensagem}")
            
            ValidadorReal.validar_cidade_async(
                self.cidade_entry, 
                self.cidade_var.get(),
                resultado_callback
            )
        self.cidade_var.trace_add("write", validar_cidade_callback)
        # PERÍODO COM VALIDAÇÃO
        ctk.CTkLabel(params_card, text="📅 Período de Análise", 
                    font=ctk.CTkFont(size=12, weight="bold")).grid(
                    row=2, column=0, padx=(20, 10), pady=15, sticky="w")
        
        date_frame = ctk.CTkFrame(params_card, fg_color="transparent")
        date_frame.grid(row=2, column=1, padx=(0, 20), pady=15, sticky="ew")
        
        # Data início
        inicio_frame = ctk.CTkFrame(date_frame, fg_color="transparent")
        inicio_frame.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(inicio_frame, text="Início:", font=ctk.CTkFont(size=10)).pack()
        inicio_date_frame = ctk.CTkFrame(inicio_frame, fg_color="transparent")
        inicio_date_frame.pack()
        
        self.dia_inicio_var = ctk.StringVar(value="15")
        self.mes_inicio_var = ctk.StringVar(value="01")
        
        self.dia_inicio_entry = ctk.CTkEntry(inicio_date_frame, textvariable=self.dia_inicio_var, 
                                       width=50, placeholder_text="DD")
        self.dia_inicio_entry.pack(side="left", padx=2)
        ctk.CTkLabel(inicio_date_frame, text="/", font=ctk.CTkFont(size=14)).pack(side="left", padx=2)
        self.mes_inicio_entry = ctk.CTkEntry(inicio_date_frame, textvariable=self.mes_inicio_var, 
                                       width=50, placeholder_text="MM")
        self.mes_inicio_entry.pack(side="left", padx=2)
        
        ToolTip(self.dia_inicio_entry, "📅 Dia (1-31)")
        ToolTip(self.mes_inicio_entry, "📅 Mês (1-12)")
        
        def validar_dia_inicio(*args):
            ValidadorVisual.validar_dia(self.dia_inicio_entry, self.dia_inicio_var.get())
        def validar_mes_inicio(*args):
            ValidadorVisual.validar_mes(self.mes_inicio_entry, self.mes_inicio_var.get())
        
        self.dia_inicio_var.trace_add("write", validar_dia_inicio)
        self.mes_inicio_var.trace_add("write", validar_mes_inicio)
        
        # Data fim
        fim_frame = ctk.CTkFrame(date_frame, fg_color="transparent")
        fim_frame.pack(side="left")
        ctk.CTkLabel(fim_frame, text="Fim:", font=ctk.CTkFont(size=10)).pack()
        fim_date_frame = ctk.CTkFrame(fim_frame, fg_color="transparent")
        fim_date_frame.pack()
        
        self.dia_fim_var = ctk.StringVar(value="28")
        self.mes_fim_var = ctk.StringVar(value="02")
        
        self.dia_fim_entry = ctk.CTkEntry(fim_date_frame, textvariable=self.dia_fim_var, 
                                    width=50, placeholder_text="DD")
        self.dia_fim_entry.pack(side="left", padx=2)
        ctk.CTkLabel(fim_date_frame, text="/", font=ctk.CTkFont(size=14)).pack(side="left", padx=2)
        self.mes_fim_entry = ctk.CTkEntry(fim_date_frame, textvariable=self.mes_fim_var, 
                                    width=50, placeholder_text="MM")
        self.mes_fim_entry.pack(side="left", padx=2)
        
        ToolTip(self.dia_fim_entry, "📅 Dia (1-31)")
        ToolTip(self.mes_fim_entry, "📅 Mês (1-12)")
        
        def validar_dia_fim(*args):
            ValidadorVisual.validar_dia(self.dia_fim_entry, self.dia_fim_var.get())
        def validar_mes_fim(*args):
            ValidadorVisual.validar_mes(self.mes_fim_entry, self.mes_fim_var.get())
        
        self.dia_fim_var.trace_add("write", validar_dia_fim)
        self.mes_fim_var.trace_add("write", validar_mes_fim)

        # ANOS COM VALIDAÇÃO
        ctk.CTkLabel(params_card, text="📊 Anos para Analisar", 
                    font=ctk.CTkFont(size=12, weight="bold")).grid(
                    row=3, column=0, padx=(20, 10), pady=15, sticky="w")
        
        self.anos_var = ctk.StringVar(value="10")
        self.anos_entry = ctk.CTkEntry(params_card, textvariable=self.anos_var, 
                                 width=100, placeholder_text="1-20")
        self.anos_entry.grid(row=3, column=1, padx=(0, 20), pady=15, sticky="w")
        
        ToolTip(self.anos_entry, "📊 Quantidade de anos históricos\n💡 Recomendado: 5-15 anos")
        
        def validar_anos_callback(*args):
            ValidadorVisual.validar_anos(self.anos_entry, self.anos_var.get())
        self.anos_var.trace_add("write", validar_anos_callback)

        # PRESETS DE OBRA
        ctk.CTkLabel(params_card, text="🏗️ Tipo de Obra", 
                    font=ctk.CTkFont(size=12, weight="bold")).grid(
                    row=4, column=0, padx=(20, 10), pady=15, sticky="w")
        
        self.preset_obras = [
            "Nenhum (Análise Geral)", "Fundações", "Terraplanagem", 
            "Alvenaria", "Concretagem", "Cobertura/Telhado", "Pintura Externa"
        ]
        self.preset_var = ctk.StringVar(value=self.preset_obras[0])
        self.preset_menu = ctk.CTkOptionMenu(params_card, variable=self.preset_var, values=self.preset_obras)
        self.preset_menu.grid(row=4, column=1, padx=(0, 20), pady=15, sticky="w")
        
        ToolTip(self.preset_menu, "🎯 Selecione o tipo de obra para\nreceber recomendações específicas\nno relatório final")

        # BOTÕES
        action_frame = ctk.CTkFrame(main_content_frame, fg_color="transparent")
        action_frame.grid(row=1, column=0, pady=20)
        
        config_btn = ctk.CTkButton(action_frame, text="⚙️ Configurar APIs",
                                  command=self.abrir_config_apis, width=150, height=40)
        config_btn.pack(side="left", padx=15)
        
        self.analisar_btn = ctk.CTkButton(action_frame, text="🚀 Iniciar Análise",
                                         command=self.iniciar_analise, width=180, height=45)
        self.analisar_btn.pack(side="left", padx=15)

        # STATUS
        status_frame = ctk.CTkFrame(main_content_frame, fg_color="transparent")
        status_frame.grid(row=2, column=0, sticky="ew", pady=(20, 0))
        status_frame.grid_columnconfigure(0, weight=1)

        self.progress_var = ctk.StringVar(value="✅ Pronto para análise")
        status_label = ctk.CTkLabel(status_frame, textvariable=self.progress_var)
        status_label.grid(row=0, column=0, pady=(0, 10))
        
        self.progress_bar = ctk.CTkProgressBar(status_frame, mode='determinate')
        self.progress_bar.set(0)
        self.progress_bar.grid(row=1, column=0, sticky="ew", padx=50)

        # BOTÕES DE RESULTADO
        result_buttons_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        result_buttons_frame.grid(row=2, column=0, pady=(20, 0))

        self.relatorio_btn = ctk.CTkButton(result_buttons_frame, text="📄 Abrir Relatório", 
                                          command=self.abrir_relatorio, state='disabled')
        self.relatorio_btn.pack(side="left", padx=10)
        
        self.pasta_btn = ctk.CTkButton(result_buttons_frame, text="📂 Abrir Pasta", 
                                      command=self.abrir_pasta, state='disabled')
        self.pasta_btn.pack(side="left", padx=10)

    def carregar_api_keys(self):
        config_file = "api_config.json"
        default_keys = {"openweathermap": "", "stormglass": "", "visualcrossing": "", "wolfram": ""}
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f: 
                    return json.load(f)
            except: 
                return default_keys
        return default_keys
        
    def salvar_api_keys(self):
        with open("api_config.json", 'w', encoding='utf-8') as f: 
            json.dump(self.api_keys, f, indent=4)
            
    def abrir_config_apis(self):
        ConfigAPIsWindow(self, self.api_keys, self.salvar_api_keys)
        
    def validar_entradas(self):
        try:
            dia_inicio = int(self.dia_inicio_var.get())
            mes_inicio = int(self.mes_inicio_var.get())
            dia_fim = int(self.dia_fim_var.get())
            mes_fim = int(self.mes_fim_var.get())
            anos = int(self.anos_var.get())
            if not (1 <= dia_inicio <= 31 and 1 <= mes_inicio <= 12): 
                raise ValueError("Data de início inválida")
            if not (1 <= dia_fim <= 31 and 1 <= mes_fim <= 12): 
                raise ValueError("Data de fim inválida")
            if anos < 1: 
                raise ValueError("Número de anos deve ser pelo menos 1")
            cidade = self.cidade_var.get().strip()
            if not cidade: 
                raise ValueError("Cidade não pode estar vazia")
            return True, None
        except ValueError as e: 
            return False, str(e)
            
    def iniciar_analise(self):
        valido, erro = self.validar_entradas()
        if not valido:
            messagebox.showerror("Erro de Validação", erro)
            return
            
        if not any(self.api_keys.values()):
            messagebox.showwarning("APIs não configuradas", "Configure pelo menos uma chave de API antes de iniciar a análise.")
            return
            
        self.analisar_btn.configure(state='disabled')
        self.relatorio_btn.configure(state='disabled')
        self.pasta_btn.configure(state='disabled')
        self.progress_bar.set(0)
        self.progress_bar.configure(mode='indeterminate')
        self.progress_bar.start()
        self.progress_var.set("Iniciando análise...")
        
        thread = threading.Thread(target=self.executar_analise)
        thread.daemon = True
        thread.start()
        
    def executar_analise(self):
        try:
            local_nome = self.cidade_var.get().strip()
            dia_inicio = int(self.dia_inicio_var.get())
            mes_inicio = int(self.mes_inicio_var.get())
            dia_fim = int(self.dia_fim_var.get())
            mes_fim = int(self.mes_fim_var.get())
            num_anos = int(self.anos_var.get())
            preset_obra = self.preset_var.get()  # Pega o preset selecionado
            
            if not os.path.exists('cache'): 
                os.makedirs('cache')

            def update_progress_gui(message, current_step=None, total_steps=None):
                self.progress_var.set(message)
                if current_step and total_steps:
                    self.progress_bar.stop()
                    self.progress_bar.configure(mode='determinate')
                    progress_value = float(current_step) / float(total_steps)
                    self.progress_bar.set(progress_value)

            # Passa o preset para o main.py
            sucesso, resultado = orquestrar_coleta_e_analise(
                local_nome, dia_inicio, mes_inicio, dia_fim, mes_fim, num_anos,
                self.api_keys, update_progress_gui, preset_obra
            )
            
            if sucesso:
                self.ultimo_arquivo_csv = resultado
                self.after(0, self.analise_concluida)
            else:
                self.after(0, lambda: self.analise_erro(resultado))
                
        except Exception as e:
            erro_msg = f"Erro durante a análise: {str(e)}"
            self.after(0, lambda: self.analise_erro(erro_msg))
            
    def analise_concluida(self):
        self.progress_bar.stop()
        self.progress_bar.set(1)
        self.progress_var.set("✅ Análise concluída com sucesso!")
        self.analisar_btn.configure(state='normal')
        self.relatorio_btn.configure(state='normal')
        self.pasta_btn.configure(state='normal')
        messagebox.showinfo("Sucesso", "Análise climática concluída!")
        
    def analise_erro(self, mensagem):
        self.progress_bar.stop()
        self.progress_bar.set(0)
        self.progress_var.set("❌ Erro na análise. Verifique as configurações.")
        self.analisar_btn.configure(state='normal')
        messagebox.showerror("Erro", mensagem)

    def _abrir_arquivo_ou_pasta(self, caminho):
        try:
            os.startfile(caminho)
        except AttributeError:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, caminho])

    def abrir_relatorio(self):
        if self.ultimo_arquivo_csv:
            arquivo_relatorio = self.ultimo_arquivo_csv.replace('.csv', '_relatorio_historico.txt')
            if os.path.exists(arquivo_relatorio):
                self._abrir_arquivo_ou_pasta(arquivo_relatorio)
            else: 
                messagebox.showerror("Erro", "Arquivo de relatório não encontrado.")
                
    def abrir_pasta(self):
        self._abrir_arquivo_ou_pasta(os.getcwd())


# === JANELA DE CONFIGURAÇÃO ===
class ConfigAPIsWindow(ctk.CTkToplevel):
    def __init__(self, parent, api_keys, callback_salvar):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.title("🔑 Configuração de APIs")
        self.geometry("600x500")
        self.resizable(False, False)
        self.api_keys = api_keys
        self.callback_salvar = callback_salvar
        self.entries = {}
        self.criar_interface()

    def criar_interface(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(main_frame, text="🔑 Configuração de Chaves de API", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(0, 20))
        
        apis_info = [
            {'name': 'OpenWeatherMap', 'key': 'openweathermap', 'url': 'https://openweathermap.org/api'},
            {'name': 'StormGlass', 'key': 'stormglass', 'url': 'https://stormglass.io/'},
            {'name': 'Visual Crossing', 'key': 'visualcrossing', 'url': 'https://www.visualcrossing.com/weather-api'},
            {'name': 'Wolfram Alpha', 'key': 'wolfram', 'url': 'https://developer.wolframalpha.com/portal/myapps/'}
        ]
        
        for api in apis_info:
            api_frame = ctk.CTkFrame(main_frame)
            api_frame.pack(fill="x", pady=5)
            api_frame.grid_columnconfigure(1, weight=1)
            
            ctk.CTkLabel(api_frame, text=api['name'], 
                        font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=10)
            
            entry = ctk.CTkEntry(api_frame, show="*")
            entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
            entry.insert(0, self.api_keys.get(api['key'], ''))
            self.entries[api['key']] = entry
            
            criar_btn = ctk.CTkButton(api_frame, text="Obter Chave", width=100, 
                                     command=lambda url=api['url']: webbrowser.open(url))
            criar_btn.grid(row=0, column=2, padx=10, pady=10)
            
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=20)
        
        ctk.CTkButton(button_frame, text="💾 Salvar e Fechar", 
                     command=self.salvar_configuracao).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="❌ Cancelar", command=self.destroy, 
                     fg_color="gray50", hover_color="gray30").pack(side="left", padx=10)
                  
    def salvar_configuracao(self):
        for key, entry in self.entries.items(): 
            self.api_keys[key] = entry.get().strip()
        self.callback_salvar()
        messagebox.showinfo("Sucesso", "Configuração salva com sucesso!", parent=self)
        self.destroy()


if __name__ == "__main__":
    app = AnaliseClimaticaGUI()
    app.mainloop()
