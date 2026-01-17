import pandas as pd
import networkx as nx
from glob import glob
from typing import List

class EdgeHandler:
    def __init__(self, edges_pattern: str = 'edges_part*.csv', batch_size: int = 50):
        self.edges_files = sorted(glob(edges_pattern))
        self.graph = nx.DiGraph()  # Directed for forward/reverse relations
        self.batch_size = batch_size
        self._load_edges_in_batches()

    def _load_edges_in_batches(self):
        for i in range(0, len(self.edges_files), self.batch_size):
            batch_files = self.edges_files[i:i + self.batch_size]
            batch_df = pd.concat([pd.read_csv(f) for f in batch_files], ignore_index=True)
            for _, row in batch_df.iterrows():
                x_id = str(row['x_id'])  # Stringify IDs for consistency (mixed types in data)
                y_id = str(row['y_id'])
                attrs = {
                    'relation': row['relation'],
                    'display_relation': row['display_relation'],
                    'direction': row['direction'],
                    'full_relation': row['full_relation'],
                    'x_type': row['x_type'],
                    'x_name': row['x_name'],
                    'x_source': row['x_source'],
                    'y_type': row['y_type'],
                    'y_name': row['y_name'],
                    'y_source': row['y_source']
                }
                if row['direction'] == 'forward':
                    self.graph.add_edge(x_id, y_id, **attrs)
                elif row['direction'] == 'reverse':
                    self.graph.add_edge(y_id, x_id, **attrs)  # Reverse edge direction

    def get_subgraph(self, node_ids: List[str]) -> nx.DiGraph:
        return self.graph.subgraph([str(nid) for nid in node_ids])

    def search_edges(self, query: str, column: str = 'relation') -> pd.DataFrame:
        # Load all for search (for large sets, consider dask or partial loads)
        all_edges = pd.concat([pd.read_csv(f) for f in self.edges_files], ignore_index=True)
        return all_edges[all_edges[column].str.contains(query, case=False, na=False)]

    def get_ad_relevant_subgraph(self) -> nx.DiGraph:
        # Tailored for AD: Search edges involving AD terms in names or relations
        ad_edges = self.search_edges('alzheimer|dementia|ad|apoE|psen|app|tau|amyloid|neurodeg|expression|upregulated', column='x_name')
        ad_edges = pd.concat([ad_edges, self.search_edges('alzheimer|dementia|ad|apoE|psen|app|tau|amyloid|neurodeg|expression|upregulated', column='y_name')])
        ad_edges = pd.concat([ad_edges, self.search_edges('disease_protein|bioprocess|molfunc', column='relation')])  # AD-relevant relations
        nodes = set(ad_edges['x_id'].astype(str).unique()) | set(ad_edges['y_id'].astype(str).unique())
        return self.get_subgraph(list(nodes))