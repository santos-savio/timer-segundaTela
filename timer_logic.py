"""
Timer Logic Module
Gerencia a lógica do timer incluindo contagem, estados e formatação.
"""

import time
from threading import Thread, Event
from typing import Callable, Optional

class TimerMode:
    COUNTDOWN = "countdown"  # Decrescente
    STOPWATCH = "stopwatch"  # Crescente

class TimerState:
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"

class TimerLogic:
    def __init__(self):
        self._hours = 0
        self._minutes = 0
        self._seconds = 0
        self._initial_hours = 0
        self._initial_minutes = 0
        self._initial_seconds = 0
        
        self._mode = TimerMode.COUNTDOWN
        self._state = TimerState.STOPPED
        
        self._current_time = 0  # Tempo em segundos
        self._stop_event = Event()
        self._thread: Optional[Thread] = None
        
        # Callbacks para atualização da UI
        self._update_callback: Optional[Callable] = None
        self._state_callback: Optional[Callable] = None
        
    def set_update_callback(self, callback: Callable[[str], None]):
        """Define callback para atualização do display"""
        self._update_callback = callback
        
    def set_state_callback(self, callback: Callable[[str], None]):
        """Define callback para mudança de estado"""
        self._state_callback = callback
        
    def set_time(self, hours: int, minutes: int, seconds: int):
        """Define o tempo inicial"""
        self._hours = hours
        self._minutes = minutes
        self._seconds = seconds
        self._initial_hours = hours
        self._initial_minutes = minutes
        self._initial_seconds = seconds
        
        if self._state == TimerState.STOPPED:
            self._current_time = hours * 3600 + minutes * 60 + seconds
            self._notify_update()
    
    def set_mode(self, mode: str):
        """Define o modo do timer (countdown ou stopwatch)"""
        self._mode = mode
        self.reset()
    
    def get_mode(self) -> str:
        """Retorna o modo atual"""
        return self._mode
    
    def get_state(self) -> str:
        """Retorna o estado atual"""
        return self._state
    
    def start(self):
        """Inicia o timer"""
        if self._state != TimerState.RUNNING:
            self._state = TimerState.RUNNING
            self._stop_event.clear()
            self._thread = Thread(target=self._run_timer, daemon=True)
            self._thread.start()
            self._notify_state_change()
    
    def pause(self):
        """Pausa o timer"""
        if self._state == TimerState.RUNNING:
            self._state = TimerState.PAUSED
            self._stop_event.set()
            self._notify_state_change()
    
    def reset(self):
        """Reseta o timer para o tempo inicial"""
        self._state = TimerState.STOPPED
        self._stop_event.set()
        
        if self._mode == TimerMode.COUNTDOWN:
            self._current_time = self._initial_hours * 3600 + self._initial_minutes * 60 + self._initial_seconds
        else:
            self._current_time = 0
        
        self._notify_update()
        self._notify_state_change()
    
    def _run_timer(self):
        """Thread principal do timer"""
        while not self._stop_event.is_set():
            if self._mode == TimerMode.COUNTDOWN:
                if self._current_time <= 0:
                    self._state = TimerState.STOPPED
                    self._notify_state_change()
                    break
                self._current_time -= 1
            else:  # STOPWATCH
                self._current_time += 1
            
            self._notify_update()
            time.sleep(1)
    
    def _notify_update(self):
        """Notifica a UI sobre atualização do tempo"""
        if self._update_callback:
            time_str = self.format_time()
            self._update_callback(time_str)
    
    def _notify_state_change(self):
        """Notifica a UI sobre mudança de estado"""
        if self._state_callback:
            self._state_callback(self._state)
    
    def format_time(self) -> str:
        """Formata o tempo atual como string"""
        hours = self._current_time // 3600
        minutes = (self._current_time % 3600) // 60
        seconds = self._current_time % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    def get_current_seconds(self) -> int:
        """Retorna o tempo atual em segundos"""
        return self._current_time
