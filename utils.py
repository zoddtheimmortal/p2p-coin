import json
import time
import hashlib
from typing import List

class Block:
    def __init__(self, index: int, transactions: List[str], previous_hash: str,hash:str=None, nonce: int = 0):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash:str = hash if hash is not None else self.calculate_hash()

    def calculate_hash(self) -> str:
        block_string = f"{self.index}{json.dumps(self.transactions)}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty: int):
        while self.hash[:difficulty] != '0' * difficulty:
            self.nonce += 1
            self.hash = self.calculate_hash()
        print(f"Block mined with nonce {self.nonce}: {self.hash}")

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 4
        self.pending_transactions = []
        self.unbroadcasted_blocks = []

    def create_genesis_block(self) -> Block:
        return Block(index=0, transactions=["Genesis Block"],hash="0",previous_hash="0")

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def add_block(self, new_block: Block):
        for blocks in self.chain:
            if blocks.hash == new_block.hash:
                blocks=new_block
                print("Block already exists in chain. Replaced.")
                self.unbroadcasted_blocks=[]
                return 1
        
        for blocks in self.unbroadcasted_blocks:
            if blocks.hash == new_block.hash:
                print("Block already exists in unbroadcasted blocks. Replaced.")
                new_block.previous_hash = self.get_latest_block().hash
                self.chain.append(new_block)
                self.unbroadcasted_blocks=[]
                return 1

        if new_block.previous_hash != self.get_latest_block().hash:
            print("Invalid block. Previous hash doesn't match.")
            return -1
        
        for blocks in self.unbroadcasted_blocks:
            ghost_txn=[]
            for t2 in new_block.transactions:
                if t2 in blocks.transactions:
                    if t2 not in ghost_txn:
                        ghost_txn.append(t2)
                        blocks.transactions.remove(t2)

            if len(ghost_txn)>0:
                print(f"Ghost transactions found: {ghost_txn}")
                for t in ghost_txn:
                    self.add_transaction(t)
                self.unbroadcasted_blocks.remove(blocks)

        for t2 in new_block.transactions:
            if t2 in self.pending_transactions:
                print(f"Transaction {t2} already exists in pending transactions. Removed.")
                self.pending_transactions.remove(t2)

        new_block.previous_hash = self.get_latest_block().hash
        self.chain.append(new_block)
        return 1

    def add_transaction(self, transaction: str):
        self.pending_transactions.append(transaction)

    def mine_pending_transactions(self):
        if self.pending_transactions:
            new_block = Block(len(self.chain), self.pending_transactions, self.get_latest_block().hash)
            new_block.mine_block(self.difficulty)
            self.unbroadcasted_blocks.append(new_block)
            self.pending_transactions = []

    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.hash != current_block.calculate_hash():
                print("Current block's hash is invalid.")
                return False
            if current_block.previous_hash != previous_block.hash:
                print("Previous block's hash doesn't match.")
                return False
            
        print("Chain is valid.")
        self.display_chain()
        return True
    
    def display_chain(self):
        print("-"*20)
        for block in self.chain:
            print(f"Block {block.index} [{block.hash}]: {block.transactions}")
        print("-"*20)