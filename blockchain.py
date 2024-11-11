import hashlib
import time

class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        """Create the genesis block (first block)."""
        genesis_block = Block(0, '0', time.time(), {}, 0)
        self.chain.append(genesis_block)

    def add_block(self, new_block):
        """Add a new block to the blockchain."""
        previous_block = self.chain[-1]
        new_block.previous_hash = previous_block.hash
        new_block.hash = new_block.calculate_hash()
        self.chain.append(new_block)

    def display_chain(self):
        """Display the blockchain."""
        for block in self.chain:
            print(f"Block {block.index}:")
            print(f"Data: {block.data}")
            print(f"Hash: {block.hash}")
            print(f"Previous Hash: {block.previous_hash}")
            print(f"Timestamp: {block.timestamp}")
            print(f"Trust Score: {block.trust_score}\n")


class Block:
    def __init__(self, index, previous_hash, timestamp, data, trust_score):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data  # This will now hold trust ratings data
        self.trust_score = trust_score  # Add trust score to the block
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """Calculate the hash of the block."""
        value = f"{self.index}{self.previous_hash}{self.timestamp}{self.data}{self.trust_score}".encode()
        return hashlib.sha256(value).hexdigest()