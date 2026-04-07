# Solução: Executar CULTURA EM PESO BATTLE no Pop!_OS com NTFS

## Problema

AppImage não executa no Pop!_OS com discos NTFS porque:

1. **NTFS não permite bit de execução** (execute bit)
2. **Permissões de escrita limitadas** 
3. **Arquivo JSON não consegue ser salvo**

---

## Solução

### ✅ OPÇÃO 1: Instalar em EXT4 (RECOMENDADO)

Copie o AppImage para a partição home (EXT4) do seu sistema:

```bash
cd ~
mkdir -p ~/aplicativos
cp /caminho/do/CULTURA_EM_PESO_BATTLE.AppImage ~/aplicativos/
chmod +x ~/aplicativos/CULTURA_EM_PESO_BATTLE.AppImage
```

**Agora com duplo-clique:**
- Abra gerenciador de arquivos
- Navegue para `~/aplicativos/`
- Double-click em `CULTURA_EM_PESO_BATTLE.AppImage`
- ✅ Pronto!

---

### 📋 OPÇÃO 2: Montar disco NTFS com permissões corretas

Se seus arquivos estão no disco NTFS, monte-o com permissões de execução:

```bash
# Desmontar (se já está montado)
sudo umount /ponto/de/montagem

# Criar ponto de montagem
sudo mkdir -p /mnt/dados_ntfs

# Montar com permissões corretas
sudo mount -t ntfs-3g -o uid=1000,gid=1000,fmask=0133,dmask=0022 /dev/sdXN /mnt/dados_ntfs
```

⚠️ **Substitua `/dev/sdXN`** pela sua partição NTFS.  
Para descobrir: execute `lsblk`

Depois:
```bash
chmod +x /mnt/dados_ntfs/CULTURA_EM_PESO_BATTLE.AppImage
/mnt/dados_ntfs/CULTURA_EM_PESO_BATTLE.AppImage
```

---

### 🐍 OPÇÃO 3: Executar via Python3 (sem AppImage)

Se não conseguir fazer funcionar o AppImage:

```bash
cd ~/Downloads/calc/copa_cep  # (Ou aonde você baixou)
python3 main.py
```

**Vantagem:** Dados salvam em `~/.cultura_em_peso/` (permissões EXT4 garantidas)

---

## 🔒 Permissões NTFS Pop!_OS - Detalhes

```
uid=1000          = seu usuário padrão
gid=1000          = seu grupo padrão
fmask=0133        = remove execute (x) para arquivos
dmask=0022        = garante write (w) para diretórios
```

---

## 🔧 FIXAR Montagem Automática (opcional)

Para montar o NTFS automaticamente com essas permissões:

```bash
sudo nano /etc/fstab
```

Adicione a linha:
```
/dev/sdXN /mnt/dados_ntfs ntfs-3g uid=1000,gid=1000,fmask=0133,dmask=0022 0 0
```

Salvar: **Ctrl+O**, Enter, **Ctrl+X**

---

## ✅ Verificar se funcionou

### Teste 1: Bit de execução
```bash
touch /mnt/dados_ntfs/teste.txt
ls -la /mnt/dados_ntfs/teste.txt
# Deve mostrar: -rw-r--r-- (SEM x)
```

### Teste 2: Permissões de escrita JSON
```bash
python3 << 'EOF'
import json, os

test_file = os.path.expanduser("~/.cultura_em_peso/test.json")
os.makedirs(os.path.dirname(test_file), exist_ok=True)

with open(test_file, "w") as f:
    json.dump({"test": "ok"}, f)

print("✅ Permissões de escrita OK!")
EOF
```

---

## 📦 Resumo das Correções Implementadas

O código foi corrigido para:

1. **Usar `sys._MEIPASS`** - Encontra assets corretos em PyInstaller --onefile
2. **Salvar JSON em `~/.cultura_em_peso/`** - Evita problemas de permissão NTFS
3. **Tratamento robusto de erro** - Mensagens claras se algo falhar
4. **AppImage com bit de execução** - Pronto para duplo-clique

---

## 🚀 Resumo

| Método | Setup | Duplo-clique | Dados | Melhor para |
|--------|--------|--------------|-------|-----------|
| **EXT4** | Copiar | ✅ Sim | Automático | Máxima compatibilidade |
| **NTFS montado** | Montar | ✅ Sim | Automático | NTFS com perms corretas |
| **Python direto** | Nada | ❌ Não | ~/.cultura_em_peso | Máxima compatibilidade |

