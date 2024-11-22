import numpy as np
from scipy.sparse import csr_matrix

class EigenTrust:
    def __init__(self, peers):
        self.peers = peers
        self.N = len(peers)
        # Data structures for sparse matrix
        self.trust_matrix_data = []
        self.trust_matrix_rows = []
        self.trust_matrix_cols = []
        self.trust_scores = np.ones((self.N, 1)) / self.N  # Initialize trust scores

    def build_trust_matrix(self):
        """Build the trust matrix based on peer ratings."""
        peer_index = {peer.name: index for index, peer in enumerate(self.peers)}

        # Collect data for the sparse matrix
        for i, peer in enumerate(self.peers):
            ratings = peer.get_ratings()
            for rated_peer_name, ratings_list in ratings.items():
                j = peer_index[rated_peer_name]  # Find the index of the rated peer
                avg_rating = sum(ratings_list) / len(ratings_list)  # Average rating for this peer
                self.trust_matrix_rows.append(i)
                self.trust_matrix_cols.append(j)
                self.trust_matrix_data.append(avg_rating)

    def normalize_trust_matrix(self):
        """Normalize the trust matrix so that each column sums to 1."""
        # Create the sparse trust matrix
        trust_matrix = csr_matrix(
            (self.trust_matrix_data, (self.trust_matrix_rows, self.trust_matrix_cols)),
            shape=(self.N, self.N)
        )

        # Apply max(s_ij, 0) to ensure non-negative trust values
        trust_matrix.data = np.maximum(trust_matrix.data, 0)

        # Compute column sums
        column_sums = np.array(trust_matrix.sum(axis=0)).flatten()

        # Avoid division by zero
        column_sums[column_sums == 0] = 1  # Prevent division by zero in normalization

        # Normalize each column
        _, col_indices = trust_matrix.nonzero()
        trust_matrix.data /= column_sums[col_indices]

        self.trust_matrix = trust_matrix

    def calculate_trust_scores(self, max_iterations=40, epsilon=1e-8):
        """Calculate the global trust scores using the EigenTrust algorithm."""
        trust_scores = self.trust_scores.copy()

        for _ in range(max_iterations):
            # Update trust scores based on the current trust matrix
            new_trust_scores = self.trust_matrix.dot(trust_scores)
                            
            # Check for convergence (when trust scores stop changing)
            if np.max(np.abs(new_trust_scores - trust_scores)) < epsilon:
                break

            trust_scores = new_trust_scores

        self.trust_scores = trust_scores

        return self.trust_scores

    def display_trust_scores(self):
        """Display the final trust scores for each peer."""
        for i, peer in enumerate(self.peers):
            print(f"{peer.name}: {self.trust_scores[i, 0]:.4f}")
