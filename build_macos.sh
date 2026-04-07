#!/bin/bash
# build_macos.sh - Build script para macOS
# Execute ESTE SCRIPT em uma máquina macOS com Python 3.8+ instalado

set -e

OUTDIR="dist"
APPNAME="CULTURA_EM_PESO_BATTLE"

echo "🏗️  BUILD PARA MACOS - CULTURA EM PESO BATTLE"
echo "=============================================="
echo ""

# 1. Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado"
    echo "Instale via: brew install python3"
    exit 1
fi

echo "✅ Python encontrado:"
python3 --version

# 2. Install dependencies
echo ""
echo "Instalando dependências..."
python3 -m pip install --upgrade pip
python3 -m pip install pyinstaller Pillow

# 3. Clean previous builds
echo ""
echo "Limpando builds anteriores..."
rm -rf build *.spec __pycache__

# 4. Build
echo ""
echo "Compilando para macOS..."
python3 -m PyInstaller \
    --onefile \
    --windowed \
    --name "$APPNAME" \
    --add-data "logo.png:." \
    --add-data "tournament_data.json:." \
    --target-arch universal2 \
    --distpath "$OUTDIR" \
    main.py

# 5. Check result
echo ""
if [ -f "$OUTDIR/$APPNAME" ] || [ -d "$OUTDIR/$APPNAME.app" ]; then
    echo "✅ Build concluído com sucesso!"
    echo ""
    echo "📦 Arquivos gerados:"
    ls -lhd "$OUTDIR"/* 2>/dev/null
    echo ""
    echo "🚀 Para executar:"
    echo "   open ./$OUTDIR/$APPNAME.app"
    echo ""
    echo "Ou:"
    echo "   ./$OUTDIR/$APPNAME"
else
    echo "❌ Build falhou"
    exit 1
fi
