#!/bin/bash
# Salve como: prepare_desktop.sh
# RODE NO DESKTOP: bash prepare_desktop.sh

set -e # Para se der erro

echo ">>> [1/5] Atualizando sistema e instalando RabbitMQ..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv rabbitmq-server

echo ">>> [2/5] Configurando Permissões do RabbitMQ..."
sudo systemctl enable rabbitmq-server
sudo systemctl start rabbitmq-server

# Cria usuário 'sduser' com senha 'sdpass' para acesso remoto dos notebooks
# O '|| true' evita erro se o usuário já existir
sudo rabbitmqctl add_user sduser sdpass 2>/dev/null || echo "   (Usuário já existe)"
sudo rabbitmqctl set_user_tags sduser administrator 2>/dev/null || true
sudo rabbitmqctl set_permissions -p / sduser ".*" ".*" ".*" 2>/dev/null || true

echo ">>> [3/5] Liberando Firewall (Portas 5672 e 18861)..."
sudo ufw allow 5672/tcp
sudo ufw allow 18861/tcp
# Se o firewall estiver inativo, não tem problema, o comando avisa.

echo ">>> [4/5] Criando Ambiente Virtual Python (venv)..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "   Venv criado com sucesso."
else
    echo "   Venv já existia."
fi

echo ">>> [5/5] Instalando pika e rpyc dentro do venv..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install pika rpyc

# Cria o atalho para rodar
cat <<EOT > rodar_sequencer.sh
#!/bin/bash
echo "Iniciando Sequencer..."
./venv/bin/python3 sequencer.py
EOT
chmod +x rodar_sequencer.sh

echo ""
echo "========================================================"
echo " DESKTOP PRONTO!"
echo " Para ligar o servidor, digite: ./rodar_sequencer.sh"
echo "========================================================"
