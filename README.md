# Sistema-Distribuido-Trabalho-final-Parte-III
==============================================================================
TRABALHO DE SISTEMAS DISTRIBUÍDOS
Parte 1: Aplicação Replicada (Banco Distribuído)
Parte 3: Coordenação via Ordenação Total (Sequenciador)
==============================================================================

INTEGRANTES DO GRUPO:
- Boanerges Cipriano Gomes Junior 201702731

==============================================================================
1. ARQUITETURA E LÓGICA DE NEGÓCIO
==============================================================================
O sistema implementa uma "Máquina de Estados Replicada" simulando um ambiente
bancário de consistência forte.

TOPOLOGIA:
- 1 Servidor Central (Desktop): Roda o RabbitMQ e o Sequenciador.
- 3 Clientes (Notebooks): Rodam a aplicação do Banco.

CONCEITO (CAIXAS ELETRÔNICOS):
O sistema simula um ÚNICO BANCO centralizado.
- Os notebooks agem como terminais de autoatendimento (Caixas Eletrônicos).
- Não existem "agências separadas". Todos acessam o mesmo Livro Razão global.
- Se uma conta é criada no Notebook 1, ela existe imediatamente no Notebook 3.
- A consistência é garantida pelo SEQUENCIADOR, que ordena todas as transações
  antes de elas serem processadas pelos nós.

==============================================================================
2. PREPARAÇÃO DO AMBIENTE (LINUX UBUNTU)
==============================================================================
Os scripts .sh inclusos automatizam a criação do ambiente virtual (venv), 
instalação de bibliotecas (pika, rpyc) e configuração do firewall.

PASSO A: NO DESKTOP (SERVIDOR)
1. Coloque na pasta: 'prepare_desktop.sh' e 'sequencer.py'.
2. No terminal, execute:
   $ bash prepare_desktop.sh

PASSO B: NOS NOTEBOOKS (CLIENTES)
1. Coloque na pasta: 'prepare_node.sh' e 'banco_node.py'.
2. No terminal, execute:
   $ bash prepare_node.sh

==============================================================================
3. COMO RODAR O SISTEMA
==============================================================================

[PASSO 1] INICIAR O SEQUENCIADOR (No Desktop)
Execute o script gerado automaticamente:
   $ ./rodar_sequencer.sh
   (Saída esperada: "[*] Sequencer PRONTO. Aguardando comandos...")

[PASSO 2] INICIAR OS CAIXAS (Nos 3 Notebooks)
Execute o script passando o nome do caixa e o IP do Desktop.
Exemplo (Assumindo que o IP do Desktop seja 192.168.1.50):

   No Note 1: $ ./rodar_banco.sh CAIXA_01 192.168.1.50
   No Note 2: $ ./rodar_banco.sh CAIXA_02 192.168.1.50
   No Note 3: $ ./rodar_banco.sh CAIXA_03 192.168.1.50

==============================================================================
4. OPERAÇÕES BANCÁRIAS (COMANDOS)
==============================================================================
O banco começa vazio. Contas são abertas automaticamente no primeiro depósito.

A) DEPOSITAR (Adiciona saldo / Cria conta)
   Comando: DEPOSITAR <nome> <valor>
   Exemplo: DEPOSITAR neymar 1000

B) SACAR (Remove saldo)
   Comando: SACAR <nome> <valor>
   Exemplo: SACAR neymar 50

C) TRANSFERIR (Move saldo entre contas)
   Comando: TRANSFERIR <origem> <destino> <valor>
   Exemplo: TRANSFERIR neymar anitta 200

==============================================================================
5. AUDITORIA E PROVA DE CONSISTÊNCIA (CHECKER)
==============================================================================
O script 'checker.py' prova que a Ordenação Total funciona. Ele conecta nos
3 notebooks simultaneamente e compara se os saldos são idênticos.

!!! IMPORTANTE !!!
Para rodar o checker, os programas dos bancos PRECISAM estar rodando.
1. NÃO FECHE a janela dos bancos.
2. Abra um NOVO terminal (nova aba/janela).
3. Execute o checker apontando para os IPs dos notebooks.

Comando:
   $ ./venv/bin/python3 checker.py <IP_NOTE1> <IP_NOTE2> <IP_NOTE3>

Exemplo Real:
   $ ./venv/bin/python3 checker.py 192.168.1.101 192.168.1.102 192.168.1.103

Saída de Sucesso:
   "[SUCESSO] TODOS OS BANCOS ESTÃO IDÊNTICOS!"

==============================================================================
6. SOLUÇÃO DE PROBLEMAS COMUNS (TROUBLESHOOTING)
==============================================================================

ERRO: "FALHA AO CONECTAR" (Connection Refused) no checker.
CAUSA: O firewall do notebook está bloqueando ou o programa do banco fechou.
SOLUÇÃO:
1. Verifique se o banco_node.py está rodando na outra janela.
2. No notebook que deu erro, libere a porta:
   $ sudo ufw allow 18861/tcp

ERRO: Desktop não conecta no RabbitMQ ou "Connection Closed".
CAUSA: Usuário/Senha errados ou IP errado.
SOLUÇÃO:
1. Verifique o IP do Desktop com o comando: $ hostname -I
2. Garanta que rodou o 'prepare_desktop.sh' para criar o usuário 'sduser'.

==============================================================================
