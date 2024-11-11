import time

from utils import Blockchain

def analyse_performance(blockchain: Blockchain):
    start_mine = time.time()
    blockchain.mine_pending_transactions()
    end_mine = time.time()

    start_valid = time.time()
    is_valid = blockchain.is_chain_valid()
    end_valid = time.time()

    print(f"Time to mine block: {end_mine - start_mine}")
    print(f"Time to validate chain: {end_valid - start_valid}")
    print(f"Chain is valid: {is_valid}")