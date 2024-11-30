from scipy.sparse import csr_matrix, diags
import numpy as np
from multiprocessing import Pool, cpu_count

class EigenTrust:
    def __init__(self, peers):
        self.peers = peers
        self.N = len(peers)
        self.trust_matrix = csr_matrix((self.N, self.N), dtype=np.float64)  # Sparse matrix
        self.trust_scores = np.ones((self.N, 1)) / self.N  # Initialize trust scores

    def build_trust_matrix(self):
        """Build the trust matrix using sparse matrix operations in a parallel-safe manner."""
        peer_index = {peer.name: index for index, peer in enumerate(self.peers)}
        
        # Tasks to distribute across processes
        tasks = [(i, peer.get_ratings(), peer_index) for i, peer in enumerate(self.peers)]
        
        # Parallel processing
        with Pool(processes=min(cpu_count(), len(self.peers))) as pool:
            results = pool.map(self._process_peer_ratings, tasks)
        
        # Aggregate results directly into sparse matrix format
        rows, cols, data = [], [], []
        for i, ratings in results:
            for j, avg_rating in ratings.items():
                rows.append(i)
                cols.append(j)
                data.append(avg_rating)
        
        # Create the sparse trust matrix
        self.trust_matrix = csr_matrix((data, (rows, cols)), shape=(self.N, self.N))

    @staticmethod
    def _process_peer_ratings(task):
        """Helper method to process peer ratings."""
        i, ratings, peer_index = task
        processed_ratings = {}
        for rated_peer_name, ratings_list in ratings.items():
            j = peer_index[rated_peer_name]
            avg_rating = sum(ratings_list) / len(ratings_list)
            processed_ratings[j] = avg_rating
        return i, processed_ratings
    
    def normalize_trust_matrix(self):
        """Normalize the trust matrix so that each column sums to 1."""
        self.trust_matrix = self.trust_matrix.maximum(0)
        column_sums = self.trust_matrix.sum(axis=0).A1
        column_sums[column_sums == 0] = 1
        normalization_factors = diags(1 / column_sums)

        self.trust_matrix = self.trust_matrix.dot(normalization_factors)

    def calculate_trust_scores(self, max_iterations=40, epsilon=1e-8):
        """Efficiently calculate global trust scores using sparse matrix operations."""
        for _ in range(max_iterations):
            new_trust_scores = self.trust_matrix.dot(self.trust_scores)
            new_trust_scores /= np.linalg.norm(new_trust_scores, ord=1)

            if np.linalg.norm(new_trust_scores - self.trust_scores, ord=1) < epsilon:
                break

            self.trust_scores = new_trust_scores

        return self.trust_scores

    def display_trust_scores(self):
        """Display the final trust scores for each peer."""
        for i, peer in enumerate(self.peers):
            print(f"{peer.name}: {self.trust_scores[i, 0]:.4f}")
