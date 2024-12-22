import hashlib
import time


def hash(text: str) -> str:
    hashed = hashlib.sha256(text.encode()).hexdigest()
    return hashed


class Block:
    def __init__(self, previous_hash, transactions):
        self.previous_hash = previous_hash
        self.timestamp = time.time()
        self.transactions = transactions
        self.merkle_root = self.calculate_merkle_root(transactions)
        self.hash = self.mine_block()

    def calculate_merkle_root(self, transactions):
        transaction_hashes = [hash(tx) for tx in transactions]
        while len(transaction_hashes) > 1:
            if len(transaction_hashes) % 2 != 0:
                transaction_hashes.append(transaction_hashes[-1])
            transaction_hashes = [
                hash(transaction_hashes[i] + transaction_hashes[i + 1])
                for i in range(0, len(transaction_hashes), 2)
            ]
        return transaction_hashes[0] if transaction_hashes else None

    def mine_block(self):
        nonce = 0
        while True:
            block_contents = f"{self.previous_hash}{self.timestamp}{self.merkle_root}{nonce}"
            block_hash = hash(block_contents)
            if block_hash.startswith("0"):  # Простое условие майнинга
                return block_hash
            nonce += 1


class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block("0", ["Genesis Block"])
        self.chain.append(genesis_block)

    def add_block(self, transactions):
        previous_hash = self.chain[-1].hash
        new_block = Block(previous_hash, transactions)
        self.chain.append(new_block)

    def validate_blockchain(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            if current.previous_hash != previous.hash:
                return False
            if current.hash != hash(
                f"{current.previous_hash}{current.timestamp}{current.merkle_root}{0}"
            ):
                return False
        return True


if __name__ == "__main__":
    blockchain = Blockchain()

    blockchain.add_block(["Alice->Bob: $10", "Bob->Charlie: $20"])
    blockchain.add_block(["Charlie->Dave: $15", "Dave->Eve: $25"])

    for i, block in enumerate(blockchain.chain):
        print(f"Block {i}:")
        print(f"  Previous Hash: {block.previous_hash}")
        print(f"  Timestamp: {block.timestamp}")
        print(f"  Merkle Root: {block.merkle_root}")
        print(f"  Block Hash: {block.hash}")
        print()

    is_valid = blockchain.validate_blockchain()
    print("Blockchain is valid:", is_valid)
