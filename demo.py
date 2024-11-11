import eigentrust as et
import blockchain as bc
import time

# Example usage 
# Create peers
N = 10  # Number of peers and blocks

# Create N peers
peers = [et.Peer(f"Peer {i+1}") for i in range(N)]

# Peers rate each other with biased ratings (randomly)
for i in range(N):
    for j in range(N):
        if i != j:
            rating = peers[i].biased_rating()
            peers[i].rate_peer(peers[j], rating)

# Initialize Blockchain and EigenTrust
blockchain = bc.Blockchain()
eigentrust = et.EigenTrust(peers)

# Build the trust matrix and normalize
eigentrust.build_trust_matrix()
eigentrust.normalize_trust_matrix()

# Calculate and display trust scores
eigentrust.calculate_trust_scores()

# Adding N blocks with trust ratings as block data
for i in range(N):
    trust_ratings = peers[i].get_ratings()  # Get the ratings from the peer
    trust_score = eigentrust.trust_scores[i, 0]  # Get the calculated trust score for the peer
    blockchain.add_block(bc.Block(i + 1, blockchain.chain[-1].hash, time.time(), trust_ratings, trust_score))

# Display the blockchain
blockchain.display_chain()
