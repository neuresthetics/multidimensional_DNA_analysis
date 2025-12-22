import pandas as pd
import re
import numpy as np
from scipy.integrate import odeint
from scipy.optimize import fsolve
import networkx as nx

class NodesHandler:
    """
    Enhanced stateful handler for nodes.csv and optional edges_part1.csv in multidimensional DNA analysis.
    Upgraded for edges integration (PPI networks), AD interactome extraction, degree-scaled ODE params,
    and 2025 CASP8/polyGR hardening. Advances predictive prototyping by fusing graph metrics with dynamics
    for * factors (e.g., hub degree as mu boosters) and DNA markers (e.g., connectivity-scaled v_s).
    
    Attributes:
        nodes_df (pd.DataFrame): Cached nodes.csv.
        edges_df (pd.DataFrame | None): Cached edges_part1.csv (optional).
        G (nx.Graph | None): Undirected PPI graph (built on demand).
    
    Lineage: Neuresthetic Ethics Eternal – DNA Ontology Hardening
    Evaluation: 2025-12-21 (Edges-integrated for network invariance)
    """
    
    def __init__(self, nodes_path: str, edges_path: str | None = None):
        """
        Initializes with nodes.csv; optionally loads edges_part1.csv for graph analysis.
        
        Args:
            nodes_path (str): Path to nodes.csv.
            edges_path (str | None): Path to edges_part1.csv (optional for PPI networks).
        
        Raises:
            FileNotFoundError: If files not found.
            ValueError: If structures invalid.
        """
        try:
            self.nodes_df = pd.read_csv(nodes_path, dtype=str)
            expected_node_cols = ['node_index', 'node_id', 'node_type', 'node_name', 'node_source']
            if not all(col in self.nodes_df.columns for col in expected_node_cols):
                raise ValueError(f"Invalid nodes structure. Expected: {expected_node_cols}")
            print(f"Loaded {len(self.nodes_df)} nodes.")
            
            self.edges_df = None
            self.G = None
            if edges_path:
                self.edges_df = pd.read_csv(edges_path, dtype=str)
                expected_edge_cols = ['edge_index', 'direction', 'relation', 'x_index', 'y_index']
                if not all(col in self.edges_df.columns for col in expected_edge_cols):
                    raise ValueError(f"Invalid edges structure. Expected: {expected_edge_cols}")
                print(f"Loaded {len(self.edges_df)} edges.")
        except FileNotFoundError as e:
            raise FileNotFoundError(f"File not found: {e.filename}")
        except pd.errors.EmptyDataError:
            raise ValueError("Empty or malformed file")
    
    def build_graph(self) -> nx.Graph:
        """
        Builds undirected PPI graph from edges (lazy-loaded).
        
        Returns:
            nx.Graph: PPI network.
        """
        if self.G is None and self.edges_df is not None:
            self.G = nx.Graph()
            forward_edges = self.edges_df[self.edges_df['direction'] == 'forward']
            for _, row in forward_edges.iterrows():
                self.G.add_edge(row['x_index'], row['y_index'], relation=row['relation'])
            print(f"Built graph with {self.G.number_of_nodes()} nodes and {self.G.number_of_edges()} edges.")
        return self.G
    
    def query_by_type(self, node_type: str) -> pd.DataFrame:
        """Filters nodes by type (e.g., 'gene/protein')."""
        filtered = self.nodes_df[self.nodes_df['node_type'] == node_type]
        print(f"Found {len(filtered)} nodes of type '{node_type}'.")
        return filtered
    
    def search_name(self, keyword: str, case_sensitive: bool = False) -> pd.DataFrame:
        """Searches node_name via regex."""
        flags = 0 if case_sensitive else re.IGNORECASE
        pattern = re.compile(re.escape(keyword), flags)
        filtered = self.nodes_df[self.nodes_df['node_name'].str.contains(pattern, na=False)]
        print(f"Found {len(filtered)} nodes matching '{keyword}'.")
        return filtered
    
    def get_ad_markers(self) -> pd.DataFrame:
        """Extracts AD markers (incl. 2025 CASP8/polyGR)."""
        ad_keywords = r'Alzheimer|AD|dementia|Amyloid|beta|Tau|APOE|APP|PSEN|TREM2|SORL1|MAPT|CASP8|polyGR'
        relevant_types = ['gene/protein', 'cell_subtype', 'pathway']
        filtered = self.nodes_df[
            self.nodes_df['node_name'].str.contains(ad_keywords, case=False, na=False) &
            self.nodes_df['node_type'].isin(relevant_types)
        ]
        print(f"Extracted {len(filtered)} AD markers (incl. 2025 updates).")
        return filtered
    
    def get_polygenic_cluster(self, genes_list: list) -> pd.DataFrame:
        """Retrieves polygenic subset."""
        filtered = self.nodes_df[self.nodes_df['node_name'].isin(genes_list)]
        print(f"Found {len(filtered)} nodes in cluster.")
        return filtered
    
    def summary_stats(self) -> dict:
        """Computes distribution metrics (nodes + edges if loaded)."""
        stats = {
            'total_nodes': len(self.nodes_df),
            'node_type_counts': self.nodes_df['node_type'].value_counts().to_dict(),
            'node_source_counts': self.nodes_df['node_source'].value_counts().to_dict()
        }
        if self.edges_df is not None:
            stats['total_edges'] = len(self.edges_df)
            stats['edge_relation_counts'] = self.edges_df['relation'].value_counts().to_dict()
        print(f"Summary: {stats['total_nodes']} nodes; edges: {stats.get('total_edges', 0)}.")
        return stats
    
    def get_ad_interactome(self) -> pd.DataFrame:
        """Extracts edges connected to AD markers (requires edges loaded)."""
        if self.edges_df is None:
            raise ValueError("Edges not loaded; provide edges_path in init.")
        ad_markers = self.get_ad_markers()
        ad_indices = ad_markers['node_index'].unique()
        ad_edges = self.edges_df[
            (self.edges_df['x_index'].isin(ad_indices)) | 
            (self.edges_df['y_index'].isin(ad_indices))
        ]
        print(f"Extracted {len(ad_edges)} AD-related edges.")
        return ad_edges
    
    def estimate_ode_params(self, cluster_df: pd.DataFrame, use_graph: bool = True) -> dict:
        """
        Estimates ODE params from cluster; upgraded with degree scaling if graph available.
        High-degree hubs elevate v_s/mu for propagation risk (e.g., MYC as toxicity amplifier).
        """
        num_risk_genes = len(cluster_df[cluster_df['node_name'].str.contains(r'APOE|APP|PSEN|TREM2|SORL1|MAPT|CASP8', case=False)])
        v_s_base = 0.3 + 0.1 * (num_risk_genes / max(1, len(cluster_df)))
        mu_base = 0.1 + 0.05 * (num_risk_genes / max(1, len(cluster_df)))
        
        if use_graph and self.G is not None:
            self.build_graph()  # Ensure built
            degrees = {idx: self.G.degree(idx) for idx in cluster_df['node_index'] if idx in self.G}
            if degrees:
                avg_degree = np.mean(list(degrees.values()))
                v_s = v_s_base * (1 + 0.05 * avg_degree)  # Scale by connectivity
                mu = mu_base * (1 + 0.03 * avg_degree)
            else:
                v_s, mu = v_s_base, mu_base
        else:
            v_s, mu = v_s_base, mu_base
        
        params = {'kappa': 0.9, 'lam': 0.4, 'v_s': min(v_s, 0.6), 'mu': min(mu, 0.2)}
        print(f"Estimated params from {len(cluster_df)} nodes (graph: {use_graph}): {params}.")
        return params
    
    def simulate_dna_dynamics(self, cluster_df: pd.DataFrame, t_span: np.ndarray, y0: list = [0.1, 1.0, 0.8]) -> np.ndarray:
        """Simulates ODEs with cluster params."""
        params = self.estimate_ode_params(cluster_df)
        
        def dna_dynamics(y, t, kappa, lam, v_s, mu):
            rho, P, epi = y
            drho = v_s * (1 - kappa) * (1 - rho) * epi - lam * rho + mu * rho * (1 - rho)
            dP = P * (1 - rho) * kappa * lam - v_s * rho * P * epi
            depi = lam * (1 - epi) - mu * epi * rho
            return [drho, dP, depi]
        
        sol = odeint(dna_dynamics, y0, t_span, args=(params['kappa'], params['lam'], params['v_s'], params['mu']))
        print(f"Simulated for {len(cluster_df)} nodes; final ρ: {sol[-1, 0]:.3f}.")
        return sol
    
    def find_fixed_point(self, cluster_df: pd.DataFrame) -> tuple:
        """Solves fixed point with cluster params."""
        params = self.estimate_ode_params(cluster_df)
        
        def eqs(vars, kappa, lam, v_s, mu):
            rho, epi = vars
            return [
                v_s * (1 - kappa) * (1 - rho) * epi - lam * rho + mu * rho * (1 - rho),
                lam * (1 - epi) - mu * epi * rho
            ]
        
        fixed_point = fsolve(eqs, [0.1, 0.8], args=(params['kappa'], params['lam'], params['v_s'], params['mu']))
        print(f"Fixed point for {len(cluster_df)} nodes: ρ≈{fixed_point[0]:.3f}, epi≈{fixed_point[1]:.3f}.")
        return tuple(fixed_point)

# Example REPL (uncomment):
# handler = NodesHandler('nodes.csv', 'edges_part1.csv')
# handler.summary_stats()
# ad_interactome = handler.get_ad_interactome()
# print(ad_interactome.head())
# cluster = handler.get_polygenic_cluster(['MYC', 'APP', 'APOE'])
# params = handler.estimate_ode_params(cluster)
# t_span = np.linspace(0, 50, 500)
# sol = handler.simulate_dna_dynamics(cluster, t_span)
# fixed = handler.find_fixed_point(cluster)