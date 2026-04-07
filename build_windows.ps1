#!/bin/bash
# build_windows.sh - Build script para Windows
# Execute ESTE SCRIPT em uma máquina Windows com Python 3.8+ instalado

echo "🏗️  BUILD PARA WINDOWS - CULTURA EM PESO BATTLE"
echo "==============================================="
echo ""
echo "❗ INSTRUÇÕES:"
echo "1. Instale Python 3.8+ de https://python.org"
echo "2. Execute este script em PowerShell ou CMD"
echo ""
echo "Instalando dependências..."
python -m pip install --upgrade pip
python -m pip install pyinstaller Pillow
echo ""
echo "Compilando..."
python -m PyInstaller `
    --onefile `
    --windowed `
    --name "CULTURA_EM_PESO_BATTLE" `
    --add-data "logo.png;." `
    --add-data "tournament_data.json;." `
    --distpath "dist" `
    main.py

echo ""
if (Test-Path "dist\CULTURA_EM_PESO_BATTLE.exe") {
    Write-Host "✅ Build concluído com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📦 Arquivo gerado: dist\CULTURA_EM_PESO_BATTLE.exe"
    Write-Host ""
    Write-Host "🚀 Para executar:"
    Write-Host "   .\dist\CULTURA_EM_PESO_BATTLE.exe"
} else {
    Write-Host "❌ Build falhou" -ForegroundColor Red
}
