import numpy as np
from typing import Dict, Any

class GradientLens:
    def __init__(self, threshold: float = 0.99, steepness: float = 10, min_floor: float = 0.01):
        """
        Initialize gradient-aware lens.
        :param threshold: Central sigmoid point (e.g., 0.99 for high skepticism).
        :param steepness: Controls gradient sharpness (higher = more binary-like).
        :param min_floor: NAND-cull below this to retain doubt.
        """
        self.threshold = threshold
        self.steepness = steepness
        self.min_floor = min_floor
        self.gates = {
            'NAND': lambda a, b: not (a and b)
        }

    def soften(self, value: float) -> float:
        """Apply sigmoid softening to preserve gradients."""
        return 1 / (1 + np.exp(-self.steepness * (value - self.threshold)))

    def apply(self, invariants: Dict[str, Any]) -> Dict[str, Any]:
        """
        Soften kiln invariants, then filter for skepticism.
        :param invariants: Kiln output dict.
        :return: Softened and filtered invariants.
        """
        softened = {}
        for key, val in invariants.items():
            if isinstance(val, (int, float)):
                soft_val = self.soften(val)
                # Skepticism gate: Cull if too low, else keep gradient
                if self.gates['NAND'](soft_val < self.min_floor, True):
                    softened[key] = soft_val
                else:
                    softened[key] = 0  # Dissolve weak signals
        return softened

# Usage in FrameworkIntegrator (add to simulate_kiln)
# self.gradient_lens = GradientLens()
# return self.gradient_lens.apply(kilned_invariants)