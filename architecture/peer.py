import random
import ecdsa
import hashlib

class Peer:
    def __init__(self, name, dht):
        self.name = name
        self.trust_ratings = {}  # Trust ratings for other peers
        self.rating_bias = random.uniform(0.7, 1.5)  # Peer-specific rating bias (random)
        self.is_verified = False  # Indicates whether the peer is verified
        self.private_key = None  # Private key for signing messages (set later)
        self.public_key = None  # Public key (set during verification)
        self.dht = dht
        self.peer_id = self.generate_peer_id(name)
    
    def generate_peer_id(self, name):
        """Generate a unique ID for the peer based on its name."""
        return int(hashlib.sha256(name.encode('utf-8')).hexdigest(), 16)

    def rate_peer(self, peer, rating):
        """Rate another peer's content."""
        if peer.name not in self.trust_ratings:
            self.trust_ratings[peer.name] = []
        self.trust_ratings[peer.name].append(rating)  # Store ratings given to other peers

    def get_ratings(self):
        """Return the ratings given by this peer."""
        return self.trust_ratings

    def biased_rating(self):
        """Generate a biased trust rating, skewed by the peer's rating bias."""
        base_rating = random.randint(1, 10)
        adjusted_rating = base_rating * self.rating_bias  # Adjust by bias
        # Ensure adjusted rating stays within 1-10
        return min(max(int(adjusted_rating), 1), 10)

    def generate_key_pair(self):
        """Generate a public and private key pair for the peer."""
        self.private_key = ecdsa.SigningKey.generate(curve=ecdsa.NIST384p)
        self.public_key = self.private_key.get_verifying_key()

    def sign_message(self, message):
        """Sign a message using the peer's private key."""
        if not self.private_key:
            raise Exception("Private key is not set for signing.")
        return self.private_key.sign(message.encode())  # Sign the message

    def verify_signature(self, message, signature):
        """Verify the message's signature using the peer's public key."""
        if not self.public_key:
            raise Exception("Public key is not set for verification.")
        try:
            self.public_key.verify(signature, message.encode())  # Verify the message signature
            return True
        except ecdsa.BadSignatureError:
            return False
    
    def store_data_in_dht(self, key, value):
        """Store data in the DHT under the peer's ID."""
        self.dht.insert_data(self.peer_id, key, value)

    def retrieve_data_from_dht(self, key):
        """Retrieve data from the DHT."""
        return self.dht.search_data(self.peer_id, key)

class DHT:
    def __init__(self):
        self.data_store = {}  # Main data store to hold key-value pairs
    
    def insert_data(self, peer_id, key, value):
        """Insert data into the DHT at the appropriate location (based on key)."""
        hashed_key = self.hash_key(key)
        
        # Check if the key already exists in the DHT
        if hashed_key in self.data_store:
            stored_peer_id, existing_value = self.data_store[hashed_key]
            
            # Prevent duplication: Data is already stored for this key, return or handle conflict
            if stored_peer_id == peer_id:
                print(f"Data for key '{key}' already exists. Skipping insertion.")
            else:
                # Data exists but from a different peer
                print(f"Warning: Key '{key}' already exists with a different peer (Peer {stored_peer_id}).")
                # Optional: You could merge, overwrite, or handle this case differently
                # For example, to overwrite the data or store both values:
                # self.data_store[hashed_key] = (peer_id, value)  # Overwrite with new data
                # Or merge the data if appropriate, depending on your requirements
        else:
            # Store key-value pair if key does not exist
            self.data_store[hashed_key] = (peer_id, value)
            print(f"Data for key '{key}' inserted successfully.")
    
    def search_data(self, peer_id, key):
        """Search for data in the DHT based on the key."""
        hashed_key = self.hash_key(key)
        
        # Simulating a search and retrieval
        if hashed_key in self.data_store:
            stored_peer_id, value = self.data_store[hashed_key]
            if stored_peer_id == peer_id:
                return value
            else:
                return None  # Data found, but not owned by this peer
        else:
            return None  # Key not found

    def hash_key(self, key):
        """Generate a hashed key from the data's key."""
        return int(hashlib.sha256(key.encode('utf-8')).hexdigest(), 16)

    def display_data(self):
        """Display the contents of the DHT."""
        for key, value in self.data_store.items():
            print(f"Key: {key}, Value: {value}")


class PeerManager:
    def __init__(self):
        self.peers = []
        self.public_key_mapping = {}  # Mapping of public keys to peer names

    def register_peer(self, new_peer, message, signature):
        """Register a new peer after verifying its identity."""
        # Check if the peer's signature is valid
        if new_peer.verify_signature(message, signature):
            new_peer.is_verified = True
            self.public_key_mapping[new_peer.name] = new_peer.public_key
            print(f"{new_peer.name} has been verified and registered as a verified peer.")
        else:
            print(f"{new_peer.name} failed verification. They are a non-verified peer.")

    def add_peer(self, peer):
        """Add a peer to the peer list."""
        self.peers.append(peer)
        print(f"Peer {peer.name} added to the network.")