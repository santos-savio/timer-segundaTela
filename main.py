"""
Timer Desktop App para Segunda Tela
Aplicativo de timer com janela independente ideal para projeção em segunda tela.

Autor: Cascade
Descrição: Timer desktop com interface gráfica usando Tkinter
"""

import tkinter as tk
import sys
import os

# Adicionar diretório atual ao path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from timer_logic import TimerLogic
from timer_window import TimerWindow
from control_window import ControlWindow

class TimerApp:
    def __init__(self):
        # Criar instâncias das classes principais
        self.timer_logic = TimerLogic()
        self.timer_window = TimerWindow()
        self.control_window = ControlWindow(self.timer_logic, self.timer_window)
        
        # Configurar tratamento de fechamento
        self.control_window.window.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Inicializar timer com tempo padrão
        self.timer_logic.set_time(0, 1, 0)  # 1 minuto padrão
    
    def _on_closing(self):
        """Trata o evento de fechamento da aplicação"""
        try:
            # Parar o timer
            self.timer_logic.reset()
            
            # Fechar janelas
            self.timer_window.destroy()
            self.control_window.destroy()
            
            # Encerrar aplicação
            sys.exit(0)
        except Exception as e:
            print(f"Erro ao fechar aplicação: {e}")
            sys.exit(1)
    
    def run(self):
        """Inicia a aplicação"""
        try:
            # Iniciar a janela de controle (principal)
            self.control_window.run()
        except KeyboardInterrupt:
            self._on_closing()
        except Exception as e:
            print(f"Erro na execução: {e}")
            self._on_closing()

def main():
    """Função principal"""
    print("Timer Desktop App para Segunda Tela")
    print("=" * 40)
    print("Iniciando aplicação...")
    
    try:
        app = TimerApp()
        app.run()
    except Exception as e:
        print(f"Erro ao iniciar aplicação: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
