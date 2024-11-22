import hashlib
import time
import json

class Blockchain:
    def __init__(self, difficulty=4):
        self.chain = []
        self.difficulty = difficulty  # Difficulty level of the Proof of Work puzzle
        self.create_genesis_block()

    def create_genesis_block(self):
        """Create the genesis block (first block)."""
        genesis_block = Block(0, '0', time.time(), {}, 0)
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)

    def add_block(self, new_block):
        """Add a new block to the blockchain after solving the Proof of Work puzzle."""
        # Set the previous hash and index before mining
        previous_block = self.chain[-1]
        new_block.previous_hash = previous_block.hash
        new_block.index = previous_block.index + 1

        # Proof of Work (mining) step
        new_block.mine_block(self.difficulty)
        
        # Validate the block before adding it to the chain
        if self.is_valid_new_block(new_block):
            self.chain.append(new_block)
        else:
            print(f"Invalid block at index {new_block.index}, rejecting...")

    def is_valid_new_block(self, new_block):
        """Validate the new block against the current blockchain."""
        previous_block = self.chain[-1]

        # 1. Check if the block's previous hash matches the last block in the chain
        if new_block.previous_hash != previous_block.hash:
            print("Previous hash doesn't match.")
            return False
        
        # 2. Check if the block hash meets the Proof of Work requirement (difficulty)
        if new_block.hash[:self.difficulty] != '0' * self.difficulty:
            print("Proof of Work failed.")
            return False

        # 3. Check if the hash is correct
        if new_block.hash != new_block.calculate_hash():
            print("Hash calculation is incorrect.")
            return False

        # If all checks pass, return True
        return True

    def display_chain(self):
        """Display the blockchain."""
        for block in self.chain:
            print(f"Block {block.index}:")
            print(f"Data: {block.data}")
            print(f"Trust Score: {block.trust_score}")
            print(f"Hash: {block.hash}")
            print(f"Previous Hash: {block.previous_hash}")
            print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(block.timestamp))}\n")


class Block:
    def __init__(self, index, previous_hash, timestamp, data, trust_score):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data  # This will now hold trust ratings data
        self.trust_score = trust_score  # Add trust score to the block
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """Calculate the hash of the block."""
        block_contents = (
            str(self.index),
            self.previous_hash,
            str(self.timestamp),
            json.dumps(self.data, sort_keys=True),
            str(self.trust_score),
            str(self.nonce)
        )
        value = ''.join(block_contents).encode()
        return hashlib.sha256(value).hexdigest()

    def mine_block(self, difficulty):
        """Mine the block using Proof of Work."""
        target = '0' * difficulty  # Target string (e.g., '0000' for difficulty=4)

        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()  # Recalculate hash with new nonce
        
        print(f"Block mined with nonce value: {self.nonce}")
