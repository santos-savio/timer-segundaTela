"""
Timer Window Module
Janela de exibição do timer sem bordas, ideal para segunda tela.
"""

import tkinter as tk
from tkinter import font as tkfont
import platform

class TimerWindow:
    def __init__(self, master=None):
        # Usar Toplevel para evitar múltiplas janelas raiz
        self.window = tk.Toplevel(master=master)
        self.window.title("Timer Display")
        
        # Configurações iniciais
        self.bg_color = "#000000"  # Preto
        self.fg_color = "#FFFFFF"  # Branco
        self.font_family = "Arial"
        self.font_size = 120
        
        # Estado da janela
        self.is_locked = True
        self.is_visible = False
        
        # Configurar janela sem bordas
        self._setup_window()
        
        # Criar label do timer
        self.timer_label = tk.Label(
            self.window,
            text="00:00",
            font=(self.font_family, self.font_size),
            bg=self.bg_color,
            fg=self.fg_color,
            anchor="center"
        )
        self.timer_label.pack(expand=True, fill="both")
        
        # Bindings para movimentação e redimensionamento
        self._setup_bindings()
        
        # Variáveis para drag
        self.start_x = 0
        self.start_y = 0
    
    def _setup_window(self):
        """Configura a janela sem bordas"""
        self.window.overrideredirect(True)  # Remove bordas e barra de título
        
        # Configurações iniciais de posição e tamanho
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # Posição centralizada por padrão
        window_width = 800
        window_height = 400
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Always on top quando travado
        if self.is_locked:
            self.window.attributes("-topmost", True)
        
        # Começar oculto para evitar flash ao iniciar a aplicação
        self.window.withdraw()
    
    def _setup_bindings(self):
        """Configura eventos de mouse para movimentação e redimensionamento"""
        # Para movimentação da janela
        self.window.bind("<Button-1>", self._on_click)
        self.window.bind("<B1-Motion>", self._on_drag)
        self.window.bind("<ButtonRelease-1>", self._on_release)
        
        # Para redimensionamento nas bordas
        self.window.bind("<Motion>", self._on_motion)
        self.window.bind("<Configure>", self._on_configure)
    
    def _on_click(self, event):
        """Evento ao clicar na janela"""
        if not self.is_locked:
            self.start_x = event.x_root - self.window.winfo_x()
            self.start_y = event.y_root - self.window.winfo_y()
    
    def _on_drag(self, event):
        """Evento ao arrastar a janela"""
        if not self.is_locked:
            x = event.x_root - self.start_x
            y = event.y_root - self.start_y
            self.window.geometry(f"+{x}+{y}")
    
    def _on_release(self, event):
        """Evento ao soltar o mouse"""
        pass
    
    def _on_motion(self, event):
        """Evento ao mover o mouse (para cursor de redimensionamento)"""
        if not self.is_locked:
            # Detectar se está na borda para mudar cursor
            width = self.window.winfo_width()
            height = self.window.winfo_height()
            
            on_edge = (event.x < 10 or event.x > width - 10 or 
                      event.y < 10 or event.y > height - 10)
            
            if on_edge:
                self.window.config(cursor="sizing")
            else:
                self.window.config(cursor="fleur")
        else:
            self.window.config(cursor="arrow")
    
    def _on_configure(self, event):
        """Evento ao redimensionar a janela"""
        # Ajustar tamanho da fonte proporcionalmente ao tamanho da janela
        if not self.is_locked:
            new_size = max(20, min(event.height // 3, 200))
            if new_size != self.font_size:
                self.font_size = new_size
                self._update_font()
    
    def update_time(self, time_str: str):
        """Atualiza o display do timer"""
        self.timer_label.config(text=time_str)
    
    def update_formatting(self, bg_color: str, fg_color: str, font_family: str, font_size: int):
        """Atualiza a formatação do timer"""
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.font_family = font_family
        self.font_size = font_size
        
        self.timer_label.config(bg=bg_color, fg=fg_color)
        self._update_font()
    
    def _update_font(self):
        """Atualiza a fonte do label"""
        try:
            self.timer_label.config(font=(self.font_family, self.font_size))
        except:
            # Se a fonte não existir, usa a padrão
            self.timer_label.config(font=("Arial", self.font_size))
    
    def show(self):
        """Mostra a janela do timer"""
        self.window.deiconify()
        self.window.lift()
        self.is_visible = True
    
    def hide(self):
        """Esconde a janela do timer"""
        self.window.withdraw()
        self.is_visible = False
    
    def set_locked(self, locked: bool):
        """Define se a janela está travada ou não"""
        self.is_locked = locked
        
        if locked:
            # Travada: always on top, não pode mover/redimensionar
            self.window.attributes("-topmost", True)
            self.window.config(cursor="arrow")
        else:
            # Destravada: pode mover/redimensionar
            self.window.attributes("-topmost", False)
            self.window.config(cursor="fleur")
    
    def get_geometry(self) -> str:
        """Retorna a geometria atual da janela"""
        return self.window.geometry()
    
    def set_geometry(self, geometry: str):
        """Define a geometria da janela"""
        self.window.geometry(geometry)
    
    def destroy(self):
        """Fecha a janela"""
        self.window.destroy()
    
    def run(self):
        """Inicia o loop principal da janela"""
        self.window.mainloop()
