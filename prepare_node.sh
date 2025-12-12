#!/bin/bash
# Salve como: prepare_node.sh
# RODE NOS NOTEBOOKS: bash prepare_node.sh

set -e

echo ">>> [1/3] Atualizando e instalando Python Venv..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv

echo ">>> [2/3] Liberando porta de Auditoria (18861)..."
sudo ufw allow 18861/tcp

echo ">>> [3/3] Criando Venv e instalando libs..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
else
    echo "   Venv já existia."
fi

./venv/bin/pip install --upgrade pip
./venv/bin/pip install pika rpyc

# Cria o atalho para rodar
cat <<EOT > rodar_banco.sh
#!/bin/bash
if [ -z "\$1" ] || [ -z "\$2" ]; then
    echo "Uso: ./rodar_banco.sh <NOME_DO_NO> <IP_DO_SERVIDOR>"
    exit 1
fi
echo "Iniciando Banco (\$1) conectando em \$2..."
./venv/bin/python3 banco_node.py \$1 \$2
EOT
chmod +x rodar_banco.sh

echo ""
echo "========================================================"
echo " NOTEBOOK PRONTO!"
echo " Para usar, digite: ./rodar_banco.sh NOME IP_DO_DESKTOP"
echo "========================================================"
