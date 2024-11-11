import time
import hashlib
from typing import List

class Block:
    def __init__(self, index: int, transactions: List[str], previous_hash: str, nonce: int = 0):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        block_string = f"{self.index}{self.timestamp}{self.transactions}{self.previous_hash}{self.nonce}"
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

    def create_genesis_block(self) -> Block:
        return Block(0, ["Genesis Block"], "0")

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def add_block(self, new_block: Block):
        new_block.previous_hash = self.get_latest_block().hash
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)

    def add_transaction(self, transaction: str):
        self.pending_transactions.append(transaction)

    def mine_pending_transactions(self):
        if self.pending_transactions:
            new_block = Block(len(self.chain), self.pending_transactions, self.get_latest_block().hash)
            self.add_block(new_block)
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
        return True