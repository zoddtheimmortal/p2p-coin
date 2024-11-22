
import threading
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
                       " - 'l': Show current latency stats\n - 'q': Quit\nChoose an option: ")
        
        if action == 't':
            _from = input("Enter sender address: ")
            _to = input("Enter receiver address: ")
            _amt = float(input("Enter amount: "))
            transaction=f"{_from}->{_to}::{_amt}"
            blockchain.add_transaction(transaction)
            node.broadcast({"data": transaction,"type":'transaction'}, "transaction")
            print("Transaction added and broadcasted.")

        elif action == 'm':
            blockchain.mine_pending_transactions()
            new_block = blockchain.get_latest_block()
            message = {"type": "block", "data": new_block.__dict__}
            print(f"Block mined: {new_block.hash}")
            print(f"Press 'b' to broadcast the block to peers.")

        elif action == 'v':
            for block in blockchain.chain:
                print(f"Block {block.index} [{block.hash}]: {block.transactions}")
        
        elif action == 'b':
            if len(blockchain.chain) > 1:
                last_block = blockchain.get_latest_block()
                message = {"type": "block", "data": last_block.__dict__}
                node.broadcast(message, "block")
                print(f"Last block broadcasted: {last_block.hash}")
            else:
                print("No blocks to broadcast.")

        elif action == 'l':
            analyse_performance(blockchain)

        elif action == 'q':
            print("Quitting node.")
            break

        else:
            print("Invalid option.")

if __name__ == '__main__':
    main()