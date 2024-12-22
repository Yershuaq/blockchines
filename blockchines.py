import time

# Реализация собственной SHA-256
def sha256_custom(message: str) -> str:
    def rotate_right(x, n):
        return (x >> n) | (x << (32 - n)) & 0xFFFFFFFF

    def sha256_compression(chunk, h_values):
        k = [
            0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4,
            0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe,
            0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f,
            0x4a7484aa, 0x5cb0a9dc, 0x76f988da, 0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
            0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc,
            0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b,
            0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070, 0x19a4c116,
            0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
            0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7,
            0xc67178f2,
        ]

        w = [int.from_bytes(chunk[i:i + 4], 'big') for i in range(0, 64, 4)]
        for i in range(16, 64):
            s0 = rotate_right(w[i - 15], 7) ^ rotate_right(w[i - 15], 18) ^ (w[i - 15] >> 3)
            s1 = rotate_right(w[i - 2], 17) ^ rotate_right(w[i - 2], 19) ^ (w[i - 2] >> 10)
            w.append((w[i - 16] + s0 + w[i - 7] + s1) & 0xFFFFFFFF)

        a, b, c, d, e, f, g, h = h_values

        for i in range(64):
            s1 = rotate_right(e, 6) ^ rotate_right(e, 11) ^ rotate_right(e, 25)
            ch = (e & f) ^ (~e & g)
            temp1 = (h + s1 + ch + k[i] + w[i]) & 0xFFFFFFFF
            s0 = rotate_right(a, 2) ^ rotate_right(a, 13) ^ rotate_right(a, 22)
            maj = (a & b) ^ (a & c) ^ (b & c)
            temp2 = (s0 + maj) & 0xFFFFFFFF

            h = g
            g = f
            f = e
            e = (d + temp1) & 0xFFFFFFFF
            d = c
            c = b
            b = a
            a = (temp1 + temp2) & 0xFFFFFFFF

        return [
            (h_values[0] + a) & 0xFFFFFFFF,
            (h_values[1] + b) & 0xFFFFFFFF,
            (h_values[2] + c) & 0xFFFFFFFF,
            (h_values[3] + d) & 0xFFFFFFFF,
            (h_values[4] + e) & 0xFFFFFFFF,
            (h_values[5] + f) & 0xFFFFFFFF,
            (h_values[6] + g) & 0xFFFFFFFF,
            (h_values[7] + h) & 0xFFFFFFFF,
        ]

    message_bytes = bytearray(message, 'utf-8')
    message_bytes.append(0x80)
    while (len(message_bytes) * 8) % 512 != 448:
        message_bytes.append(0)

    message_bit_length = len(message) * 8
    message_bytes += message_bit_length.to_bytes(8, 'big')

    h_values = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
    ]

    for i in range(0, len(message_bytes), 64):
        chunk = message_bytes[i:i + 64]
        h_values = sha256_compression(chunk, h_values)

    return ''.join(f'{value:08x}' for value in h_values)


# Классы Blockchain, Block, Transaction
class Transaction:
    """Транзакция в блокчейне."""
    def __init__(self, sender: str, receiver: str, amount: float):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount

    def __str__(self):
        return f"{self.sender}->{self.receiver}:{self.amount}"


class Block:
    """Блок в блокчейне."""
    def __init__(self, index: int, transactions: list, previous_hash: str):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.merkle_root = self.calculate_merkle_root()
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        block_content = f"{self.index}{self.timestamp}{self.merkle_root}{self.previous_hash}{self.nonce}"
        return sha256_custom(block_content)

    def calculate_merkle_root(self) -> str:
        transaction_hashes = [sha256_custom(str(tx)) for tx in self.transactions]
        while len(transaction_hashes) > 1:
            if len(transaction_hashes) % 2 == 1:
                transaction_hashes.append(transaction_hashes[-1])
            transaction_hashes = [
                sha256_custom(transaction_hashes[i] + transaction_hashes[i + 1])
                for i in range(0, len(transaction_hashes), 2)
            ]
        return transaction_hashes[0] if transaction_hashes else sha256_custom("")

    def mine_block(self, difficulty: int):
        target = "0" * difficulty
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.calculate_hash()


class Blockchain:
    """Блокчейн."""
    def __init__(self, difficulty: int = 2):
        self.chain = [self.create_genesis_block()]
        self.difficulty = difficulty

    def create_genesis_block(self) -> Block:
        return Block(0, [], "0")

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def add_block(self, transactions: list):
        previous_block = self.get_latest_block()
        new_block = Block(len(self.chain), transactions, previous_block.hash)
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)

    def validate_blockchain(self) -> bool:
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True


# Демонстрация работы
blockchain = Blockchain()

transactions = [
    Transaction("Alice", "Bob", 50),
    Transaction("Bob", "Charlie", 20),
    Transaction("Charlie", "Dave", 15),
    Transaction("Dave", "Eve", 100),
    Transaction("Eve", "Frank", 5),
    Transaction("Frank", "Alice", 30),
    Transaction("Alice", "Charlie", 25),
    Transaction("Charlie", "Eve", 35),
    Transaction("Eve", "Bob", 40),
    Transaction("Bob", "Frank", 10),
]

blockchain.add_block(transactions)

is_valid = blockchain.validate_blockchain()
print(f"Блокчейн валиден: {is_valid}")

for block in blockchain.chain:
    print(f"Блок {block.index}:")
    print(f"  Время: {block.timestamp}")
    print(f"  Хэш: {block.hash}")
    print(f"  Предыдущий хэш: {block.previous_hash}")
    print(f"  Корень дерева Меркла: {block.merkle_root}")
    print(f"  Транзакции: {[str(tx) for tx in block.transactions]}")
