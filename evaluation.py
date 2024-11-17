import architecture.eigentrust as et
import architecture.peer as p
import architecture.blockchain as bc
import time
import pandas as pd

# Example usage 
# Create peers
N = [500, 1000, 5000, 10000]

# Create dictionary for storage of time values
time_vals = {
    "register_and_add" : [],
    "store_data" : [],
    "retrieve_data" : [],
    "peer_trust_rating" : [],
    "calculate_EigenTrust" : [],
    "add_block" : []
}

# Function to calculate normalised time over N peers
def normalize_time_vals(time_vals):    
    # Iterate over each key in the dictionary
    normalized_dict = {}
    for key, values in time_vals.items():
        # Divide each element of the list by the corresponding divisor
        normalized_dict[key] = [
            val / N[i] if i < len(N) else val  # Prevent index out of range
            for i, val in enumerate(values)
        ]
    
    return normalized_dict


for n in N:
####################################################
#### Intitialising P2P network and adding peers ####
####################################################

    ## Add peers to network
    # Initialise DHT
    dht = p.DHT()

    # Create N peers
    peers = [p.Peer(f"Peer {i+1}", dht) for i in range(n)]

    # Generate key pairs for peers
    for peer in peers:
        peer.generate_key_pair()

    # Register peers with messages and signatures
    peer_manager = p.PeerManager()

    message = "This is a registration message"


    # Simulate registering a verified peer
    start = time.time()

    for peer in peers:
        signature = peer.sign_message(message)  # Peer 0 signs the message
        peer_manager.register_peer(peer, message, signature)
        peer_manager.add_peer(peer)

    end = time.time()
    elapsed = end - start
    
    time_vals["register_and_add"].append(elapsed)

    ############################################
    #### Storing and retrieving data via DHT####
    ############################################

    # Generate and store sample data (a short string) for each peer
    start = time.time()

    for i, peer in enumerate(peers):
        sample_data = f"This is Peer {i+1}'s sample data."

        # Store the data in the DHT for each peer
        key = f"peer_{i+1}_data"
        peer.store_data_in_dht(key, sample_data)

    end = time.time()
    elapsed = end - start

    time_vals["store_data"].append(elapsed)

    # Retrieve and display data from the DHT
    start = time.time()

    for i, peer in enumerate(peers):
        key = f"peer_{i+1}_data"
        retrieved_data = peer.retrieve_data_from_dht(key)
        print(f"Data retrieved for {peer.name}: {retrieved_data}")

    end = time.time()
    elapsed = end - start

    time_vals["retrieve_data"].append(elapsed)

    # Display the contents of the DHT
    dht.display_data()

    ##############################################
    #### Calculating EigenTrust for all peers ####
    ##############################################

    ## Calculate EigenTrust 
    # Peers rate each other with biased ratings (randomly)

    start = time.time()
    
    for i in range(n):
        for j in range(n):
            if i != j:
                rating = peers[i].biased_rating()
                peers[i].rate_peer(peers[j], rating)
    
    end = time.time()
    elapsed = end - start

    time_vals["peer_trust_rating"].append(elapsed)

    # Initialize Blockchain and EigenTrust

    # Set at difficulty at 0 for baseline purposes of easiest case
    blockchain = bc.Blockchain(difficulty = 0)
    eigentrust = et.EigenTrust(peers)

    # Build the trust matrix and normalize
    start = time.time()

    eigentrust.build_trust_matrix()
    eigentrust.normalize_trust_matrix()

    # Calculate and display trust scores
    eigentrust.calculate_trust_scores()

    end = time.time()
    elapsed = end - start

    time_vals["calculate_EigenTrust"].append(elapsed)

    ###########################################################
    #### Validating trust scores to be added to blockchain ####
    ###########################################################

    ## Adding N blocks with trust ratings as block data into blockchain
    start = time.time()

    for i in range(n):
        trust_ratings = peers[i].get_ratings()  # Get the ratings from the peer
        trust_score = eigentrust.trust_scores[i, 0]  # Get the calculated trust score for the peer
        new_block = bc.Block(i + 1, blockchain.chain[-1].hash, time.time(), trust_ratings, trust_score)
        
        # Simulate the consensus and adding block
        blockchain.add_block(new_block)
    
    end = time.time()
    elapsed = end - start

    time_vals["add_block"].append(elapsed)

    # Display the blockchain
    # blockchain.display_chain()

print(time_vals)

avg_time_vals = normalize_time_vals(time_vals)


df_time_vals = pd.DataFrame(time_vals)
df_avg_time_vals = pd.DataFrame(avg_time_vals)

df_time_vals["num_peers"] = N
df_avg_time_vals["num_peers"] = N

df_time_vals.to_csv("time_vals.csv", index = False)
df_avg_time_vals.to_csv("avg_time_vals.csv", index = False)
