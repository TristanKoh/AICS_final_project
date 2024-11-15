import random
import ecdsa

class Peer:
    def __init__(self, name):
        self.name = name
        self.trust_ratings = {}  # Trust ratings for other peers
        self.rating_bias = random.uniform(0.7, 1.5)  # Peer-specific rating bias (random)
        self.is_verified = False  # Indicates whether the peer is verified
        self.private_key = None  # Private key for signing messages (set later)
        self.public_key = None  # Public key (set during verification)
    
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