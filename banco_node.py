#!/usr/bin/env python3
# banco_node.py (VERSÃO FINAL COM SACAR)
import sys
import threading
import pika
import rpyc
from rpyc.utils.server import ThreadedServer

MQ_HOST = 'localhost' 
REQ_QUEUE = 'BANCO_REQ_QUEUE'
EXCHANGE_NAME = 'banco_fanout'
RPC_PORT = 18861

# Estado local
banco_dados = {}
ultimo_seq = 0
lock = threading.Lock()
MEU_NOME = "CLIENTE"

# Credenciais (definidas no script de setup)
CREDENTIALS = pika.PlainCredentials('sduser', 'sdpass')

def executar_transacao(comando):
    """ Processa a lógica do banco de dados """
    partes = comando.split()
    if len(partes) < 2: return "Cmd Inválido"
    
    # Ex: NB1 DEPOSITAR contaA 100
    origem = partes[0]
    op = partes[1].upper()
    
    # LÓGICA DE DEPOSITAR
    if op == "DEPOSITAR" and len(partes) >= 4:
        conta, val = partes[2], float(partes[3])
        banco_dados[conta] = banco_dados.get(conta, 0.0) + val
        return f"Depósito: {conta} +{val}"
    
    # LÓGICA DE SACAR (NOVO!)
    elif op == "SACAR" and len(partes) >= 4:
        conta, val = partes[2], float(partes[3])
        saldo_atual = banco_dados.get(conta, 0.0)
        
        if saldo_atual >= val:
            banco_dados[conta] -= val
            return f"Saque: {conta} -{val}"
        else:
            return f"FALHA Saque: {conta} (Saldo insuficiente: {saldo_atual})"

    # LÓGICA DE TRANSFERIR
    elif op == "TRANSFERIR" and len(partes) >= 5:
        de, para, val = partes[2], partes[3], float(partes[4])
        if banco_dados.get(de, 0.0) >= val:
            banco_dados[de] -= val
            banco_dados[para] = banco_dados.get(para, 0.0) + val
            return f"Transf: {de}->{para} ${val}"
        return f"FALHA Transf: {de} s/ saldo"
        
    return f"Ignorado: {op}"

# --- O RESTO É IGUAL ---

class Auditoria(rpyc.Service):
    def exposed_get_estado(self): return banco_dados
    def exposed_get_seq(self): return ultimo_seq

def start_rpc():
    try: ThreadedTCPServer(Auditoria, port=RPC_PORT).start()
    except: pass

def start_consumer():
    params = pika.ConnectionParameters(host=MQ_HOST, credentials=CREDENTIALS)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='fanout')
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue_name)

    def callback(ch, method, properties, body):
        global ultimo_seq
        try:
            seq_str, comando = body.decode().split('|', 1)
            seq = int(seq_str)
            with lock:
                res = executar_transacao(comando)
                ultimo_seq = seq
            print(f"\n[SEQ {seq}] {res} | Saldo Global: {banco_dados}")
            print(f"{MEU_NOME}> ", end="", flush=True)
        except: pass

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

def main():
    global MEU_NOME, MQ_HOST
    if len(sys.argv) < 3:
        print("Uso: python3 banco_node.py <NOME> <IP_SERVER>")
        sys.exit(1)
    MEU_NOME, MQ_HOST = sys.argv[1], sys.argv[2]

    threading.Thread(target=start_rpc, daemon=True).start()
    threading.Thread(target=start_consumer, daemon=True).start()

    params = pika.ConnectionParameters(host=MQ_HOST, credentials=CREDENTIALS)
    conn_send = pika.BlockingConnection(params)
    ch_send = conn_send.channel()
    ch_send.queue_declare(queue=REQ_QUEUE)

    print(f"=== BANCO {MEU_NOME} CONECTADO A {MQ_HOST} ===")
    print("Comandos: DEPOSITAR conta valor | SACAR conta valor | TRANSFERIR de para valor")
    
    while True:
        try:
            msg = input(f"{MEU_NOME}> ")
            if msg:
                full = f"{MEU_NOME} {msg}"
                ch_send.basic_publish(exchange='', routing_key=REQ_QUEUE, body=full)
        except: break

if __name__ == '__main__': main()
