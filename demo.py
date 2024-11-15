import architecture.eigentrust as et
import architecture.peer as p
import architecture.blockchain as bc
import time

# Example usage 
# Create peers
N = 10  # Number of peers and blocks

## Add peers to network
# Create N peers
peers = [p.Peer(f"Peer {i+1}") for i in range(N)]

# Generate key pairs for peers
for peer in peers:
    peer.generate_key_pair()

# Register peers with messages and signatures
peer_manager = p.PeerManager()

message = "This is a registration message"

# Simulate registering a verified peer
signature = peers[0].sign_message(message)  # Peer 0 signs the message
peer_manager.register_peer(peers[0], message, signature)

# Simulate registering a non-verified peer (using invalid signature)
signature_invalid = peers[1].sign_message("Fake message")
peer_manager.register_peer(peers[1], message, signature_invalid)

# Add the peers to the network
for peer in peers:
    peer_manager.add_peer(peer)


## Calculate EigenTrust 
# Peers rate each other with biased ratings (randomly)
for i in range(N):
    for j in range(N):
        if i != j:
            rating = peers[i].biased_rating()
            peers[i].rate_peer(peers[j], rating)

# Initialize Blockchain and EigenTrust
blockchain = bc.Blockchain(difficulty = 2)
eigentrust = et.EigenTrust(peers)

# Build the trust matrix and normalize
eigentrust.build_trust_matrix()
eigentrust.normalize_trust_matrix()

# Calculate and display trust scores
eigentrust.calculate_trust_scores()

## Adding N blocks with trust ratings as block data into blockchain
for i in range(N):
    trust_ratings = peers[i].get_ratings()  # Get the ratings from the peer
    trust_score = eigentrust.trust_scores[i, 0]  # Get the calculated trust score for the peer
    new_block = bc.Block(i + 1, blockchain.chain[-1].hash, time.time(), trust_ratings, trust_score)
    
    # Simulate the consensus and adding block
    blockchain.add_block(new_block)

# Display the blockchain
blockchain.display_chain()
