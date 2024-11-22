
import threading
import time
from network import Node
from performance import analyse_performance
from utils import Blockchain


def main():
    blockchain = Blockchain()
    host = 'localhost'
    port = int(input("Enter port number: "))

    node = Node(blockchain,host,port)

    with open('peerlist.bin', 'rb') as f:
        peer_ports = f.read().splitlines()

    for peer_port in peer_ports:
        peer_port = int(peer_port)
        if peer_port != port:
            node.peers.append((host, peer_port))

    threading.Thread(target=node.listen, daemon=True).start()

    print(f"Node started at {host}:{port}, waiting for input")

    mined_block=None
    while True:
        action = input("\nOptions:\n - 't': Add a transaction\n - 'm': Mine a new block\n"
                       " - 'v': View the blockchain\n - 'b': Broadcast last mined block\n"
                       " - 'l': Show current latency stats\n - 'c': Check blockchain validity\n - 'p': Display pending transactions\n - 'q': Quit\nChoose an option: ")
        
        if action == 't':
            _from = input("Enter sender address: ")
            _to = input("Enter receiver address: ")
            _amt = float(input("Enter amount: "))
            transaction=f"{_from}->{_to}::{_amt}::{time.time()}"
            blockchain.add_transaction(transaction)
            node.broadcast({"data": transaction,"type":'transaction',"return_port":port}, "transaction")
            print("Transaction added and broadcasted.")

        elif action == 'm':
            blockchain.mine_pending_transactions()
            if(len(blockchain.unbroadcasted_blocks)<=0):
                print("No blocks to mine.")
                continue
            if(len(blockchain.unbroadcasted_blocks)>1):
                print("Unbroadcasted blocks exist. Broadcast them first.")
                continue
            new_block = blockchain.unbroadcasted_blocks[-1]
            # message = {"type": "block", "data": new_block.__dict__, "return_port": port}
            print(f"Block mined: {new_block.hash}")
            print(f"Press 'b' to broadcast the block to peers.")

        elif action == 'v':
            blockchain.display_chain()
        
        elif action == 'b':
            if len(blockchain.unbroadcasted_blocks) == 1:
                for last_block in blockchain.unbroadcasted_blocks:
                    print(f"Broadcasting last block: {last_block.__dict__}")
                    message = {"type": "block", "data": last_block.__dict__, "return_port": port}
                    node.broadcast(message, "block")
                    print(f"Last block broadcasted: {last_block.hash}")
                    blockchain.unbroadcasted_blocks = []
                    res=blockchain.add_block(last_block)

                    ghost_txn=[]
                    latest_block=blockchain.get_latest_block()
                    if res==-1:
                        for t2 in last_block.transactions:
                            if t2 not in latest_block.transactions:
                                if t2 not in ghost_txn:
                                    ghost_txn.append(t2)

                    if len(ghost_txn)>0:
                        print(f"Ghost transactions found: {ghost_txn}")
                        for t in ghost_txn:
                            blockchain.add_transaction(t)

            else:
                print("No blocks to broadcast.")

        elif action=='p':
            if len(blockchain.pending_transactions)==0:
                print("No pending transactions.")
                continue
            print("Pending transactions:")
            for transaction in blockchain.pending_transactions:
                print(transaction)

        elif action=='c':
            blockchain.is_chain_valid()

        elif action == 'l':
            analyse_performance(blockchain)

        elif action == 'q':
            print("Quitting node.")
            break

        else:
            print("Invalid option.")

if __name__ == '__main__':
    main()