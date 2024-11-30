import hashlib
import time
from multiprocessing import Process, Manager, cpu_count

class Blockchain:
    def __init__(self, difficulty=4):
        self.chain = []
        self.difficulty = difficulty  # Difficulty level of the Proof of Work puzzle
        self.create_genesis_block()

    def create_genesis_block(self):
        """Create the genesis block (first block)."""
        genesis_block = Block(0, '0', time.time(), {}, 0)
        self.chain.append(genesis_block)

    def add_block(self, new_block, process_queue):
        """Add a new block to the blockchain after parallel mining."""
        mined_block = process_queue.get()  # Retrieve the mined block from the queue
        if self.is_valid_new_block(mined_block):
            self.chain.append(mined_block)
        else:
            print(f"Invalid block from peer {new_block.index}, rejecting...")

    def is_valid_new_block(self, new_block):
        """Validate the new block against the current blockchain."""
        # 1. Check if the block's previous hash matches the last block in the chain
        if new_block.previous_hash != self.chain[-1].hash:
            print("Previous hash doesn't match.")
            return False
        
        # 2. Check if the block hash meets the Proof of Work requirement (difficulty)
        if new_block.hash[:self.difficulty] != '0' * self.difficulty:
            print("Proof of Work failed.")
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
            print(f"Timestamp: {block.timestamp}\n")


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
        value = f"{self.index}{self.previous_hash}{self.timestamp}{self.data}{self.trust_score}{self.nonce}".encode()
        return hashlib.sha256(value).hexdigest()

    def mine_block(self, difficulty, process_queue):
        """Mine the block using Proof of Work in a separate process."""
        target = '0' * difficulty  # Target string (e.g., '0000' for difficulty=4)

        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()

        print(f"Block mined with nonce: {self.nonce}")
        process_queue.put(self)  # Send the mined block to the main process


def mine_in_parallel(blockchain, blocks_to_mine, max_processes=None):
    """
    Mine multiple blocks in parallel and add them sequentially to the blockchain.
    """
    if max_processes is None:
        max_processes = min(cpu_count(), len(blocks_to_mine))  # Limit parallelism to available cores

    with Manager() as manager:
        process_queue = manager.Queue()  # Shared queue for mined blocks
        processes = []

        # Split blocks into batches to avoid overwhelming the system
        for block in blocks_to_mine:
            # Assign the correct previous_hash before mining
            block.previous_hash = blockchain.chain[-1].hash

            # Create a process for mining the block
            process = Process(target=block.mine_block, args=(blockchain.difficulty, process_queue))
            processes.append(process)
            if len(processes) == max_processes:  # Start a batch of processes
                for p in processes:
                    p.start()
                for p in processes:
                    p.join()  # Wait for batch to finish
                processes.clear()  # Reset for the next batch

        # Collect mined blocks and add them to the blockchain sequentially
        while not process_queue.empty():
            mined_block = process_queue.get()

            # Validate and add the block sequentially
            mined_block.previous_hash = blockchain.chain[-1].hash
            if blockchain.is_valid_new_block(mined_block):
                blockchain.chain.append(mined_block)
            else:
                print(f"Invalid block from peer {mined_block.index}, rejecting...")

