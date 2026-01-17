# insight_accumulator.py
# A module for accumulating, ranking, and steel-manning hypotheses from graph analyses.
# Designed for AD-related insights from edge files, integrating Steel Man OS principles.

from typing import List, Dict, Any
import json

class InsightAccumulator:
    def __init__(self):
        """
        Initialize the accumulator with an empty list of hypotheses.
        """
        self.hypotheses: List[Dict[str, Any]] = []

    def add_hypothesis(self, hypothesis: str, strength: float, evidence_summary: str, 
                       steel_man_resolution: str, contributing_files: List[str]):
        """
        Add or update a hypothesis. If it exists, max the strength and append evidence/files.
        
        :param hypothesis: The steel-manned statement.
        :param strength: Normalized score (0.0-1.0).
        :param evidence_summary: Key evidence details.
        :param steel_man_resolution: Gate applications and alignments.
        :param contributing_files: List of file sources.
        """
        for h in self.hypotheses:
            if h['hypothesis'] == hypothesis:
                # Update existing: max strength, append evidence and files
                h['strength'] = max(h['strength'], strength)
                h['evidence_summary'] += f"; {evidence_summary}"
                h['contributing_files'] = list(set(h['contributing_files'] + contributing_files))
                return
        
        # Add new
        self.hypotheses.append({
            'hypothesis': hypothesis,
            'strength': strength,
            'evidence_summary': evidence_summary,
            'steel_man_resolution': steel_man_resolution,
            'contributing_files': contributing_files
        })

    def rank_hypotheses(self) -> List[Dict[str, Any]]:
        """
        Rank hypotheses by descending strength and assign ranks.
        
        :return: Sorted list with added 'rank' key.
        """
        sorted_hypos = sorted(self.hypotheses, key=lambda x: x['strength'], reverse=True)
        for i, h in enumerate(sorted_hypos, start=1):
            h['rank'] = i
        return sorted_hypos

    def to_json(self) -> str:
        """
        Export ranked hypotheses as JSON string.
        
        :return: JSON representation.
        """
        return json.dumps(self.rank_hypotheses(), indent=2)

    def load_from_json(self, json_str: str):
        """
        Load hypotheses from JSON string.
        
        :param json_str: JSON data.
        """
        data = json.loads(json_str)
        self.hypotheses = [ {k: v for k, v in item.items() if k != 'rank'} for item in data ]

    def apply_steel_man(self, hypothesis: str, gate: str = 'XNOR') -> str:
        """
        Simulate steel-manning a hypothesis with a gate (placeholder for full OS integration).
        
        :param hypothesis: The hypothesis to strengthen.
        :param gate: Logic gate (e.g., 'XNOR' for invariance).
        :return: Strengthened version.
        """
        # Placeholder: In full impl, integrate collider/joiner/grounder/kiln logic.
        return f"{hypothesis} [Strengthened via {gate} gate for invariance]."

# Example usage:
if __name__ == "__main__":
    accumulator = InsightAccumulator()
    accumulator.add_hypothesis(
        "Gene 1019 (CDK4) plays a central role in AD-related networks.",
        0.25,
        "High degree in disease_protein.",
        "AND-chained to GWAS loci.",
        ["Parts 6, 7"]
    )
    print(accumulator.to_json())