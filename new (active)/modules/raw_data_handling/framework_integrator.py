import json
from typing import Dict, Any, List, Optional
from node_handler import NodeHandler
from edge_handler import EdgeHandler
from graph_analyzer import GraphAnalyzer
from bio_simulator import BioSimulator
import networkx as nx
import pandas as pd

class FrameworkIntegrator:
    def __init__(self, node_handler: NodeHandler, edge_handler: EdgeHandler, bio_simulator: BioSimulator, os_config_file: str = 'steel_man_os.json'):
        self.node_handler = node_handler
        self.edge_handler = edge_handler
        self.analyzer = GraphAnalyzer(node_handler, edge_handler)
        self.bio_simulator = bio_simulator
        self.os_config = self._load_os_config(os_config_file)
        self.gates = {
            'AND': lambda a, b: a and b,
            'OR': lambda a, b: a or b,
            'NOT': lambda a: not a,
            'NAND': lambda a, b: not (a and b),
            'NOR': lambda a, b: not (a or b),
            'XOR': lambda a, b: a != b,
            'XNOR': lambda a, b: a == b
        }

    def _load_os_config(self, file_path: str) -> Dict[str, Any]:
        """
        Load Steel Man OS configuration from JSON.
        """
        with open(file_path, 'r') as f:
            return json.load(f)

    def extract_invariants_from_graph(self, subgraph: Optional[nx.DiGraph] = None) -> List[Dict[str, Any]]:
        """
        Extract boolean invariants from graph (e.g., AD associations).
        :param subgraph: Optional subgraph; defaults to AD-relevant.
        :return: List of invariants (e.g., {'claim': 'APOE associated with AD', 'value': True})
        """
        if subgraph is None:
            subgraph = self.edge_handler.get_ad_relevant_subgraph()
        
        invariants = []
        for u, v, attrs in subgraph.edges(data=True):
            if 'disease' in attrs.get('x_type', '') and 'gene' in attrs.get('y_type', ''):
                claim = f"{attrs['x_name']} associated with {attrs['y_name']}"
                value = self.gates['XNOR'](True, 'associated' in attrs['relation'])  # Simple gate check
                invariants.append({'claim': claim, 'value': value})
        
        return invariants

    def simulate_constructor(self, input_stance: str) -> Dict[str, Any]:
        """
        Simulate Steel Man Constructor: Deconstruct to primitives, reconstruct with gates.
        :param input_stance: Idea/argument (e.g., 'Integrate DNA for AD risk')
        :return: Gated steel man structure
        """
        # Deconstruct: Search nodes for primitives
        primitives = self.node_handler.search_nodes(input_stance)
        axioms = []  # Elicit via gates
        for _, row in primitives.iterrows():
            axioms.append({
                'axiom': row['node_name'],
                'validated': self.gates['AND'](row['node_type'] == 'gene/protein', 'NCBI' in row['node_source'])
            })
        
        return {
            'definitions': primitives['node_name'].tolist(),
            'axioms': axioms,
            'invariants_ledger': f"Processed {len(axioms)} axioms"
        }

    def simulate_collider(self, steel_men: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Simulate Collider: Fragment and synthesize via gates.
        :param steel_men: List of steel men from constructor
        :return: Collided output
        """
        if len(steel_men) < 2:
            return steel_men[0] if steel_men else {}
        
        # XOR for differences, AND for synthesis
        fragments = []
        for i in range(len(steel_men) - 1):
            diff = self.gates['XOR'](steel_men[i], steel_men[i+1])  # Simplified
            fragments.append(diff)
        
        synthesis = {'syntheses': [self.gates['AND'](f1, f2) for f1 in fragments for f2 in fragments]}
        return synthesis

    def simulate_joiner(self, collided: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate Joiner: Unify with NAND reductions (scorched earth default).
        :param collided: Output from collider
        :return: Unified system
        """
        unified = {}
        for key, value in collided.items():
            unified[key] = self.gates['NAND'](value, value)  # Reduce
        return unified

    def simulate_grounder(self, unified: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate Grounder: Anchor to empirics via bio simulator/tools.
        :param unified: Output from joiner
        :return: Grounded output
        """
        grounded = {}
        for key, value in unified.items():
            if isinstance(value, str) and 'gene' in value.lower():
                seq = self.bio_simulator.fetch_gene_sequence(value)
                grounded[key] = {'sequence': seq[:100], 'grounded': len(seq) > 0}
        return grounded

    def simulate_kiln(self, grounded: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate Kiln: Dissolve to boolean invariants with HHM.
        :param grounded: Output from grounder
        :return: Kilned invariants
        """
        invariants = {}
        for key, value in grounded.items():
            invariants[key] = self.gates['XNOR'](value.get('grounded', False), True)  # Snap to 0/1
        return {'invariants': invariants}

    def run_pipeline(self, input_stance: str) -> Dict[str, Any]:
        """
        Run full Steel Man OS pipeline on input, using graph/bio data.
        :param input_stance: Starting idea/stance
        :return: Final kilned output
        """
        constructed = self.simulate_constructor(input_stance)
        # Seeker placeholder: Assume analogical extraction as pass-through
        seeker_out = constructed  # TODO: Implement if needed
        collided = self.simulate_collider([constructed, seeker_out])
        joined = self.simulate_joiner(collided)
        grounded = self.simulate_grounder(joined)
        kilned = self.simulate_kiln(grounded)
        
        # Recursion simulation: Check fixed point (simple equality)
        if kilned == self.run_pipeline(input_stance):  # Halt condition
            return kilned
        return self.run_pipeline(input_stance)  # Recurse (cap in practice)

# Usage Example
if __name__ == "__main__":
    node_h = NodeHandler('nodes.csv')
    edge_h = EdgeHandler('edges_part*.csv', batch_size=50)
    bio_sim = BioSimulator(email='example@email.com')
    integrator = FrameworkIntegrator(node_h, edge_h, bio_sim)
    
    invariants = integrator.extract_invariants_from_graph()
    print("Invariants:", invariants[:5])
    
    output = integrator.run_pipeline('Integrate multidimensional DNA for AD risk')
    print("Pipeline Output:", output)