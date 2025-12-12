#!/usr/bin/env python3
# checker.py
import sys
import rpyc

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 checker.py <IP1> <IP2> ...")
        sys.exit(1)

    ips = sys.argv[1:]
    estados = {}
    
    print("=== CONFERÊNCIA DE CONSISTÊNCIA ===")
    for ip in ips:
        try:
            c = rpyc.connect(ip, 18861, config={'allow_public_attrs': True})
            st = c.root.get_estado()
            seq = c.root.get_seq()
            estados[ip] = (seq, st)
            c.close()
            print(f"[{ip}] SEQ: {seq} | DADOS: {st}")
        except:
            print(f"[{ip}] FALHA AO CONECTAR")

    if not estados: return

    # Compara todos com o primeiro
    ref = list(estados.values())[0]
    if all(v == ref for v in estados.values()):
        print("\n[SUCESSO] TODOS OS BANCOS ESTÃO IDÊNTICOS!")
    else:
        print("\n[ERRO] DIVERGÊNCIA ENCONTRADA!")

if __name__ == "__main__": main()
