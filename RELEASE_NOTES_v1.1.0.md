# Timer Segunda Tela — v1.1.0

Timer desktop para segunda tela com janela de exibição configurável e janela de controle completa.

---

## Novidades

### Atalhos de teclado

| Atalho | Ação |
|---|---|
| `H` | Foca o campo de **hora** |
| `M` | Foca o campo de **minuto** |
| `S` | Foca o campo de **segundo** |
| `Espaço` | Inicia o timer se parado/pausado; pausa se estiver contando |
| `Ctrl+I` | Iniciar |
| `Ctrl+R` | Resetar |
| `Ctrl+F` | Abrir formatação |
| `Ctrl+P` | Projetar/Ocultar janela do timer |
| `Ctrl+C` | Carregar preset |
| `Ctrl+Shift+S` | Salvar preset |
| `Ctrl+Shift+↓` | Centralizar janela do timer no inferior direito da tela |

### Access Keys (estilo menu do Windows)

Pressione `Alt` uma vez para ativar o modo — os botões exibem a letra sublinhada correspondente. Pressione a letra para executar o comando. Pressione `Alt` ou `Escape` para cancelar.

| Alt, então... | Ação |
|---|---|
| `I` | **I**niciar |
| `P` | **P**ausar |
| `R` | **R**esetar |
| `F` | **F**ormatar |
| `O` | Projetar/**O**cultar |
| `D` | Centralizar Inferior **D**ireito |
| `S` | **S**alvar Preset |
| `C` | **C**arregar Preset |

---

## Correções

- **Tamanho de fonte preservado ao ajustar posição** — ativar "Ajustar posição e tamanho" não altera mais o tamanho da fonte definido pelo usuário; o ajuste automático por proporção só ocorre ao redimensionar manualmente pelas bordas.
- **Modal de preset sem duplicação** — abrir "Carregar Preset" enquanto o modal já está aberto passa o foco para a janela existente em vez de abrir uma segunda.
- **Escape fecha o modal de preset** — o modal de carregamento responde ao `Escape` imediatamente ao abrir.
