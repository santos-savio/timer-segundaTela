"""
Control Window Module
Janela de controle principal do timer.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter import font as tkfont
from format_modal import FormatModal
import os
import csv
from datetime import datetime
import re
try:
    from screeninfo import get_monitors
except ImportError:
    get_monitors = None  # Fallback para caso screeninfo não esteja instalado

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
        self.window.geometry("780x650")
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
        
        # Preview unificado: mostra o timer e permite posicioná-lo no monitor selecionado
        top_container = ttk.Frame(main_frame)
        top_container.pack(fill="x", pady=(0, 10))

        self.preview_frame = ttk.LabelFrame(
            top_container,
            text="Preview / Posição",
            padding="10"
        )
        self.preview_frame.pack(anchor="w")

        self._create_preview_map(self.preview_frame)

        # Iniciar polling do mapa de posição
        self._refresh_position_map()

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
        
        # Container horizontal para presets e monitores
        presets_monitors_container = ttk.Frame(main_frame)
        presets_monitors_container.pack(fill="x", pady=(0, 10))
        
        # Frame de presets
        presets_frame = ttk.LabelFrame(presets_monitors_container, text="Presets", padding="10")
        presets_frame.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
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
        
        # Frame de monitores
        monitors_frame = ttk.LabelFrame(presets_monitors_container, text="Monitores", padding="10")
        monitors_frame.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        # Listbox de monitores
        self.monitors_listbox = tk.Listbox(
            monitors_frame,
            height=3,
            exportselection=False
        )
        self.monitors_listbox.pack(fill="x", pady=(0, 5))
        
        # Frame para botões de monitores
        monitors_buttons_frame = ttk.Frame(monitors_frame)
        monitors_buttons_frame.pack(fill="x", pady=(5, 0))
        
        # Botão Identificar telas
        self.identify_btn = ttk.Button(
            monitors_buttons_frame,
            text="Identificar telas",
            underline=-1,
            command=self._identify_screens
        )
        self.identify_btn.pack(side="left", fill="x", expand=True, padx=(0, 2))
        
        # Botão Aplicar ao preview
        self.apply_monitor_btn = ttk.Button(
            monitors_buttons_frame,
            text="Aplicar ao preview",
            underline=-1,
            command=self._apply_monitor_to_preview
        )
        self.apply_monitor_btn.pack(side="left", fill="x", expand=True, padx=(2, 0))
        
        # Configurar pesos das colunas do container presets/monitores
        presets_monitors_container.grid_columnconfigure(0, weight=1)
        presets_monitors_container.grid_columnconfigure(1, weight=1)
        
        # Preencher listbox de monitores
        self._populate_monitors_listbox()

        # Iniciar polling de monitores (reconhece telas conectadas com o app aberto)
        self.window.after(3000, self._poll_monitors)
    
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
        self.preview_canvas.itemconfig(self.preview_label, text=time_str)
        
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
        """Força atualização imediata do tempo, em qualquer estado do timer (rodando, pausado ou parado)"""
        hours = self.hours_var.get()
        minutes = self.minutes_var.get()
        seconds = self.seconds_var.get()
        # force_set_time atualiza o tempo atual e notifica via callback,
        # que já propaga para o preview e para a janela projetada.
        self.timer_logic.force_set_time(hours, minutes, seconds)
    
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

            # Re-escanear monitores para reconhecer telas conectadas após abrir o app
            self._check_monitors_changed()

            # Posicionar no monitor selecionado conforme o quadro de preview
            self._apply_projection_geometry()

            self.timer_window.show()
        else:
            self.timer_window.hide()

    def _apply_projection_geometry(self):
        """Aplica ao timer a geometria definida no preview, no monitor selecionado"""
        if self.timer_window is None:
            return
        if not (self._monitors and self._selected_monitor_index < len(self._monitors)):
            return

        monitor = self._monitors[self._selected_monitor_index]
        g = self._timer_geom

        # Garantir que o timer caiba dentro do monitor selecionado
        w = min(g['w'], monitor.width)
        h = min(g['h'], monitor.height)
        x = max(0, min(g['x'], monitor.width - w))
        y = max(0, min(g['y'], monitor.height - h))
        self._timer_geom = {'x': x, 'y': y, 'w': w, 'h': h}

        # A posição relativa é somada ao offset do monitor no desktop virtual
        abs_x = monitor.x + x
        abs_y = monitor.y + y

        print(f"[Timer] Exibindo no Monitor {self._selected_monitor_index + 1} "
              f"({monitor.width}x{monitor.height} @ {monitor.x},{monitor.y}) | "
              f"Posição: {x},{y} (relativa) -> {abs_x},{abs_y} (absoluta) | "
              f"Tamanho: {w}x{h}")

        self.timer_window.window.geometry(f"{w}x{h}+{abs_x}+{abs_y}")
    
    def _toggle_adjust(self):
        """Alterna o ajuste de posição e tamanho"""
        is_locked = not self.adjust_var.get()
        if self.timer_window is not None:
            self.timer_window.set_locked(is_locked)
        self._update_map_interaction()
    
    def _center_bottom_right(self):
        """Posiciona o timer no canto inferior direito do monitor selecionado"""
        if self.timer_window is None:
            return

        if self._monitors and self._selected_monitor_index < len(self._monitors):
            m = self._monitors[self._selected_monitor_index]
            mon_x, mon_y, mon_w, mon_h = m.x, m.y, m.width, m.height
        else:
            mon_x, mon_y = 0, 0
            mon_w = self.timer_window.window.winfo_screenwidth()
            mon_h = self.timer_window.window.winfo_screenheight()

        # Usar o cache de geometria (válido mesmo com a janela oculta)
        g = self._timer_geom
        w, h = g['w'], g['h']

        # Posição inferior direita relativa ao monitor (com margem de 20px)
        x = max(0, mon_w - w - 20)
        y = max(0, mon_h - h - 20)
        self._timer_geom = {'x': x, 'y': y, 'w': w, 'h': h}

        # Aplicar posição absoluta no desktop virtual
        self.timer_window.window.geometry(f"{w}x{h}+{mon_x + x}+{mon_y + y}")

        # Se a janela estiver oculta, mostrar para feedback visual
        if not self.is_projected:
            self.timer_window.window.deiconify()
            self.timer_window.window.lift()
    
    def _create_preview_map(self, parent):
        """Cria o canvas unificado de preview e posicionamento do timer.

        O canvas representa o monitor selecionado; o retângulo interno mostra o
        timer com as cores e o texto reais, e pode ser arrastado/redimensionado
        para posicionar a janela projetada.
        """
        # Suporte a múltiplos monitores
        self._monitors = self._get_monitors_list()
        self._selected_monitor_index = 0  # Índice do monitor selecionado
        self._identification_windows = []  # Janelas de identificação

        # Resolução da tela destino (ajustada ao selecionar outro monitor)
        if self._monitors:
            self._map_screen_w = self._monitors[0].width
            self._map_screen_h = self._monitors[0].height
        else:
            self._map_screen_w = self.window.winfo_screenwidth()
            self._map_screen_h = self.window.winfo_screenheight()

        # Dimensões do canvas proporcional ao monitor
        self._map_canvas_h = 189
        self._map_canvas_w = int(self._map_canvas_h * self._map_screen_w / self._map_screen_h)

        self.preview_canvas = tk.Canvas(
            parent,
            width=self._map_canvas_w,
            height=self._map_canvas_h,
            bg="#1a1a2e",
            highlightthickness=1,
            highlightbackground="#444"
        )
        self.preview_canvas.pack()
        # Preview e mapa de posição compartilham o mesmo canvas
        self.map_canvas = self.preview_canvas

        # Retângulo representando o timer, com a cor de fundo atual
        self._map_rect = self.map_canvas.create_rectangle(
            0, 0, 60, 30,
            outline="#4fc3f7",
            fill=self.current_format["bg_color"],
            width=2
        )

        # Texto do timer dentro do retângulo
        self.preview_label = self.map_canvas.create_text(
            30, 15,
            text="00:00",
            font=(self.current_format["font_family"], 12),
            fill=self.current_format["fg_color"]
        )

        # Label de coordenadas
        self._map_coord_text = self.map_canvas.create_text(
            self._map_canvas_w // 2,
            self._map_canvas_h - 8,
            text="",
            fill="#aaa",
            font=("Arial", 7)
        )

        # Cache da geometria do timer relativa ao monitor selecionado
        # (válido mesmo quando oculto)
        self._timer_geom = {'x': 0, 'y': 0, 'w': 800, 'h': 400}

        # Estado do drag/resize
        self._map_drag_start_x = 0
        self._map_drag_start_y = 0
        self._map_drag_rect_x1 = 0
        self._map_drag_rect_y1 = 0
        self._map_drag_rect_x2 = 0
        self._map_drag_rect_y2 = 0
        self._map_dragging = False
        self._map_resize_mode = None  # None = move, ou 'n','s','e','w','ne','nw','se','sw'

    def _get_live_timer_geometry(self):
        """Retorna a geometria absoluta atual do timer, ou None se oculto/indisponível."""
        if self.timer_window is None:
            return None

        tw = self.timer_window.window
        # Quando oculto (withdrawn), o cache relativo em self._timer_geom é a fonte
        # de verdade; retornar None evita converter coordenadas duas vezes.
        try:
            if tw.state() == 'withdrawn':
                return None
        except Exception:
            return None

        try:
            geometry = tw.geometry()
            # Ex.: "800x400+100+200" ou "800x400-1920+100"
            match = re.match(r"^(\d+)x(\d+)([+-]\d+)([+-]\d+)$", geometry)
            if match:
                return {
                    'w': int(match.group(1)),
                    'h': int(match.group(2)),
                    'x': int(match.group(3)),
                    'y': int(match.group(4)),
                }
        except Exception:
            pass

        # Fallback para casos inesperados de parse
        try:
            tw.update_idletasks()
            w = tw.winfo_width()
            h = tw.winfo_height()
            if w > 1:
                return {'x': tw.winfo_x(), 'y': tw.winfo_y(), 'w': w, 'h': h}
        except Exception:
            pass

        return None

    def _fit_font_to_size(self, width, height, pad_w=0.92, pad_h=0.9):
        """Tamanho de fonte (px de tela) para o texto do timer preencher width×height.

        Mede o texto atual em um tamanho de referência e escala proporcionalmente
        para que ele ocupe a maior parte possível do quadro sem transbordar.
        """
        family = self.current_format.get("font_family", "Arial")
        text = self.timer_logic.format_time() or "00:00"
        ref = 100
        try:
            f = tkfont.Font(family=family, size=ref)
        except Exception:
            f = tkfont.Font(family="Arial", size=ref)
        text_w = max(1, f.measure(text))
        text_h = max(1, f.metrics("linespace"))
        scale = min((width * pad_w) / text_w, (height * pad_h) / text_h)
        return max(8, int(ref * scale))

    def _sync_preview_text(self):
        """Centraliza o texto do timer no retângulo e escala a fonte ao preview"""
        coords = self.map_canvas.coords(self._map_rect)
        if not coords:
            return
        rx1, ry1, rx2, ry2 = coords
        cx = (rx1 + rx2) / 2
        cy = (ry1 + ry2) / 2
        sy = self._map_canvas_h / self._map_screen_h
        size = max(6, int(self.current_format["font_size"] * sy))
        self.map_canvas.coords(self.preview_label, cx, cy)
        try:
            self.map_canvas.itemconfig(
                self.preview_label,
                font=(self.current_format["font_family"], size)
            )
        except Exception:
            self.map_canvas.itemconfig(self.preview_label, font=("Arial", size))

    def _refresh_position_map(self):
        """Atualiza o mapa de posição com a geometria atual do timer"""
        # Não atualiza enquanto o usuário está interagindo (evita salto ao arrastar)
        if not getattr(self, '_map_dragging', False):
            try:
                if hasattr(self, 'map_canvas'):
                    monitor_x, monitor_y = 0, 0
                    if self._monitors and self._selected_monitor_index < len(self._monitors):
                        m = self._monitors[self._selected_monitor_index]
                        monitor_x, monitor_y = m.x, m.y

                    live = self._get_live_timer_geometry()
                    if live is not None:
                        self._timer_geom = {
                            'x': live['x'] - monitor_x,
                            'y': live['y'] - monitor_y,
                            'w': live['w'],
                            'h': live['h'],
                        }
                    g = self._timer_geom

                    sx = self._map_canvas_w / self._map_screen_w
                    sy = self._map_canvas_h / self._map_screen_h

                    rx1 = int(g['x'] * sx)
                    ry1 = int(g['y'] * sy)
                    rx2 = int((g['x'] + g['w']) * sx)
                    ry2 = int((g['y'] + g['h']) * sy)

                    self.map_canvas.coords(self._map_rect, rx1, ry1, rx2, ry2)
                    self.map_canvas.itemconfig(
                        self._map_coord_text,
                        text=f"{g['x']},{g['y']}  {g['w']}×{g['h']}"
                    )
                    self._sync_preview_text()
            except Exception:
                pass
        self.window.after(200, self._refresh_position_map)

    def _update_map_interaction(self):
        """Liga ou desliga os bindings de drag/resize no mapa conforme o estado de ajuste"""
        if not hasattr(self, 'map_canvas'):
            return
        if self.adjust_var.get():
            self.map_canvas.bind("<Button-1>", self._on_map_drag_start)
            self.map_canvas.bind("<B1-Motion>", self._on_map_drag)
            self.map_canvas.bind("<ButtonRelease-1>", self._on_map_drag_end)
            self.map_canvas.bind("<Motion>", self._on_map_motion)
        else:
            self.map_canvas.unbind("<Button-1>")
            self.map_canvas.unbind("<B1-Motion>")
            self.map_canvas.unbind("<ButtonRelease-1>")
            self.map_canvas.unbind("<Motion>")
            self.map_canvas.config(cursor="arrow")

    def _map_get_resize_mode(self, event, rx1, ry1, rx2, ry2):
        """Detecta o modo de resize/move com base na posição do cursor no retângulo"""
        edge = max(5, int(min(rx2 - rx1, ry2 - ry1) * 0.2))
        on_n = ry1 <= event.y <= ry1 + edge
        on_s = ry2 - edge <= event.y <= ry2
        on_w = rx1 <= event.x <= rx1 + edge
        on_e = rx2 - edge <= event.x <= rx2
        if on_n and on_w: return 'nw'
        if on_n and on_e: return 'ne'
        if on_s and on_w: return 'sw'
        if on_s and on_e: return 'se'
        if on_n: return 'n'
        if on_s: return 's'
        if on_w: return 'w'
        if on_e: return 'e'
        return None  # interior = mover

    def _on_map_motion(self, event):
        """Atualiza o cursor conforme a posição sobre o retângulo"""
        coords = self.map_canvas.coords(self._map_rect)
        if not coords:
            self.map_canvas.config(cursor="arrow")
            return
        rx1, ry1, rx2, ry2 = coords
        if not (rx1 <= event.x <= rx2 and ry1 <= event.y <= ry2):
            self.map_canvas.config(cursor="arrow")
            return
        mode = self._map_get_resize_mode(event, rx1, ry1, rx2, ry2)
        cursor_map = {
            'nw': 'top_left_corner', 'ne': 'top_right_corner',
            'sw': 'bottom_left_corner', 'se': 'bottom_right_corner',
            'n': 'sb_v_double_arrow', 's': 'sb_v_double_arrow',
            'w': 'sb_h_double_arrow', 'e': 'sb_h_double_arrow',
            None: 'fleur'
        }
        self.map_canvas.config(cursor=cursor_map.get(mode, 'fleur'))

    def _on_map_drag_start(self, event):
        """Inicia o drag ou resize do retângulo no mapa"""
        coords = self.map_canvas.coords(self._map_rect)
        if not coords:
            return
        rx1, ry1, rx2, ry2 = coords
        if not (rx1 <= event.x <= rx2 and ry1 <= event.y <= ry2):
            self._map_dragging = False
            return
        self._map_drag_start_x = event.x
        self._map_drag_start_y = event.y
        self._map_drag_rect_x1 = rx1
        self._map_drag_rect_y1 = ry1
        self._map_drag_rect_x2 = rx2
        self._map_drag_rect_y2 = ry2
        self._map_resize_mode = self._map_get_resize_mode(event, rx1, ry1, rx2, ry2)
        self._map_dragging = True

    def _on_map_drag(self, event):
        """Move ou redimensiona o retângulo enquanto arrasta"""
        if not self._map_dragging:
            return
        dx = event.x - self._map_drag_start_x
        dy = event.y - self._map_drag_start_y
        x1 = self._map_drag_rect_x1
        y1 = self._map_drag_rect_y1
        x2 = self._map_drag_rect_x2
        y2 = self._map_drag_rect_y2
        # Limites mínimos coerentes com TimerWindow (_handle_resize usa 200px)
        screen_per_canvas_x = self._map_screen_w / self._map_canvas_w
        screen_per_canvas_y = self._map_screen_h / self._map_canvas_h
        min_w_map = max(8, int(200 / screen_per_canvas_x))
        min_h_map = max(8, int(200 / screen_per_canvas_y))
        mode = self._map_resize_mode

        if mode is None:  # mover
            x1 += dx; x2 += dx
            y1 += dy; y2 += dy
        elif mode == 'n':
            y1 = min(y1 + dy, y2 - min_h_map)
        elif mode == 's':
            y2 = max(y2 + dy, y1 + min_h_map)
        elif mode == 'w':
            x1 = min(x1 + dx, x2 - min_w_map)
        elif mode == 'e':
            x2 = max(x2 + dx, x1 + min_w_map)
        elif mode == 'nw':
            x1 = min(x1 + dx, x2 - min_w_map)
            y1 = min(y1 + dy, y2 - min_h_map)
        elif mode == 'ne':
            x2 = max(x2 + dx, x1 + min_w_map)
            y1 = min(y1 + dy, y2 - min_h_map)
        elif mode == 'sw':
            x1 = min(x1 + dx, x2 - min_w_map)
            y2 = max(y2 + dy, y1 + min_h_map)
        elif mode == 'se':
            x2 = max(x2 + dx, x1 + min_w_map)
            y2 = max(y2 + dy, y1 + min_h_map)

        # Clamp rect to canvas bounds
        x1 = max(0, min(x1, self._map_canvas_w - min_w_map))
        y1 = max(0, min(y1, self._map_canvas_h - min_h_map))
        x2 = max(x1 + min_w_map, min(x2, self._map_canvas_w))
        y2 = max(y1 + min_h_map, min(y2, self._map_canvas_h))

        self.map_canvas.coords(self._map_rect, x1, y1, x2, y2)

        sx = self._map_screen_w / self._map_canvas_w
        sy = self._map_screen_h / self._map_canvas_h
        real_x = int(x1 * sx)
        real_y = int(y1 * sy)
        real_w = int((x2 - x1) * sx)
        real_h = int((y2 - y1) * sy)

        # Ao redimensionar, a fonte acompanha o quadro para preenchê-lo
        if mode is not None:
            self.current_format["font_size"] = self._fit_font_to_size(real_w, real_h)

        self._sync_preview_text()
        self.map_canvas.itemconfig(
            self._map_coord_text,
            text=f"{real_x},{real_y}  {real_w}×{real_h}"
        )

    def _on_map_drag_end(self, event):
        """Aplica posição e tamanho ao timer_window ao soltar"""
        if not self._map_dragging:
            return
        self._map_dragging = False
        if self.timer_window is None:
            return
        coords = self.map_canvas.coords(self._map_rect)
        if not coords:
            return
        rx1, ry1, rx2, ry2 = coords
        sx = self._map_screen_w / self._map_canvas_w
        sy = self._map_screen_h / self._map_canvas_h
        real_x = int(rx1 * sx)
        real_y = int(ry1 * sy)
        raw_w = max(1, int((rx2 - rx1) * sx))
        raw_h = max(1, int((ry2 - ry1) * sy))

        # Respeitar tamanho mínimo e preservar proporção do retângulo ajustado
        min_size = 200
        ratio = raw_w / raw_h
        real_w = raw_w
        real_h = raw_h
        if real_w < min_size or real_h < min_size:
            if ratio >= 1:
                real_w = max(real_w, min_size)
                real_h = max(min_size, int(real_w / ratio))
            else:
                real_h = max(real_h, min_size)
                real_w = max(min_size, int(real_h * ratio))

        monitor_x, monitor_y = 0, 0
        monitor_label = "Monitor 1 (padrão)"
        if self._monitors and self._selected_monitor_index < len(self._monitors):
            m = self._monitors[self._selected_monitor_index]
            monitor_x, monitor_y = m.x, m.y
            monitor_label = f"Monitor {self._selected_monitor_index + 1} ({m.width}x{m.height} @ {m.x},{m.y})"

        self._timer_geom = {'x': real_x, 'y': real_y, 'w': real_w, 'h': real_h}
        abs_x = real_x + monitor_x
        abs_y = real_y + monitor_y

        # Fonte final que preenche o quadro, aplicada ao preview e ao timer
        self.current_format["font_size"] = self._fit_font_to_size(real_w, real_h)
        self._sync_preview_text()

        print(f"[Timer] Reposicionado via mapa | {monitor_label} | "
              f"Posição: {real_x},{real_y} (relativa) -> {abs_x},{abs_y} (absoluta) | "
              f"Tamanho: {real_w}x{real_h} | Fonte: {self.current_format['font_size']}")
        self.timer_window.window.geometry(f"{real_w}x{real_h}+{abs_x}+{abs_y}")
        fmt = self.current_format
        self.timer_window.update_formatting(
            fmt["bg_color"], fmt["fg_color"], fmt["font_family"],
            fmt["font_size"], fmt.get("transparent", False)
        )

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

        # Atualizar preview (retângulo do timer no mapa de posição)
        try:
            self.preview_canvas.itemconfig(self._map_rect, fill=bg_color)
            self.preview_canvas.itemconfig(
                self.preview_label,
                fill=new_format["fg_color"]
            )
            self._sync_preview_text()
        except Exception:
            pass
        
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
    
    # Métodos para suporte a múltiplos monitores
    
    def _get_monitors_list(self, verbose=True):
        """Obtém a lista de monitores disponíveis"""
        if get_monitors is None:
            if verbose:
                print("[Timer] screeninfo não disponível — monitor único assumido")
            return []
        try:
            monitors = list(get_monitors())
            if verbose:
                for i, mon in enumerate(monitors):
                    primary = " [Principal]" if getattr(mon, 'is_primary', False) else ""
                    print(f"[Timer] Monitor {i + 1}{primary}: {mon.width}x{mon.height} @ {mon.x},{mon.y}")
            return monitors
        except Exception as e:
            if verbose:
                print(f"[Timer] Erro ao obter monitores: {e}")
            return []

    def _monitors_signature(self, monitors):
        """Assinatura da configuração de monitores para detectar mudanças"""
        return [
            (getattr(m, 'name', ''), m.x, m.y, m.width, m.height)
            for m in monitors
        ]

    def _check_monitors_changed(self):
        """Re-escaneia os monitores e atualiza a interface se houve mudança (hot-plug)"""
        try:
            new_monitors = self._get_monitors_list(verbose=False)
        except Exception:
            return
        if self._monitors_signature(new_monitors) != self._monitors_signature(self._monitors):
            self._on_monitors_changed(new_monitors)

    def _poll_monitors(self):
        """Polling periódico para reconhecer telas conectadas com o app já aberto"""
        self._check_monitors_changed()
        self.window.after(3000, self._poll_monitors)

    def _on_monitors_changed(self, new_monitors):
        """Atualiza lista, preview e projeção após mudança nos monitores"""
        old_name = None
        if self._monitors and self._selected_monitor_index < len(self._monitors):
            old_name = getattr(self._monitors[self._selected_monitor_index], 'name', None)

        self._monitors = new_monitors
        print(f"[Timer] Mudança nos monitores detectada — {len(new_monitors)} monitor(es) ativo(s)")
        for i, mon in enumerate(new_monitors):
            primary = " [Principal]" if getattr(mon, 'is_primary', False) else ""
            print(f"[Timer] Monitor {i + 1}{primary}: {mon.width}x{mon.height} @ {mon.x},{mon.y}")

        self._populate_monitors_listbox()

        # Tentar manter o monitor selecionado anteriormente
        if old_name:
            for i, m in enumerate(new_monitors):
                if getattr(m, 'name', None) == old_name:
                    self._selected_monitor_index = i
                    self.monitors_listbox.selection_clear(0, tk.END)
                    self.monitors_listbox.selection_set(i)
                    break

        self._update_map_for_selected_monitor()

        # Se estiver projetando, reposicionar no monitor válido
        if self.is_projected:
            self._apply_projection_geometry()
    
    def _populate_monitors_listbox(self):
        """Preenche o listbox com a lista de monitores"""
        self.monitors_listbox.delete(0, tk.END)
        
        if not self._monitors:
            self.monitors_listbox.insert(tk.END, "Nenhum monitor detectado")
            return
        
        for i, monitor in enumerate(self._monitors):
            name = getattr(monitor, 'name', f'Monitor {i+1}')
            primary = " (Principal)" if getattr(monitor, 'is_primary', False) else ""
            resolution = f"{monitor.width}x{monitor.height}"
            self.monitors_listbox.insert(tk.END, f"{i+1}. {name}{primary} - {resolution}")
        
        # Selecionar o monitor principal por padrão
        for i, monitor in enumerate(self._monitors):
            if getattr(monitor, 'is_primary', False):
                self.monitors_listbox.selection_set(i)
                self._selected_monitor_index = i
                break
        else:
            if self._monitors:
                self.monitors_listbox.selection_set(0)
                self._selected_monitor_index = 0
        
        # Bind para mudança de seleção
        self.monitors_listbox.bind('<<ListboxSelect>>', self._on_monitor_select)

        # Ajustar o preview às proporções do monitor selecionado
        self._update_map_for_selected_monitor()

    def _on_monitor_select(self, event):
        """Callback quando um monitor é selecionado"""
        selection = self.monitors_listbox.curselection()
        if selection:
            self._selected_monitor_index = selection[0]
            # Atualizar o mapa de posição para o monitor selecionado
            self._update_map_for_selected_monitor()
            # Se já estiver projetando, mover o timer para o novo monitor
            if self.is_projected:
                self._apply_projection_geometry()

    def _update_map_for_selected_monitor(self):
        """Atualiza o mapa de posição para o monitor selecionado"""
        if self._selected_monitor_index >= len(self._monitors):
            return

        monitor = self._monitors[self._selected_monitor_index]
        self._map_screen_w = monitor.width
        self._map_screen_h = monitor.height

        # Redimensionar o canvas se necessário
        new_canvas_w = int(self._map_canvas_h * self._map_screen_w / self._map_screen_h)
        if new_canvas_w != self._map_canvas_w:
            self._map_canvas_w = new_canvas_w
            self.map_canvas.config(width=self._map_canvas_w)
            self.map_canvas.coords(
                self._map_coord_text,
                self._map_canvas_w // 2,
                self._map_canvas_h - 8
            )

        # Redesenhar o retângulo do timer com as novas proporções
        if hasattr(self, 'map_canvas') and hasattr(self, '_map_rect'):
            # Garantir que a geometria caiba no monitor selecionado
            g = self._timer_geom
            w = min(g['w'], monitor.width)
            h = min(g['h'], monitor.height)
            x = max(0, min(g['x'], monitor.width - w))
            y = max(0, min(g['y'], monitor.height - h))
            g = {'x': x, 'y': y, 'w': w, 'h': h}
            self._timer_geom = g

            sx = self._map_canvas_w / self._map_screen_w
            sy = self._map_canvas_h / self._map_screen_h

            rx1 = int(g['x'] * sx)
            ry1 = int(g['y'] * sy)
            rx2 = int((g['x'] + g['w']) * sx)
            ry2 = int((g['y'] + g['h']) * sy)

            self.map_canvas.coords(self._map_rect, rx1, ry1, rx2, ry2)
            self.map_canvas.itemconfig(
                self._map_coord_text,
                text=f"{g['x']},{g['y']}  {g['w']}×{g['h']}"
            )
            self._sync_preview_text()
    
    def _apply_monitor_to_preview(self):
        """Define o monitor onde o timer será exibido ao projetar"""
        selection = self.monitors_listbox.curselection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um monitor primeiro.")
            return

        if not self._monitors:
            messagebox.showwarning("Aviso", "Nenhum monitor detectado.")
            return

        monitor_index = selection[0]
        if monitor_index >= len(self._monitors):
            return

        monitor = self._monitors[monitor_index]
        self._selected_monitor_index = monitor_index
        self._update_map_for_selected_monitor()
        if self.is_projected:
            self._apply_projection_geometry()

        print(f"[Timer] Monitor {monitor_index + 1} definido para projeção | "
              f"{monitor.width}x{monitor.height} @ {monitor.x},{monitor.y}")

        messagebox.showinfo(
            "Monitor Definido",
            f"Timer será exibido no Monitor {monitor_index + 1}\n"
            f"Resolução: {monitor.width}x{monitor.height}\n\n"
            f"Ative a projeção para visualizar."
        )
    
    def _identify_screens(self):
        """Exibe janelas de identificação em cada monitor"""
        # Re-escanear para reconhecer telas conectadas após abrir o app
        self._check_monitors_changed()

        print("\n=== DEBUG: _identify_screens chamada ===")
        print(f"Número de monitores detectados: {len(self._monitors)}")
        print(f"get_monitors disponível: {get_monitors is not None}")
        
        # Fechar janelas de identificação anteriores
        for win in self._identification_windows:
            try:
                win.destroy()
            except:
                pass
        self._identification_windows = []
        
        if not self._monitors:
            print("DEBUG: Nenhum monitor na lista self._monitors")
            messagebox.showinfo("Identificação", "Nenhum monitor detectado.")
            return
        
        # Criar janela de identificação para cada monitor
        for i, monitor in enumerate(self._monitors):
            print(f"\nDEBUG: Criando janela para monitor {i+1}")
            print(f"  - Nome: {getattr(monitor, 'name', 'N/A')}")
            print(f"  - Posição: x={monitor.x}, y={monitor.y}")
            print(f"  - Resolução: {monitor.width}x{monitor.height}")
            print(f"  - Primary: {getattr(monitor, 'is_primary', False)}")
            
            win = tk.Toplevel(self.window)
            win.overrideredirect(True)  # Sem bordas
            win.attributes("-topmost", True)  # Sempre visível
            
            # Calcular posição central no monitor
            center_x = monitor.x + monitor.width // 2
            center_y = monitor.y + monitor.height // 2
            
            # Tamanho da janela de identificação
            win_w, win_h = 200, 200
            win_x = center_x - win_w // 2
            win_y = center_y - win_h // 2
            
            print(f"  - Posição da janela: {win_x}+{win_y}")
            print(f"  - Tamanho da janela: {win_w}x{win_h}")
            
            win.geometry(f"{win_w}x{win_h}+{win_x}+{win_y}")
            win.configure(bg="#2196F3")
            
            # Número do monitor
            label = tk.Label(
                win,
                text=str(i + 1),
                font=("Arial", 72, "bold"),
                bg="#2196F3",
                fg="white"
            )
            label.pack(expand=True, fill="both")
            
            # Nome do monitor
            name = getattr(monitor, 'name', f'Monitor {i+1}')
            name_label = tk.Label(
                win,
                text=name,
                font=("Arial", 10),
                bg="#2196F3",
                fg="white"
            )
            name_label.pack(pady=(0, 10))
            
            self._identification_windows.append(win)
            print(f"  - Janela criada e adicionada à lista")
        
        print(f"\nDEBUG: Total de janelas de identificação criadas: {len(self._identification_windows)}")
        print("DEBUG: Agendando fechamento automático em 3 segundos")
        
        # Fechar automaticamente após 3 segundos
        self.window.after(3000, self._close_identification_windows)
    
    def _close_identification_windows(self):
        """Fecha todas as janelas de identificação"""
        print("\n=== DEBUG: _close_identification_windows chamada ===")
        print(f"Número de janelas para fechar: {len(self._identification_windows)}")
        
        for i, win in enumerate(self._identification_windows):
            try:
                print(f"  - Fechando janela {i+1}")
                win.destroy()
            except Exception as e:
                print(f"  - Erro ao fechar janela {i+1}: {e}")
        
        self._identification_windows = []
        print("DEBUG: Todas as janelas fechadas")
