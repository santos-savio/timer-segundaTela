"""
Format Modal Module
Janela modal para formatação do timer.
"""

import tkinter as tk
from tkinter import ttk, colorchooser, font
from typing import Callable, Optional, Tuple

class FormatModal:
    def __init__(self, parent, current_format: dict, apply_callback: Callable):
        self.parent = parent
        self.current_format = current_format.copy()
        self.apply_callback = apply_callback
        
        # Valores temporários para preview
        self.temp_format = current_format.copy()
        
        # Criar janela modal
        self.window = tk.Toplevel(parent)
        self.window.title("Formatação do Timer")
        self.window.geometry("500x600")
        self.window.resizable(False, False)
        
        # Tornar modal
        self.window.transient(parent)
        self.window.grab_set()
        
        # Centralizar em relação à janela pai
        self._center_window()
        
        # Criar interface
        self._create_widgets()
        
        # Configurar para fechar com ESC
        self.window.bind("<Escape>", lambda e: self.discard())
        
        # Focar na janela
        self.window.focus_set()
    
    def _center_window(self):
        """Centraliza a janela modal em relação à janela pai"""
        self.window.update_idletasks()
        
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        window_width = self.window.winfo_width()
        window_height = self.window.winfo_height()
        
        x = parent_x + (parent_width - window_width) // 2
        y = parent_y + (parent_height - window_height) // 2
        
        self.window.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """Cria os widgets da interface"""
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Seção de cores
        colors_frame = ttk.LabelFrame(main_frame, text="Cores", padding="10")
        colors_frame.pack(fill="x", pady=(0, 10))
        
        # Cor de fundo
        bg_frame = ttk.Frame(colors_frame)
        bg_frame.pack(fill="x", pady=5)
        
        ttk.Label(bg_frame, text="Cor de Fundo:").pack(side="left", padx=(0, 10))
        self.bg_color_btn = tk.Button(
            bg_frame,
            text="    ",
            bg=self.temp_format["bg_color"],
            width=10,
            command=self._choose_bg_color
        )
        self.bg_color_btn.pack(side="left", padx=(0, 10))
        
        self.bg_color_label = ttk.Label(bg_frame, text=self.temp_format["bg_color"])
        self.bg_color_label.pack(side="left")
        
        # Cor do texto
        fg_frame = ttk.Frame(colors_frame)
        fg_frame.pack(fill="x", pady=5)
        
        ttk.Label(fg_frame, text="Cor do Texto:").pack(side="left", padx=(0, 10))
        self.fg_color_btn = tk.Button(
            fg_frame,
            text="    ",
            bg=self.temp_format["fg_color"],
            width=10,
            command=self._choose_fg_color
        )
        self.fg_color_btn.pack(side="left", padx=(0, 10))
        
        self.fg_color_label = ttk.Label(fg_frame, text=self.temp_format["fg_color"])
        self.fg_color_label.pack(side="left")
        
        # Seção de fonte
        font_frame = ttk.LabelFrame(main_frame, text="Fonte", padding="10")
        font_frame.pack(fill="x", pady=(0, 10))
        
        # Família da fonte
        family_frame = ttk.Frame(font_frame)
        family_frame.pack(fill="x", pady=5)
        
        ttk.Label(family_frame, text="Fonte:").pack(side="left", padx=(0, 10))
        
        # Obter fontes disponíveis no sistema
        available_fonts = sorted(font.families())
        self.font_family_var = tk.StringVar(value=self.temp_format["font_family"])
        
        self.font_combo = ttk.Combobox(
            family_frame,
            textvariable=self.font_family_var,
            values=available_fonts,
            state="readonly",
            width=20
        )
        self.font_combo.pack(side="left", padx=(0, 10))
        self.font_combo.bind("<<ComboboxSelected>>", self._update_preview)
        
        # Tamanho da fonte
        size_frame = ttk.Frame(font_frame)
        size_frame.pack(fill="x", pady=5)
        
        ttk.Label(size_frame, text="Tamanho:").pack(side="left", padx=(0, 10))
        
        self.font_size_var = tk.IntVar(value=self.temp_format["font_size"])
        self.font_size_spin = ttk.Spinbox(
            size_frame,
            from_=10,
            to=200,
            textvariable=self.font_size_var,
            width=10,
            command=self._update_preview
        )
        self.font_size_spin.pack(side="left")
        
        # Seção de preview
        preview_frame = ttk.LabelFrame(main_frame, text="Preview", padding="10")
        preview_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        self.preview_label = tk.Label(
            preview_frame,
            text="00:00",
            anchor="center"
        )
        self.preview_label.pack(expand=True, fill="both")
        
        # Atualizar preview inicial
        self._update_preview()
        
        # Frame dos botões
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill="x", pady=(10, 0))
        
        # Botões alinhados à direita
        button_right_frame = ttk.Frame(buttons_frame)
        button_right_frame.pack(side="right")
        
        ttk.Button(
            button_right_frame,
            text="Padrão",
            command=self._reset_to_default
        ).pack(side="right", padx=(5, 0))
        
        ttk.Button(
            button_right_frame,
            text="Descartar",
            command=self.discard
        ).pack(side="right", padx=(5, 0))
        
        ttk.Button(
            button_right_frame,
            text="Aplicar",
            command=self.apply
        ).pack(side="right", padx=(5, 0))
    
    def _choose_bg_color(self):
        """Abre o seletor de cor para o fundo"""
        color = colorchooser.askcolor(initialcolor=self.temp_format["bg_color"])
        if color[1]:  # Se uma cor foi selecionada
            self.temp_format["bg_color"] = color[1]
            self.bg_color_btn.config(bg=color[1])
            self.bg_color_label.config(text=color[1])
            self._update_preview()
    
    def _choose_fg_color(self):
        """Abre o seletor de cor para o texto"""
        color = colorchooser.askcolor(initialcolor=self.temp_format["fg_color"])
        if color[1]:  # Se uma cor foi selecionada
            self.temp_format["fg_color"] = color[1]
            self.fg_color_btn.config(bg=color[1])
            self.fg_color_label.config(text=color[1])
            self._update_preview()
    
    def _update_preview(self, event=None):
        """Atualiza o preview com as configurações atuais"""
        self.temp_format["font_family"] = self.font_family_var.get()
        self.temp_format["font_size"] = self.font_size_var.get()
        
        try:
            self.preview_label.config(
                bg=self.temp_format["bg_color"],
                fg=self.temp_format["fg_color"],
                font=(self.temp_format["font_family"], min(self.temp_format["font_size"], 60))
            )
        except:
            # Se a fonte não existir, usa a padrão
            self.preview_label.config(
                bg=self.temp_format["bg_color"],
                fg=self.temp_format["fg_color"],
                font=("Arial", min(self.temp_format["font_size"], 60))
            )
    
    def _reset_to_default(self):
        """Restaura as configurações padrão"""
        default_format = {
            "bg_color": "#000000",
            "fg_color": "#FFFFFF", 
            "font_family": "Arial",
            "font_size": 120
        }
        
        self.temp_format = default_format.copy()
        
        # Atualizar widgets
        self.bg_color_btn.config(bg=default_format["bg_color"])
        self.bg_color_label.config(text=default_format["bg_color"])
        self.fg_color_btn.config(bg=default_format["fg_color"])
        self.fg_color_label.config(text=default_format["fg_color"])
        self.font_family_var.set(default_format["font_family"])
        self.font_size_var.set(default_format["font_size"])
        
        self._update_preview()
    
    def apply(self):
        """Aplica a formatação e fecha o modal"""
        self.apply_callback(self.temp_format)
        self.window.destroy()
    
    def discard(self):
        """Fecha o modal sem aplicar alterações"""
        self.window.destroy()
    
    def get_format(self) -> dict:
        """Retorna a formatação atual"""
        return self.temp_format.copy()
