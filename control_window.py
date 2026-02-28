"""
Control Window Module
Janela de controle principal do timer.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from format_modal import FormatModal
import os
import csv
from datetime import datetime

class ControlWindow:
    def __init__(self, timer_logic, timer_window=None):
        self.timer_logic = timer_logic
        self.timer_window = timer_window
        
        # Formatação atual
        self.current_format = {
            "bg_color": "#000000",
            "fg_color": "#FFFFFF",
            "font_family": "Arial",
            "font_size": 120,
            "transparent": False
        }
        
        # Criar janela principal
        self.window = tk.Tk()
        self.window.title("Timer Control")
        self.window.geometry("550x550")
        self.window.resizable(False, False)
        
        # Criar interface
        self._create_widgets()
        
        # Configurar callbacks
        self._setup_callbacks()
        
        # Configurar atalhos de teclado
        self._setup_shortcuts()
        
        # Estado da projeção
        self.is_projected = False
        
        # Centro da janela
        self._center_window()
    
    def _center_window(self):
        """Centraliza a janela na tela"""
        self.window.update_idletasks()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        window_width = self.window.winfo_width()
        window_height = self.window.winfo_height()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """Cria todos os widgets da interface"""
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Preview do timer
        preview_frame = ttk.LabelFrame(main_frame, text="Preview", padding="10")
        preview_frame.pack(fill="x", pady=(0, 10))
        
        self.preview_label = tk.Label(
            preview_frame,
            text="00:00",
            font=(self.current_format["font_family"], 48),
            bg=self.current_format["bg_color"],
            fg=self.current_format["fg_color"],
            height=2
        )
        self.preview_label.pack(fill="x")

        # Container horizontal para tempo e modo
        time_mode_container = ttk.Frame(main_frame)
        time_mode_container.pack(fill="x", pady=(0, 10))
        
        # Configuração de tempo (lado esquerdo)
        time_frame = ttk.LabelFrame(time_mode_container, text="Tempo Inicial", padding="10")
        time_frame.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        # Campos de tempo
        time_input_frame = ttk.Frame(time_frame)
        time_input_frame.pack()
        
        # Horas
        ttk.Label(time_input_frame, text="H:").grid(row=0, column=0, padx=2)
        self.hours_var = tk.IntVar(value=0)
        self.hours_spin = ttk.Spinbox(
            time_input_frame,
            from_=0,
            to=23,
            textvariable=self.hours_var,
            width=5,
            command=self._on_time_change
        )
        self.hours_spin.grid(row=0, column=1, padx=2)
        
        # Minutos
        ttk.Label(time_input_frame, text="M:").grid(row=0, column=2, padx=2)
        self.minutes_var = tk.IntVar(value=1)
        self.minutes_spin = ttk.Spinbox(
            time_input_frame,
            from_=0,
            to=59,
            textvariable=self.minutes_var,
            width=5,
            command=self._on_time_change
        )
        self.minutes_spin.grid(row=0, column=3, padx=2)
        
        # Segundos
        ttk.Label(time_input_frame, text="S:").grid(row=0, column=4, padx=2)
        self.seconds_var = tk.IntVar(value=0)
        self.seconds_spin = ttk.Spinbox(
            time_input_frame,
            from_=0,
            to=59,
            textvariable=self.seconds_var,
            width=5,
            command=self._on_time_change
        )
        self.seconds_spin.grid(row=0, column=5, padx=2)
        
        # Botão Atualizar tempo
        update_time_btn = ttk.Button(
            time_frame,
            text="Atualizar tempo",
            command=self._force_time_update
        )
        update_time_btn.pack(pady=(10, 0))
        
        # Modo do timer (lado direito)
        mode_frame = ttk.LabelFrame(time_mode_container, text="Modo", padding="10")
        mode_frame.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        self.mode_var = tk.StringVar(value="countdown")
        ttk.Radiobutton(
            mode_frame,
            text="Crescente (cronômetro)",
            variable=self.mode_var,
            value="stopwatch",
            command=self._on_mode_change
        ).pack(anchor="w")
        
        ttk.Radiobutton(
            mode_frame,
            text="Decrescente (contagem regressiva)",
            variable=self.mode_var,
            value="countdown",
            command=self._on_mode_change
        ).pack(anchor="w")
        
        # Configurar pesos das colunas do container tempo/modo
        time_mode_container.grid_columnconfigure(0, weight=7)
        time_mode_container.grid_columnconfigure(1, weight=3)
        
        # Container horizontal para controle e opções
        control_options_container = ttk.Frame(main_frame)
        control_options_container.pack(fill="x", pady=(0, 10))
        
        # Botões de controle (lado esquerdo)
        control_frame = ttk.LabelFrame(control_options_container, text="Controle", padding="10")
        control_frame.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        # Frame dos botões principais
        buttons_frame = ttk.Frame(control_frame)
        buttons_frame.pack(fill="x")
        
        self.start_btn = ttk.Button(
            buttons_frame,
            text="Iniciar",
            underline=-1,
            command=self._start_timer
        )
        self.start_btn.pack(side="left", padx=(0, 5))
        
        self.pause_btn = ttk.Button(
            buttons_frame,
            text="Pausar",
            underline=-1,
            command=self._pause_timer,
            state="disabled"
        )
        self.pause_btn.pack(side="left", padx=(0, 5))
        
        self.reset_btn = ttk.Button(
            buttons_frame,
            text="Resetar",
            underline=-1,
            command=self._reset_timer
        )
        self.reset_btn.pack(side="left", padx=(0, 5))
        
        # Botão Formatar
        self.format_btn = ttk.Button(
            control_frame,
            text="Formatar",
            underline=-1,
            command=self._open_format_modal
        )
        self.format_btn.pack(fill="x", pady=(10, 0))
        
        # Opções (lado direito)
        options_frame = ttk.LabelFrame(control_options_container, text="Opções", padding="10")
        options_frame.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        # Projetar/Ocultar
        self.project_var = tk.BooleanVar(value=False)
        self.project_check = ttk.Checkbutton(
            options_frame,
            text="Projetar/Ocultar",
            underline=-1,
            variable=self.project_var,
            command=self._toggle_projection
        )
        self.project_check.pack(anchor="w")
        
        # Ajustar posição e tamanho
        self.adjust_var = tk.BooleanVar(value=False)
        self.adjust_check = ttk.Checkbutton(
            options_frame,
            text="Ajustar posição e tamanho",
            variable=self.adjust_var,
            command=self._toggle_adjust
        )
        self.adjust_check.pack(anchor="w")
        
        # Botão para centralizar na posição inferior direita
        self.center_btn = ttk.Button(
            options_frame,
            text="Centralizar Inferior Direito",
            underline=-1,
            command=self._center_bottom_right
        )
        self.center_btn.pack(anchor="w", pady=(5, 0))
        
        # Configurar pesos das colunas do container controle/opções
        control_options_container.grid_columnconfigure(0, weight=7)
        control_options_container.grid_columnconfigure(1, weight=3)
        
        # Frame de presets
        presets_frame = ttk.LabelFrame(main_frame, text="Presets", padding="10")
        presets_frame.pack(fill="x", pady=(0, 10))
        
        # Frame dos botões de presets
        preset_buttons_frame = ttk.Frame(presets_frame)
        preset_buttons_frame.pack(fill="x")
        
        # Botão Salvar Preset
        self.save_preset_btn = ttk.Button(
            preset_buttons_frame,
            text="Salvar Preset",
            underline=-1,
            command=self._save_preset
        )
        self.save_preset_btn.pack(side="left", padx=(0, 5))
        
        # Botão Carregar Preset
        self.load_preset_btn = ttk.Button(
            preset_buttons_frame,
            text="Carregar Preset",
            underline=-1,
            command=self._load_preset
        )
        self.load_preset_btn.pack(side="left", padx=(0, 5))
    
    def _setup_shortcuts(self):
        """Configura os atalhos de teclado da janela de controle"""
        
        def _is_in_input(event):
            """Verifica se o foco atual está em um campo de entrada"""
            focused = self.window.focus_get()
            return isinstance(focused, (ttk.Spinbox, tk.Entry))
        
        def on_focus_hours(event):
            if not _is_in_input(event):
                self.hours_spin.focus_set()
                return "break"
        
        def on_focus_minutes(event):
            if not _is_in_input(event):
                self.minutes_spin.focus_set()
                return "break"
        
        def on_focus_seconds(event):
            if not _is_in_input(event):
                self.seconds_spin.focus_set()
                return "break"
        
        def on_space(event):
            if not _is_in_input(event):
                state = self.timer_logic.get_state()
                if state == "running":
                    self._pause_timer()
                else:
                    self._start_timer()
                return "break"
        
        def on_start(event):
            self._start_timer()
            return "break"
        
        def on_reset(event):
            self._reset_timer()
            return "break"
        
        def on_format(event):
            self._open_format_modal()
            return "break"
        
        def on_save_preset(event):
            self._save_preset()
            return "break"
        
        def on_load_preset(event):
            self._load_preset()
            return "break"
        
        def on_project(event):
            self.project_var.set(not self.project_var.get())
            self._toggle_projection()
            return "break"
        
        def on_center_bottom_right(event):
            self._center_bottom_right()
            return "break"
        
        # Atalhos sem CTRL (H, M, S, Espaço) - apenas quando fora de campos de entrada
        self.window.bind("<h>", on_focus_hours)
        self.window.bind("<H>", on_focus_hours)
        self.window.bind("<m>", on_focus_minutes)
        self.window.bind("<M>", on_focus_minutes)
        self.window.bind("<s>", on_focus_seconds)
        self.window.bind("<S>", on_focus_seconds)
        self.window.bind("<space>", on_space)
        
        # Atalhos com CTRL
        self.window.bind("<Control-i>", on_start)
        self.window.bind("<Control-I>", on_start)
        self.window.bind("<Control-r>", on_reset)
        self.window.bind("<Control-R>", on_reset)
        self.window.bind("<Control-f>", on_format)
        self.window.bind("<Control-F>", on_format)
        self.window.bind("<Control-c>", on_load_preset)
        self.window.bind("<Control-C>", on_load_preset)
        self.window.bind("<Control-p>", on_project)
        self.window.bind("<Control-P>", on_project)
        
        # Salvar preset: Ctrl+Shift+S
        self.window.bind("<Control-S>", on_save_preset)
        
        # Centralizar inferior direito: Ctrl+Shift+Baixo
        self.window.bind("<Control-Shift-Down>", on_center_bottom_right)
        
        # --- Modo de Access Keys (estilo Alt menu) ---
        self._access_key_mode = False
        self._access_key_widgets = [
            (self.start_btn,       0),   # I → Iniciar
            (self.pause_btn,       0),   # P → Pausar
            (self.reset_btn,       0),   # R → Resetar
            (self.format_btn,      0),   # F → Formatar
            (self.project_check,   9),   # O → Pr/Ocultar
            (self.center_btn,      22),  # D → ...Direito
            (self.save_preset_btn, 0),   # S → Salvar preset
            (self.load_preset_btn, 0),   # C → Carregar preset
        ]
        self._access_key_map = {
            'i': on_start,
            'p': lambda e: (self._pause_timer(), "break")[1],
            'r': on_reset,
            'f': on_format,
            'o': on_project,
            'd': on_center_bottom_right,
            's': on_save_preset,
            'c': on_load_preset,
        }

        def enter_access_key_mode(event):
            if self._access_key_mode:
                _exit_access_key_mode()
                return "break"
            self._access_key_mode = True
            for widget, idx in self._access_key_widgets:
                widget.config(underline=idx)
            return "break"

        def _exit_access_key_mode():
            self._access_key_mode = False
            for widget, _ in self._access_key_widgets:
                widget.config(underline=-1)

        def on_access_key_press(event):
            if not self._access_key_mode:
                return
            # Ignorar modificadores sozinhos (Alt, Ctrl, Shift, etc.)
            if event.keysym in ('Alt_L', 'Alt_R', 'Control_L', 'Control_R',
                                 'Shift_L', 'Shift_R', 'Super_L', 'Super_R'):
                return
            key = event.keysym.lower()
            _exit_access_key_mode()
            if key in self._access_key_map:
                self._access_key_map[key](event)
            return "break"

        def on_escape(event):
            if self._access_key_mode:
                _exit_access_key_mode()
                return "break"

        # Ativar modo com Alt (soltura da tecla para evitar disparo duplo)
        self.window.bind("<KeyRelease-Alt_L>", enter_access_key_mode)
        self.window.bind("<KeyRelease-Alt_R>", enter_access_key_mode)
        self.window.bind("<Escape>", on_escape)
        # Capturar qualquer tecla alfanumérica quando no modo access key
        self.window.bind("<Key>", on_access_key_press)
    
    def _setup_callbacks(self):
        """Configura os callbacks do timer logic"""
        # Encaminhar callbacks para o thread da UI com after
        def _safe_update(time_str: str):
            try:
                self.window.after(0, lambda: self._on_timer_update(time_str))
            except Exception:
                pass
        def _safe_state(state: str):
            try:
                self.window.after(0, lambda: self._on_state_change(state))
            except Exception:
                pass
        self.timer_logic.set_update_callback(_safe_update)
        self.timer_logic.set_state_callback(_safe_state)
    
    def _on_timer_update(self, time_str: str):
        """Callback para atualização do timer"""
        # Atualizar preview
        self.preview_label.config(text=time_str)
        
        # Atualizar janela do timer se estiver visível
        if self.is_projected and self.timer_window is not None:
            self.timer_window.update_time(time_str)
    
    def _on_state_change(self, state: str):
        """Callback para mudança de estado do timer"""
        if state == "running":
            self.start_btn.config(state="disabled")
            self.pause_btn.config(state="normal")
        elif state == "paused":
            self.start_btn.config(state="normal", text="Continuar")
            self.pause_btn.config(state="disabled")
        else:  # stopped
            self.start_btn.config(state="normal", text="Iniciar")
            self.pause_btn.config(state="disabled")
    
    def _on_time_change(self):
        """Callback para mudança no tempo"""
        hours = self.hours_var.get()
        minutes = self.minutes_var.get()
        seconds = self.seconds_var.get()
        self.timer_logic.set_time(hours, minutes, seconds)
        # Forçar atualização do preview
        self._on_timer_update(self.timer_logic.format_time())
    
    def _force_time_update(self):
        """Força atualização imediata do tempo no preview e timer principal"""
        hours = self.hours_var.get()
        minutes = self.minutes_var.get()
        seconds = self.seconds_var.get()
        # Atualiza o tempo inicial no TimerLogic
        self.timer_logic.set_time(hours, minutes, seconds)
        # Força atualização imediata independente do estado do timer
        current_time_str = self.timer_logic.format_time()
        self._on_timer_update(current_time_str)
    
    def _on_mode_change(self):
        """Callback para mudança no modo"""
        mode = self.mode_var.get()
        self.timer_logic.set_mode(mode)
    
    def _start_timer(self):
        """Inicia o timer"""
        self.timer_logic.start()
    
    def _pause_timer(self):
        """Pausa o timer"""
        self.timer_logic.pause()
    
    def _reset_timer(self):
        """Reseta o timer"""
        self.timer_logic.reset()
    
    def _toggle_projection(self):
        """Alterna a projeção da janela do timer"""
        self.is_projected = self.project_var.get()
        
        if self.timer_window is None:
            return
        
        if self.is_projected:
            # Aplicar formatação e tempo atuais antes de mostrar
            fmt = self.current_format
            try:
                self.timer_window.update_formatting(
                    fmt["bg_color"], fmt["fg_color"], fmt["font_family"], fmt["font_size"],
                    fmt.get("transparent", False)
                )
            except Exception:
                pass
            self.timer_window.update_time(self.timer_logic.format_time())
            self.timer_window.show()
        else:
            self.timer_window.hide()
    
    def _toggle_adjust(self):
        """Alterna o ajuste de posição e tamanho"""
        is_locked = not self.adjust_var.get()
        if self.timer_window is not None:
            self.timer_window.set_locked(is_locked)
    
    def _center_bottom_right(self):
        """Centraliza a janela do timer na posição inferior direita da tela"""
        if self.timer_window is not None:
            # Obter dimensões da tela
            screen_width = self.timer_window.window.winfo_screenwidth()
            screen_height = self.timer_window.window.winfo_screenheight()
            
            # Obter dimensões da janela do timer
            window_width = self.timer_window.window.winfo_width()
            window_height = self.timer_window.window.winfo_height()
            
            # Calcular posição inferior direita (com margem de 20px)
            x = screen_width - window_width - 20
            y = screen_height - window_height - 20
            
            # Aplicar nova posição
            self.timer_window.window.geometry(f"+{x}+{y}")
            
            # Se a janela estiver oculta, mostrar brevemente para feedback visual
            if not self.is_projected:
                self.timer_window.window.deiconify()
                self.timer_window.window.lift()
                # Opcional: esconder após 2 segundos se não estiver projetado
                # self.window.after(2000, lambda: self.timer_window.hide() if not self.is_projected else None)
    
    def _open_format_modal(self):
        """Abre o modal de formatação"""
        modal = FormatModal(
            self.window,
            self.current_format,
            self._apply_formatting
        )
    
    def _apply_formatting(self, new_format: dict):
        """Aplica a nova formatação"""
        self.current_format = new_format.copy()
        
        # No preview do controle, não usamos transparência real; mostramos a cor escolhida
        bg_color = new_format["bg_color"]
        
        # Atualizar preview
        try:
            self.preview_label.config(
                bg=bg_color,
                fg=new_format["fg_color"],
                font=(new_format["font_family"], 48)
            )
        except:
            self.preview_label.config(
                bg=bg_color,
                fg=new_format["fg_color"],
                font=("Arial", 48)
            )
        
        # Atualizar janela do timer
        if self.timer_window is not None:
            self.timer_window.update_formatting(
                new_format["bg_color"],
                new_format["fg_color"],
                new_format["font_family"],
                new_format["font_size"],
                new_format.get("transparent", False)
            )
    
    def run(self):
        """Inicia o loop principal da janela"""
        self.window.mainloop()
    
    def destroy(self):
        """Fecha a janela"""
        self.window.destroy()
    
    # Métodos de gerenciamento de presets
    
    def _get_presets_folder(self):
        """Obtém o caminho da pasta de presets"""
        return os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Timer_segunda_tela')
    
    def _ensure_presets_folder(self):
        """Cria a pasta de presets se não existir"""
        presets_folder = self._get_presets_folder()
        if not os.path.exists(presets_folder):
            os.makedirs(presets_folder)
        return presets_folder
    
    def _list_presets(self):
        """Lista todos os presets disponíveis"""
        presets_folder = self._ensure_presets_folder()
        presets = []
        
        for file in os.listdir(presets_folder):
            if file.endswith('.csv'):
                preset_name = file[:-4]  # Remove .csv
                presets.append(preset_name)
        
        return sorted(presets)
    
    def _read_preset(self, preset_name):
        """Lê os dados de um preset"""
        presets_folder = self._get_presets_folder()
        preset_file = os.path.join(presets_folder, f"{preset_name}.csv")
        
        try:
            with open(preset_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                row = next(reader)
                
                return {
                    'name': row[0],
                    'hours': int(row[1]),
                    'minutes': int(row[2]),
                    'seconds': int(row[3]),
                    'mode': row[4],
                    'x': int(row[5]),
                    'y': int(row[6]),
                    'width': int(row[7]),
                    'height': int(row[8]),
                    'bg_color': row[9],
                    'fg_color': row[10],
                    'font_family': row[11],
                    'font_size': int(row[12]),
                    'transparent': row[13].lower() == 'true'
                }
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ler preset: {e}")
            return None
    
    def _write_preset(self, preset_name, preset_data):
        """Escreve os dados de um preset"""
        presets_folder = self._ensure_presets_folder()
        preset_file = os.path.join(presets_folder, f"{preset_name}.csv")
        
        try:
            with open(preset_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    preset_data['name'],
                    preset_data['hours'],
                    preset_data['minutes'],
                    preset_data['seconds'],
                    preset_data['mode'],
                    preset_data['x'],
                    preset_data['y'],
                    preset_data['width'],
                    preset_data['height'],
                    preset_data['bg_color'],
                    preset_data['fg_color'],
                    preset_data['font_family'],
                    preset_data['font_size'],
                    preset_data['transparent']
                ])
            return True
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar preset: {e}")
            return False
    
    def _collect_current_settings(self):
        """Coleta todas as configurações atuais"""
        # Obter tempo atual
        hours = self.hours_var.get()
        minutes = self.minutes_var.get()
        seconds = self.seconds_var.get()
        
        # Obter modo atual
        mode = self.mode_var.get()
        
        # Obter posição e tamanho da janela do timer
        x, y, width, height = 0, 0, 800, 400  # Valores padrão
        if self.timer_window is not None:
            try:
                geometry = self.timer_window.get_geometry()
                # Parse geometry string (format: "widthxheight+x+y")
                parts = geometry.split('+')
                if len(parts) >= 3:
                    size_part = parts[0]
                    x = int(parts[1])
                    y = int(parts[2])
                    size_parts = size_part.split('x')
                    if len(size_parts) >= 2:
                        width = int(size_parts[0])
                        height = int(size_parts[1])
            except Exception:
                pass  # Usa valores padrão em caso de erro
        
        # Obter formatação atual
        fmt = self.current_format
        
        return {
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
            'mode': mode,
            'x': x,
            'y': y,
            'width': width,
            'height': height,
            'bg_color': fmt['bg_color'],
            'fg_color': fmt['fg_color'],
            'font_family': fmt['font_family'],
            'font_size': fmt['font_size'],
            'transparent': fmt['transparent']
        }
    
    def _apply_preset(self, preset_data):
        """Aplica as configurações de um preset"""
        try:
            # Aplicar tempo
            self.hours_var.set(preset_data['hours'])
            self.minutes_var.set(preset_data['minutes'])
            self.seconds_var.set(preset_data['seconds'])
            self._on_time_change()
            
            # Aplicar modo
            self.mode_var.set(preset_data['mode'])
            self._on_mode_change()
            
            # Aplicar posição e tamanho se a janela do timer existir
            if self.timer_window is not None:
                geometry = f"{preset_data['width']}x{preset_data['height']}+{preset_data['x']}+{preset_data['y']}"
                self.timer_window.set_geometry(geometry)
            
            # Aplicar formatação
            new_format = {
                'bg_color': preset_data['bg_color'],
                'fg_color': preset_data['fg_color'],
                'font_family': preset_data['font_family'],
                'font_size': preset_data['font_size'],
                'transparent': preset_data['transparent']
            }
            self._apply_formatting(new_format)
            
            messagebox.showinfo("Sucesso", f"Preset '{preset_data['name']}' carregado com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao aplicar preset: {e}")
    
    def _save_preset(self):
        """Abre modal para salvar preset"""
        # Obter nome do preset
        preset_name = simpledialog.askstring(
            "Salvar Preset",
            "Digite o nome do preset:",
            parent=self.window
        )
        
        if not preset_name or not preset_name.strip():
            return  # Usuário cancelou ou não digitou nada
        
        preset_name = preset_name.strip()
        
        # Validar nome
        if any(char in preset_name for char in '\\/:*?"<>|'):
            messagebox.showerror("Erro", "Nome do preset contém caracteres inválidos!")
            return
        
        # Verificar se já existe
        presets_folder = self._ensure_presets_folder()
        preset_file = os.path.join(presets_folder, f"{preset_name}.csv")
        if os.path.exists(preset_file):
            if not messagebox.askyesno("Sobrescrever", f"O preset '{preset_name}' já existe. Deseja sobrescrever?"):
                return
        
        # Coletar configurações atuais
        settings = self._collect_current_settings()
        settings['name'] = preset_name
        
        # Salvar preset
        if self._write_preset(preset_name, settings):
            messagebox.showinfo("Sucesso", f"Preset '{preset_name}' salvo com sucesso!")
    
    def _load_preset(self):
        """Abre modal para carregar preset"""
        if hasattr(self, '_load_window') and self._load_window is not None:
            try:
                if self._load_window.winfo_exists():
                    self._load_window.lift()
                    return
            except Exception:
                pass
        self._load_window = None
        # Listar presets disponíveis
        presets = self._list_presets()
        
        if not presets:
            messagebox.showinfo("Info", "Nenhum preset encontrado.")
            return
        
        # Criar modal de seleção
        load_window = tk.Toplevel(self.window)
        self._load_window = load_window
        load_window.title("Carregar Preset")
        load_window.geometry("400x300")
        load_window.resizable(False, False)
        load_window.transient(self.window)
        load_window.grab_set()
        load_window.focus_set()
        
        # Centralizar modal
        load_window.update_idletasks()
        x = (load_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (load_window.winfo_screenheight() // 2) - (300 // 2)
        load_window.geometry(f"+{x}+{y}")
        
        # Frame principal
        main_frame = ttk.Frame(load_window, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Label
        ttk.Label(main_frame, text="Selecione um preset:").pack(anchor="w", pady=(0, 10))
        
        # Listbox
        listbox_frame = ttk.Frame(main_frame)
        listbox_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side="right", fill="y")
        
        preset_listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set)
        preset_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=preset_listbox.yview)
        
        # Adicionar presets à listbox
        for preset in presets:
            preset_listbox.insert(tk.END, preset)
        
        # Frame dos botões
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill="x")
        
        def on_select():
            """Carrega o preset selecionado"""
            selection = preset_listbox.curselection()
            if not selection:
                return
            
            selected_preset = presets[selection[0]]
            preset_data = self._read_preset(selected_preset)
            
            if preset_data:
                self._apply_preset(preset_data)
                self._load_window = None
                load_window.destroy()
        
        def on_double_click(event):
            """Carrega preset com duplo clique"""
            on_select()
        
        # Bind duplo clique
        preset_listbox.bind("<Double-Button-1>", on_double_click)
        
        # Botões
        def on_cancel():
            self._load_window = None
            load_window.destroy()
        
        load_window.protocol("WM_DELETE_WINDOW", on_cancel)
        load_window.bind("<Escape>", lambda e: on_cancel())
        ttk.Button(buttons_frame, text="Carregar", command=on_select).pack(side="left", padx=(0, 5))
        ttk.Button(buttons_frame, text="Cancelar", command=on_cancel).pack(side="left")
