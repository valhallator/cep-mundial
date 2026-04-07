# CULTURA EM PESO BATTLE

Aplicativo de torneio em eliminatória dupla lado-a-lado para até 44 participantes.

## 🚀 Executar

### Opção 1: Direto com Python (Rápido)
```bash
python3 main.py
```

### Opção 2: Executável Compilado (Recomendado para Usuários)
Baixe o executável correspondente ao seu SO em `dist/`:
- **Linux**: `CULTURA_EM_PESO_BATTLE`
- **Windows**: `CULTURA_EM_PESO_BATTLE.exe`
- **macOS**: `CULTURA_EM_PESO_BATTLE`

## 🏗️ Compilar para Seu SO

### Linux/macOS
```bash
bash build.sh
```

Resultado em: `dist/CULTURA_EM_PESO_BATTLE`

### Windows (PowerShell)
```powershell
.\build_windows.ps1
```

Resultado em: `dist\CULTURA_EM_PESO_BATTLE.exe`

### macOS com Suporte Universal
```bash
bash build_macos.sh
```

## ⚙️ Requisitos para Compilar

- Python 3.8 ou superior
- PyInstaller
- Pillow (para logo)

## 📝 Funcionalidades

- ✅ Entrada flexível (16, 22, 32, 44, ou qualquer número)
- ✅ Repescagem automática para números ímpar
- ✅ Bracket lado-a-lado (metade cada lado)
- ✅ Clique para marcar vencedor
- ✅ Logo watermark em fundo (30% transparência)
- ✅ Salvamento automático (JSON)
- ✅ Final com escolha de campeão

## 📊 Estrutura do Torneio

```
LADO ESQUERDA (22 ou Nx2)        LADO DIREITA (22 ou Nx2)
┌───────────────────┐            ┌───────────────────┐
│ 1º RODADA (22→11) │            │ 1º RODADA (22→11) │
├───────────────────┤            ├───────────────────┤
│ 2º RODADA (11→5)  │            │ 2º RODADA (11→5)  │
├───────────────────┤     EQ      ├───────────────────┤
│ 3º RODADA (5→2)   │   ESTRADA  │ 3º RODADA (5→2)   │
├───────────────────┤            ├───────────────────┤
│ SEMIFINAL (2→1)   │            │ SEMIFINAL (2→1)   │
└─────────────┬─────┘            └────┬──────────────┘
              │                        │
              └────────────┬───────────┘
                        FINAL
                    CAMPEÃO ×
```

## 💾 Arquivos

- `main.py` - Aplicação principal
- `tournament_data.json` - Dados do torneio (auto-salvo)
- `logo.png` - Logo Cultura em Peso (watermark)
- `build.sh` - Script para compilar no Linux/macOS
- `build_macos.sh` - Script especial para macOS universal
- `build_windows.ps1` - Script para compilar no Windows

## 🎨 Nome do Aplicativo

- Janela: `CULTURA EM PESO BATTLE`
- Arquivo: `CULTURA_EM_PESO_BATTLE`
- Header: `www.culturaempeso.com | @culturaempeso`
- Tema: Escuro com cores azuis e verdes

## ✅ Status

✅ Desenvolvimento concluído
✅ Testado em Linux
✅ Executável Linux compilado
📋 Scripts Windows e macOS prontos

---

**Version**: 1.0.0
**Date**: 2026-04-07
**Author**: Copilot
