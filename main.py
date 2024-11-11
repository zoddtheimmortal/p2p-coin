
import threading
from network import Node
from performance import analyse_performance
from utils import Blockchain


def main():
    blockchain = Blockchain()
    host = 'localhost'
    port = int(input("Enter port number: "))

    node = Node(blockchain,host,port)

    while True:
        peer_ip = 'localhost'
        peer_port = int(input("Enter peer port or -1 to quit: "))

        if (peer_port == -1):
            break

        if (peer_ip, peer_port) not in node.peers:
            node.peers.append((peer_ip, peer_port))
        else:
            print("Peer already exists.")

    threading.Thread(target=node.listen, daemon=True).start()

    print(f"Node started at {host}:{port}, waiting for input")

    while True:
        action = input("\nOptions:\n - 't': Add a transaction\n - 'm': Mine a new block\n"
                       " - 'v': View the blockchain\n - 'b': Broadcast last mined block\n"
                       " - 'l': Show current latency stats\n - 'q': Quit\nChoose an option: ")
        
        if action == 't':
            transaction = input("Enter transaction data: ")
            blockchain.add_transaction(transaction)
            node.broadcast({"data": transaction,"type":'transaction'}, "transaction")
            print("Transaction added and broadcasted.")

        elif action == 'm':
            blockchain.mine_pending_transactions()
            new_block = blockchain.get_latest_block()
            message = {"type": "block", "data": new_block.__dict__}
            node.broadcast(message, "block")
            print(f"Block mined and broadcasted: {new_block.hash}")

        elif action == 'v':
            for block in blockchain.chain:
                print(f"Block {block.index} [{block.hash}]: {block.transactions}")
        
        elif action == 'b':
            if len(blockchain.chain) > 1:
                last_block = blockchain.get_latest_block()
                node.broadcast(last_block.__dict__, "block")
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