import pandas as pd
from typing import Dict, Any

class NodeHandler:
    def __init__(self, nodes_file: str = 'nodes.csv'):
        self.nodes_df = pd.read_csv(nodes_file)
        # Dict for index to ID mapping
        self.node_index_to_id = dict(zip(self.nodes_df['node_index'], self.nodes_df['node_id']))
        # Dict for ID to details
        self.node_id_to_details = self.nodes_df.set_index('node_id').to_dict(orient='index')

    def get_node_by_index(self, index: int) -> Dict[str, Any]:
        node_id = self.node_index_to_id.get(index)
        if node_id:
            return self.node_id_to_details.get(node_id, {})
        return {}

    def get_node_by_id(self, node_id: str) -> Dict[str, Any]:
        return self.node_id_to_details.get(node_id, {})

    def search_nodes(self, query: str, column: str = 'node_name') -> pd.DataFrame:
        return self.nodes_df[self.nodes_df[column].str.contains(query, case=False, na=False)]

    def get_ad_relevant_nodes(self) -> pd.DataFrame:
        # Tailored for AD project: Search for Alzheimer-related terms
        return self.search_nodes('alzheimer|dementia|ad|apoE|psen|app|tau|amyloid|neurodeg', column='node_name')