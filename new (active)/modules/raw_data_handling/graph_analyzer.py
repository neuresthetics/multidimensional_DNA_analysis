import networkx as nx
import pandas as pd
from typing import List, Dict, Any, Optional
from node_handler import NodeHandler
from edge_handler import EdgeHandler
import torch  # For potential GNN extensions
from torch_geometric.utils import from_networkx  # If needed for PyTorch Geometric

class GraphAnalyzer:
    def __init__(self, node_handler: NodeHandler, edge_handler: EdgeHandler):
        self.node_handler = node_handler
        self.edge_handler = edge_handler
        self.graph = self.edge_handler.graph  # Reference to the full DiGraph

    def compute_centrality(self, centrality_type: str = 'degree', top_n: int = 10) -> pd.DataFrame:
        """
        Compute network centrality metrics.
        :param centrality_type: Type of centrality ('degree', 'betweenness', 'closeness', 'eigenvector').
        :param top_n: Number of top nodes to return.
        :return: DataFrame with nodes and their centrality scores.
        """
        if centrality_type == 'degree':
            cent = nx.degree_centrality(self.graph)
        elif centrality_type == 'betweenness':
            cent = nx.betweenness_centrality(self.graph)
        elif centrality_type == 'closeness':
            cent = nx.closeness_centrality(self.graph)
        elif centrality_type == 'eigenvector':
            cent = nx.eigenvector_centrality(self.graph, max_iter=1000)
        else:
            raise ValueError("Unsupported centrality type.")
        
        # Sort and get top_n
        sorted_cent = sorted(cent.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        # Enrich with node details
        data = []
        for node_id, score in sorted_cent:
            details = self.node_handler.get_node_by_id(node_id)
            data.append({
                'node_id': node_id,
                'node_name': details.get('node_name', 'Unknown'),
                'node_type': details.get('node_type', 'Unknown'),
                'centrality_score': score
            })
        return pd.DataFrame(data)

    def get_shortest_paths(self, source_id: str, target_id: str) -> List[List[str]]:
        """
        Find all shortest paths between source and target nodes.
        :param source_id: Starting node ID.
        :param target_id: Ending node ID.
        :return: List of paths (each path is a list of node IDs).
        """
        try:
            paths = list(nx.all_shortest_paths(self.graph, source=source_id, target=target_id))
            return paths
        except nx.NetworkXNoPath:
            return []

    def extract_subgraph(self, node_ids: List[str]) -> nx.DiGraph:
        """
        Extract a subgraph for given node IDs.
        :param node_ids: List of node IDs to include.
        :return: Subgraph DiGraph.
        """
        return self.graph.subgraph(node_ids)

    def get_ad_pathways(self, relation_filter: str = 'upregulated|expression') -> pd.DataFrame:
        """
        Extract AD-relevant pathways, filtering edges by relations (e.g., upregulated).
        :param relation_filter: Regex for relations to include.
        :return: DataFrame of filtered edges.
        """
        ad_subgraph = self.edge_handler.get_ad_relevant_subgraph()
        filtered_edges = []
        for u, v, attrs in ad_subgraph.edges(data=True):
            if pd.Series(attrs['relation']).str.contains(relation_filter, case=False, na=False).any():
                u_details = self.node_handler.get_node_by_id(u)
                v_details = self.node_handler.get_node_by_id(v)
                filtered_edges.append({
                    'source_id': u,
                    'source_name': u_details.get('node_name', 'Unknown'),
                    'target_id': v,
                    'target_name': v_details.get('node_name', 'Unknown'),
                    'relation': attrs['relation'],
                    'display_relation': attrs['display_relation']
                })
        return pd.DataFrame(filtered_edges)

    def detect_isomorphisms(self, target_graph: nx.DiGraph) -> Dict[str, Any]:
        """
        Detect graph isomorphisms (structural similarities) to a target graph.
        :param target_graph: Another NetworkX graph to compare against.
        :return: Dict with isomorphism mappings if found.
        """
        gm = nx.isomorphism.GraphMatcher(self.graph, target_graph)
        if gm.is_isomorphic():
            return {'is_isomorphic': True, 'mapping': gm.mapping}
        return {'is_isomorphic': False, 'mapping': None}

    def to_pyg_data(self) -> Optional[Any]:
        """
        Convert the graph to PyTorch Geometric Data object for GNN processing.
        :return: torch_geometric.data.Data or None if import fails.
        """
        try:
            return from_networkx(self.graph)
        except ImportError:
            print("PyTorch Geometric not installed.")
            return None

# Usage Example
if __name__ == "__main__":
    node_h = NodeHandler('nodes.csv')
    edge_h = EdgeHandler('edges_part*.csv', batch_size=50)
    analyzer = GraphAnalyzer(node_h, edge_h)
    
    # Example: Top degree central nodes
    cent_df = analyzer.compute_centrality('degree', top_n=5)
    print(cent_df)
    
    # Example: AD pathways
    ad_paths = analyzer.get_ad_pathways()
    print(ad_paths.head())