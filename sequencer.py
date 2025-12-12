#!/usr/bin/env python3
# sequencer.py
import pika
import sys

MQ_HOST = 'localhost'
REQ_QUEUE = 'BANCO_REQ_QUEUE'
ORDERED_QUEUE = 'BANCO_ORDERED_QUEUE'

# Credenciais criadas pelo prepare_desktop.sh
CREDENTIALS = pika.PlainCredentials('sduser', 'sdpass')

def main():
    print(f"[*] Conectando ao RabbitMQ em {MQ_HOST}...")
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=MQ_HOST, credentials=CREDENTIALS)
        )
        channel = connection.channel()
    except Exception as e:
        print(f"ERRO FATAL: Não foi possível conectar ao RabbitMQ.\n{e}")
        return

    channel.queue_declare(queue=REQ_QUEUE)
    channel.queue_declare(queue=ORDERED_QUEUE)

    seq_counter = 0
    print(f"[*] Sequencer PRONTO. Aguardando comandos em '{REQ_QUEUE}'...")

    def callback(ch, method, properties, body):
        nonlocal seq_counter
        msg_original = body.decode()
        
        seq_counter += 1
        msg_ordenada = f"{seq_counter}|{msg_original}"
        
        # Publica na fila 'fanout' (broadcast) seria ideal, mas usando work queues simples
        # aqui todos consomem da mesma fila. Para broadcast real no RabbitMQ
        # o ideal seria Exchange do tipo Fanout, mas vamos manter a estrutura simples
        # que funciona se cada nó tiver sua lógica de leitura ou se usarmos Exchange.
        #
        # CORREÇÃO PARA O TRABALHO: Para garantir que TODOS recebam, 
        # vamos usar uma Exchange do tipo 'fanout' para a volta.
        
        ch.exchange_declare(exchange='banco_fanout', exchange_type='fanout')
        ch.basic_publish(exchange='banco_fanout',
                         routing_key='',
                         body=msg_ordenada)
        
        print(f"[Seq {seq_counter}] Processado: {msg_original}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=REQ_QUEUE, on_message_callback=callback)
    channel.start_consuming()

if __name__ == '__main__':
    if len(sys.argv) > 1: MQ_HOST = sys.argv[1]
    main()
