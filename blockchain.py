import hashlib
import time
import random
import numpy as np

class Block:
    def __init__(self, index, previous_hash, timestamp, data):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        value = f"{self.index}{self.previous_hash}{self.timestamp}{self.data}".encode()
        return hashlib.sha256(value).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_block(data="Genesis Block", previous_hash='0')  # Create the genesis block

    def create_block(self, data, previous_hash):
        index = len(self.chain) + 1
        timestamp = time.time()
        block = Block(index, previous_hash, timestamp, data)
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def print_chain(self):
        for block in self.chain:
            print(f"Block {block.index}:")
            print(f"Hash: {block.hash}")
            print(f"Previous Hash: {block.previous_hash}")
            print(f"Timestamp: {block.timestamp}")
            print(f"Data: {block.data}\n")

class Peer:
    def __init__(self, name, blockchain):
        self.name = name
        self.blockchain = blockchain
        self.trust_ratings = {}  # Trust ratings for other peers
        self.trust_scores = {}  # Final calculated trust scores

    def rate_peer(self, peer, rating):
        """Rate another peer's content."""
        if peer.name not in self.trust_ratings:
            self.trust_ratings[peer.name] = []
        self.trust_ratings[peer.name].append(rating)

        # Create a rating record to add to the blockchain
        data = {
            'peer_rated': peer.name,
            'rating': rating,
            'by_peer': self.name
        }
        self.blockchain.create_block(data, self.blockchain.get_previous_block().hash)



    def calculate_trust_scores(self):
        """Calculate trust scores using the EigenTrust algorithm."""
        peers = list(self.trust_ratings.keys())
        num_peers = len(peers)

        # Initialize trust matrix
        trust_matrix = np.zeros((num_peers, num_peers))

        # Fill trust matrix based on trust ratings

        # TODO: Fix code so that they are not all duplicates. 
        for i, peer_name in enumerate(peers):
            for j, other_peer_name in enumerate(peers):
                # Ensure that peer_name has rated other_peer_name
                if other_peer_name in self.trust_ratings and peer_name in self.trust_ratings[other_peer_name]:
                    trust_matrix[i][j] = self.trust_ratings[other_peer_name][peer_name][-1]  # Get the last rating given
                else:
                    trust_matrix[i][j] = 0  # Default to 0 if no rating exists

        print(trust_matrix)  # Debugging line to check the trust matrix

        # Normalize the trust matrix
        row_sums = trust_matrix.sum(axis=1, keepdims=True)

        # Avoid division by zero: Set row sums of zero to 1
        row_sums[row_sums == 0] = 1  # Prevent division by zero in normalization

        # Normalize each row to sum to 1
        trust_matrix = trust_matrix / row_sums  

        # Initialize trust scores (equal distribution)
        trust_scores = np.ones(num_peers) / num_peers

        # Iteratively compute trust scores until convergence
        for _ in range(10):  # Limit iterations for simplicity
            trust_scores = trust_matrix.dot(trust_scores)

        # Store trust scores
        self.trust_scores = {peers[i]: trust_scores[i] for i in range(num_peers)}



    def show_trust_ratings(self):
        print(f"Trust Ratings for {self.name}:")
        for peer, ratings in self.trust_ratings.items():
            print(f"{peer}: {ratings}")
        print("Calculated Trust Scores:")
        for peer, score in self.trust_scores.items():
            print(f"{peer}: {score:.4f}")



# Create a blockchain
blockchain = Blockchain()

# Create 10 peers
num_peers = 5
peers = [Peer(f"Peer {i + 1}", blockchain) for i in range(num_peers)]

# Peers rate each other
for i in range(num_peers):
    for j in range(num_peers):
        if i != j:  # A peer cannot rate itself
            rating = random.randint(1, 10)
            peers[i].rate_peer(peers[j], rating)

# Calculate trust scores based on ratings
for peer in peers:
    peer.calculate_trust_scores()



# Show trust ratings before calculating trust scores
print("Trust Ratings before calculation:")
for peer in peers:
    peer.show_trust_ratings()

# Show calculated trust scores
print("\nCalculated Trust Scores:")
for peer in peers:
    peer.show_trust_ratings()



# Print blockchain
print("\nBlockchain:")
blockchain.print_chain()
