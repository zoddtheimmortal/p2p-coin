import json
import socket
import threading
import time
from typing import Dict
from utils import Block, Blockchain


class Node:
    def __init__(self,blockchain:Blockchain,host='localhost',port=8080):
        self.blockchain = blockchain
        self.peers = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()

    def broadcast(self, data:Dict, message_type:str):

        for peer in self.peers:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(peer)
                s.sendall(json.dumps(data).encode())
                

    def handle_peer_connection(self,conn,addr):
        with conn:
            print(f'Connected by {addr}')
            data = conn.recv(1024)
            if data:
                message = json.loads(data.decode())

                received_time = time.time()
                sent_time = message.get('timestamp',received_time)
                latency = received_time - sent_time
                print(f'Latency: {latency:.6f} secs for {message} from {addr}')

                if message['type'] == 'transaction':
                    self.blockchain.add_transaction(message['data'])
                elif message['type']=='block':
                    new_block = Block(index=message['data']['index'],transactions=message['data']['transactions'],previous_hash=message['data']['previous_hash'],hash=message['data']['hash'],nonce=message['data']['nonce'])
                    self.blockchain.add_block(new_block)
                    print(f'Added block {new_block.hash} from {addr}')

    def listen(self):
        print("Starting server")
        while True:
            conn, addr = self.server.accept()
            threading.Thread(target=self.handle_peer_connection, args=(conn, addr)).start() 