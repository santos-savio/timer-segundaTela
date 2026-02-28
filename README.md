# Timer Desktop App para Segunda Tela

Aplicativo desktop em Python com interface gráfica para exibir um timer em janela independente, ideal para ser mostrado em segunda tela ou projetor.

## Características

- **Interface dupla**: Janela de controle e janela de exibição independente
- **Modos de timer**: Crescente (cronômetro) e Decrescente (contagem regressiva)
- **Personalização completa**: Cores, fontes e tamanhos ajustáveis
- **Modal de formatação**: Interface amigável para personalização com preview em tempo real
- **Janela borderless**: Exibição limpa ideal para projeção
- **Controle de posição**: Opção de travar/destravar movimentação e redimensionamento
- **Always on top**: Janela de exibição permanece acima das outras quando travada

## Instalação e Uso

### Opção 1: Versão Compilada (Recomendado)

1. Acesse a página de releases: https://github.com/santos-savio/timer-segundaTela/releases
2. Baixe o arquivo executável mais recente (`.exe` para Windows)
3. Execute o arquivo baixado - não é necessário instalar Python

### Opção 2: Código Fonte

1. Clone ou baixe os arquivos do projeto
2. Navegue até o diretório do projeto
3. Execute o aplicativo:

```bash
python main.py
```

### Requisitos (Apenas para código fonte)

- Python 3.x
- Tkinter (incluído por padrão na instalação Python)

## Uso

### Janela de Controle

- **Preview**: Visualização em tempo real do timer
- **Tempo Inicial**: Configure horas, minutos e segundos
- **Modo**: Escolha entre Crescente ou Decrescente
- **Botões de Controle**:
  - Iniciar/Continuar: Inicia ou continua o timer
  - Pausar: Pausa a contagem
  - Resetar: Volta ao tempo inicial e para o timer
  - Formatar: Abre modal de personalização

### Modal de Formatação

- **Cores**: Escolha cor de fundo e do texto
- **Fonte**: Selecione família e tamanho da fonte
- **Preview**: Visualização em tempo real das alterações
- **Botões**:
  - Aplicar: Aplica as alterações e fecha o modal
  - Descartar: Fecha sem aplicar alterações
  - Padrão: Restaura configuração padrão (fundo preto, texto branco, Arial 120pt)

### Opções

- **Projetar/Ocultar**: Mostra ou esconde a janela do timer
- **Ajustar posição e tamanho**: Permite mover e redimensionar a janela do timer
- **Centralizar Inferior Direito**: Posiciona a janela no canto inferior direito da tela

### Presets

- **Salvar Preset**: Salva as configurações atuais (tempo, modo, formatação, posição e tamanho)
- **Carregar Preset**: Carrega um preset previamente salvo
- **Atalhos**: 
  - `Ctrl+S`: Salvar preset
  - `Ctrl+C`: Carregar preset

### Atalhos de Teclado

- **H**: Focar campo de horas
- **M**: Focar campo de minutos  
- **S**: Focar campo de segundos
- **Espaço**: Iniciar/Pausar timer
- **Ctrl+I**: Iniciar timer
- **Ctrl+R**: Resetar timer
- **Ctrl+F**: Abrir formatação
- **Ctrl+P**: Projetar/Ocultar
- **Ctrl+S**: Salvar preset
- **Ctrl+C**: Carregar preset
- **Ctrl+Shift+Seta Baixo**: Centralizar inferior direito
- **Alt + tecla**: Modo de acesso rápido (pressione Alt e solte, depois digite a tecla de acesso)

### Janela do Timer

- **Exibição borderless**: Sem barra de título ou bordas
- **Formato de tempo**: HH:MM:SS ou MM:SS dependendo do tempo
- **Always on top**: Permanece acima das outras janelas quando travada
- **Redimensionável**: Ajuste automático da fonte ao redimensionar

## Estrutura do Projeto

```
timer-segundaTela/
├── main.py              # Ponto de entrada da aplicação
├── timer_logic.py       # Lógica do timer (contagem, estados)
├── timer_window.py      # Janela de exibição do timer
├── control_window.py    # Janela de controle principal
├── format_modal.py      # Modal de formatação
├── requirements.txt     # Dependências
└── README.md           # Este arquivo
```

## Licença

Este projeto é código livre e pode ser modificado e distribuído conforme necessário.

## Suporte

Para problemas ou sugestões, verifique os arquivos do projeto ou consulte a documentação interna do código.
