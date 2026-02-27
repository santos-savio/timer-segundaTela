"""
Control Window Module
Janela de controle principal do timer.
"""

import tkinter as tk
from tkinter import ttk
from format_modal import FormatModal

class ControlWindow:
    def __init__(self, timer_logic, timer_window=None):
        self.timer_logic = timer_logic
        self.timer_window = timer_window
        
        # Formatação atual
        self.current_format = {
            "bg_color": "#000000",
            "fg_color": "#FFFFFF",
            "font_family": "Arial",
            "font_size": 120
        }
        
        # Criar janela principal
        self.window = tk.Tk()
        self.window.title("Timer Control")
        self.window.geometry("400x600")
        self.window.resizable(False, False)
        
        # Criar interface
        self._create_widgets()
        
        # Configurar callbacks
        self._setup_callbacks()
        
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
        
        # Configuração de tempo
        time_frame = ttk.LabelFrame(main_frame, text="Tempo Inicial", padding="10")
        time_frame.pack(fill="x", pady=(0, 10))
        
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
        self.minutes_var = tk.IntVar(value=0)
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
        
        # Modo do timer
        mode_frame = ttk.LabelFrame(main_frame, text="Modo", padding="10")
        mode_frame.pack(fill="x", pady=(0, 10))
        
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
        
        # Botões de controle
        control_frame = ttk.LabelFrame(main_frame, text="Controle", padding="10")
        control_frame.pack(fill="x", pady=(0, 10))
        
        # Frame dos botões principais
        buttons_frame = ttk.Frame(control_frame)
        buttons_frame.pack(fill="x")
        
        self.start_btn = ttk.Button(
            buttons_frame,
            text="Iniciar",
            command=self._start_timer
        )
        self.start_btn.pack(side="left", padx=(0, 5))
        
        self.pause_btn = ttk.Button(
            buttons_frame,
            text="Pausar",
            command=self._pause_timer,
            state="disabled"
        )
        self.pause_btn.pack(side="left", padx=(0, 5))
        
        self.reset_btn = ttk.Button(
            buttons_frame,
            text="Resetar",
            command=self._reset_timer
        )
        self.reset_btn.pack(side="left", padx=(0, 5))
        
        # Botão Formatar
        self.format_btn = ttk.Button(
            control_frame,
            text="Formatar",
            command=self._open_format_modal
        )
        self.format_btn.pack(fill="x", pady=(10, 0))
        
        # Opções
        options_frame = ttk.LabelFrame(main_frame, text="Opções", padding="10")
        options_frame.pack(fill="x", pady=(0, 10))
        
        # Projetar/Ocultar
        self.project_var = tk.BooleanVar(value=False)
        self.project_check = ttk.Checkbutton(
            options_frame,
            text="Projetar/Ocultar",
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
                    fmt["bg_color"], fmt["fg_color"], fmt["font_family"], fmt["font_size"]
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
        
        # Atualizar preview
        try:
            self.preview_label.config(
                bg=new_format["bg_color"],
                fg=new_format["fg_color"],
                font=(new_format["font_family"], 48)
            )
        except:
            self.preview_label.config(
                bg=new_format["bg_color"],
                fg=new_format["fg_color"],
                font=("Arial", 48)
            )
        
        # Atualizar janela do timer
        if self.timer_window is not None:
            self.timer_window.update_formatting(
                new_format["bg_color"],
                new_format["fg_color"],
                new_format["font_family"],
                new_format["font_size"]
            )
    
    def run(self):
        """Inicia o loop principal da janela"""
        self.window.mainloop()
    
    def destroy(self):
        """Fecha a janela"""
        self.window.destroy()
