#!/bin/bash
# build.sh - Compile CULTURA EM PESO BATTLE para os 3 SOs

set -e

# Add local Python bin to PATH
export PATH="/home/cremo/.local/bin:$PATH"

OUTDIR="dist"
APPNAME="CULTURA_EM_PESO_BATTLE"

echo "🏗️  BUILD SCRIPT - CULTURA EM PESO BATTLE"
echo "========================================"
echo ""

# 1. Install PyInstaller if needed
echo "1️⃣  Verificando PyInstaller..."
if ! command -v pyinstaller &> /dev/null; then
    echo "   Instalando PyInstaller..."
    pip3 install --quiet pyinstaller 2>/dev/null || {
        echo "❌ Erro ao instalar PyInstaller"
        exit 1
    }
else
    echo "   ✅ PyInstaller encontrado"
fi

# 2. Install Pillow if needed
echo ""
echo "2️⃣  Verificando Pillow..."
pip3 show Pillow &>/dev/null || {
    echo "   Instalando Pillow..."
    pip3 install --quiet Pillow 2>/dev/null || true
}

# 3. Clean previous builds
echo ""
echo "3️⃣  Limpando builds anteriores..."
rm -rf build *.spec __pycache__ .eggs >/dev/null 2>&1 || true

# 4. Build for current OS
echo ""
echo "4️⃣  Gerando executável para este SO..."
echo "   Comando: pyinstaller --onefile --windowed --name \"$APPNAME\" main.py"
echo ""

pyinstaller \
    --onefile \
    --windowed \
    --name "$APPNAME" \
    --add-data "logo.png:." \
    --add-data "tournament_data.json:." \
    --icon=NONE \
    --distpath "$OUTDIR" \
    main.py 2>&1 | grep -v "WARNING" || true

# 5. Check result
if [ -f "$OUTDIR/$APPNAME" ] || [ -f "$OUTDIR/$APPNAME.exe" ] || [ -d "$OUTDIR/$APPNAME.app" ]; then
    echo ""
    echo "✅ Build concluído com sucesso!"
    echo ""
    echo "📦 Arquivos gerados:"
    ls -lh "$OUTDIR/"* 2>/dev/null || ls -lhd "$OUTDIR/"* 2>/dev/null
    echo ""
    echo "🚀 Para executar no Linux/macOS:"
    echo "   ./$OUTDIR/$APPNAME"
    echo ""
    echo "🚀 Para executar no Windows:"
    echo "   .\$OUTDIR\$APPNAME.exe"
else
    echo ""
    echo "❌ Build falhou - nenhum executável gerado"
    exit 1
fi
