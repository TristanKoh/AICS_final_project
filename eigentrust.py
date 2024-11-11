import random
import numpy as np

class Peer:
    def __init__(self, name):
        self.name = name
        self.trust_ratings = {}  # Trust ratings for other peers
        self.rating_bias = random.uniform(0.7, 1.5)  # Peer-specific rating bias (random)

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


class EigenTrust:
    def __init__(self, peers):
        self.peers = peers
        self.trust_matrix = np.zeros((len(peers), len(peers)))
        self.trust_scores = np.ones((len(peers), 1)) / len(peers)  # Initialize trust scores


    def build_trust_matrix(self):
        """Build the trust matrix based on peer ratings."""
        peer_index = {peer.name: index for index, peer in enumerate(self.peers)}

        # Fill the trust matrix with ratings
        for i, peer in enumerate(self.peers):
            ratings = peer.get_ratings()
            for rated_peer_name, ratings_list in ratings.items():
                j = peer_index[rated_peer_name]  # Find the index of the rated peer
                avg_rating = sum(ratings_list) / len(ratings_list)  # Average rating for this peer
                self.trust_matrix[i, j] = avg_rating

    def normalize_trust_matrix(self):
        """Normalize the trust matrix so that each column sums to 1."""
        # Apply max(s_ij, 0) to ensure non-negative trust values
        self.trust_matrix = np.maximum(self.trust_matrix, 0)

        column_sums = self.trust_matrix.sum(axis=0, keepdims=True)
        
        # Avoid division by zero
        column_sums[column_sums == 0] = 1  # Prevent division by zero in normalization
        
        # Normalize each column
        self.trust_matrix = self.trust_matrix / column_sums  # Normalize each column


    def calculate_trust_scores(self, max_iterations=40, epsilon=1e-30):
        """Calculate the global trust scores using the EigenTrust algorithm."""
        for i in range(max_iterations):
            # Update trust scores based on the current trust matrix
            new_trust_scores = self.trust_matrix.dot(self.trust_scores)
                        
            # Check for convergence (when trust scores stop changing)
            if np.linalg.norm(new_trust_scores - self.trust_scores) < epsilon:
                break

            self.trust_scores = new_trust_scores

        return self.trust_scores

    def display_trust_scores(self):
        """Display the final trust scores for each peer."""
        for i, peer in enumerate(self.peers):
            print(f"{peer.name}: {self.trust_scores[i, 0]:.4f}")