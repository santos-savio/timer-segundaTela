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
        # Calcular tamanho inicial da fonte baseado no tamanho padrão da janela
        initial_window_height = 400
        self.font_size = max(20, min(initial_window_height // 3, 120))  # Baseado no cálculo do _on_configure
        
        # Estado da janela
        self.is_locked = True
        self.is_visible = False
        self._font_manually_set = False
        self.transparent = False
        
        # Variáveis para redimensionamento
        self.resize_mode = None  # None, 'left', 'right', 'top', 'bottom', 'corner'
        self.start_x = 0
        self.start_y = 0
        self.start_width = 0
        self.start_height = 0
        self.initial_x = 0  # Posição inicial da janela
        self.initial_y = 0
        
        # Dimensões da tela para limites
        self.screen_width = self.window.winfo_screenwidth()
        self.screen_height = self.window.winfo_screenheight()
        
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
            self.start_x = event.x_root
            self.start_y = event.y_root
            self.start_width = self.window.winfo_width()
            self.start_height = self.window.winfo_height()
            # Armazenar posição inicial correta da janela
            self.initial_x = self.window.winfo_x()
            self.initial_y = self.window.winfo_y()
            
            # Determinar modo de redimensionamento
            width = self.start_width
            height = self.start_height
            edge_threshold = 10
            
            # Detectar borda
            on_left = event.x < edge_threshold
            on_right = event.x > width - edge_threshold
            on_top = event.y < edge_threshold
            on_bottom = event.y > height - edge_threshold
            
            # Determinar tipo de redimensionamento
            # Se for redimensionamento nas bordas, liberar ajuste automático de fonte
            if on_left or on_right or on_top or on_bottom:
                self._font_manually_set = False
            
            if on_left and on_top:
                self.resize_mode = 'top_left'
            elif on_right and on_top:
                self.resize_mode = 'top_right'
            elif on_left and on_bottom:
                self.resize_mode = 'bottom_left'
            elif on_right and on_bottom:
                self.resize_mode = 'bottom_right'
            elif on_left:
                self.resize_mode = 'left'
            elif on_right:
                self.resize_mode = 'right'
            elif on_top:
                self.resize_mode = 'top'
            elif on_bottom:
                self.resize_mode = 'bottom'
            else:
                self.resize_mode = None  # Modo de movimentação
    
    def _on_drag(self, event):
        """Evento ao arrastar a janela"""
        if not self.is_locked:
            if self.resize_mode is None:
                # Movimentação normal usando delta
                dx = event.x_root - self.start_x
                dy = event.y_root - self.start_y
                new_x = self.initial_x + dx
                new_y = self.initial_y + dy
                
                # Aplicar limites de tela
                new_x, new_y = self._constrain_position(new_x, new_y)
                
                self.window.geometry(f"+{new_x}+{new_y}")
            else:
                # Redimensionamento
                self._handle_resize(event)
    
    def _handle_resize(self, event):
        """Lida com o redimensionamento da janela"""
        dx = event.x_root - self.start_x
        dy = event.y_root - self.start_y
        
        # Valores iniciais
        x = self.initial_x
        y = self.initial_y
        width = self.start_width
        height = self.start_height
        min_size = 200
        max_width = int(self.screen_width * 0.9)
        max_height = int(self.screen_height * 0.9)
        
        # Redimensionamento mantendo borda oposta fixa
        if self.resize_mode == 'left':
            new_width = max(min_size, min(max_width, width - dx))
            x = x + (width - new_width)  # Move borda esquerda
            width = new_width
        elif self.resize_mode == 'right':
            width = max(min_size, min(max_width, width + dx))
            # X permanece o mesmo (borda esquerda fixa)
        elif self.resize_mode == 'top':
            new_height = max(min_size, min(max_height, height - dy))
            y = y + (height - new_height)  # Move borda superior
            height = new_height
        elif self.resize_mode == 'bottom':
            height = max(min_size, min(max_height, height + dy))
            # Y permanece o mesmo (borda superior fixa)
        elif self.resize_mode == 'top_left':
            new_width = max(min_size, min(max_width, width - dx))
            new_height = max(min_size, min(max_height, height - dy))
            x = x + (width - new_width)
            y = y + (height - new_height)
            width = new_width
            height = new_height
        elif self.resize_mode == 'top_right':
            new_width = max(min_size, min(max_width, width + dx))
            new_height = max(min_size, min(max_height, height - dy))
            y = y + (height - new_height)
            width = new_width
            height = new_height
        elif self.resize_mode == 'bottom_left':
            new_width = max(min_size, min(max_width, width - dx))
            new_height = max(min_size, min(max_height, height + dy))
            x = x + (width - new_width)
            width = new_width
            height = new_height
        elif self.resize_mode == 'bottom_right':
            width = max(min_size, min(max_width, width + dx))
            height = max(min_size, min(max_height, height + dy))
        
        # Aplicar limites de posição
        x, y = self._constrain_position(x, y)
        
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def _on_release(self, event):
        """Evento ao soltar o mouse"""
        self.resize_mode = None
    
    def _constrain_position(self, x, y):
        """Remove limites de posição para permitir movimentação entre múltiplas telas"""
        # Sem restrições - permite movimentação livre entre telas
        return x, y
    
    def _on_motion(self, event):
        """Evento ao mover o mouse (para cursor de redimensionamento)"""
        if not self.is_locked:
            # Detectar se está na borda para mudar cursor
            width = self.window.winfo_width()
            height = self.window.winfo_height()
            edge_threshold = 10
            
            on_left = event.x < edge_threshold
            on_right = event.x > width - edge_threshold
            on_top = event.y < edge_threshold
            on_bottom = event.y > height - edge_threshold
            
            # Definir cursor apropriado
            if on_left and on_top:
                self.window.config(cursor="top_left_corner")
            elif on_right and on_top:
                self.window.config(cursor="top_right_corner")
            elif on_left and on_bottom:
                self.window.config(cursor="bottom_left_corner")
            elif on_right and on_bottom:
                self.window.config(cursor="bottom_right_corner")
            elif on_left:
                self.window.config(cursor="sb_h_double_arrow")
            elif on_right:
                self.window.config(cursor="sb_h_double_arrow")
            elif on_top:
                self.window.config(cursor="sb_v_double_arrow")
            elif on_bottom:
                self.window.config(cursor="sb_v_double_arrow")
            else:
                self.window.config(cursor="fleur")
        else:
            self.window.config(cursor="arrow")
    
    def _on_configure(self, event):
        """Evento ao redimensionar a janela"""
        # Ajustar tamanho da fonte proporcionalmente ao tamanho da janela
        # Apenas quando a janela está desbloqueada E a fonte não foi definida manualmente
        if not self.is_locked and not self._font_manually_set:
            new_size = max(20, min(event.height // 3, 120))  # Limite máximo de 120pt
            if new_size != self.font_size:
                self.font_size = new_size
                self._update_font()
    
    def update_time(self, time_str: str):
        """Atualiza o display do timer"""
        self.timer_label.config(text=time_str)
    
    def update_formatting(self, bg_color: str, fg_color: str, font_family: str, font_size: int, transparent: bool = False):
        """Atualiza a formatação do timer"""
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.font_family = font_family
        self.font_size = font_size
        self._font_manually_set = True
        self.transparent = transparent

        # Configurar transparência usando a cor de fundo escolhida como chave
        if transparent:
            try:
                # Define a cor bg_color como transparente para a janela inteira
                self.window.attributes('-transparentcolor', bg_color)
            except Exception:
                pass
            # Garantir que tanto a janela quanto o label usem a mesma cor-chave
            self.window.configure(bg=bg_color)
        else:
            # Remover transparência se suportado
            try:
                self.window.attributes('-transparentcolor', '')
            except Exception:
                pass
            # Em modo normal, alinhar a cor de fundo da janela ao label
            self.window.configure(bg=bg_color)

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
        
        # Reaplicar transparência se necessário (para garantir efeito na primeira exibição)
        if self.transparent:
            try:
                self.window.attributes('-transparentcolor', self.bg_color)
                self.window.configure(bg=self.bg_color)
            except Exception:
                pass
    
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
