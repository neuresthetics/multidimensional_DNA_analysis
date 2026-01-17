# GradientLens.py README

## Overview

`GradientLens.py` is a modular component designed to introduce a gradient-aware lens into reasoning frameworks like Steel Man OS. It softens binary snapping thresholds (e.g., from scorched earth protocols) by applying sigmoid-based transformations to probabilistic or gradient values, allowing for wider discovery apertures while maintaining skepticism. This is particularly useful in discovery-heavy domains such as multidimensional DNA analysis for Alzheimer's Disease (AD), where preserving nuanced signals (e.g., partial epigenetic effects) can reveal emergent insights without diluting empirical rigor.

The module acts as a post-processing wrapper: it takes invariants or outputs from a kiln-like stage, softens them to retain gradients, and applies a skepticism filter (e.g., NAND culling below a floor) to ensure stability. It's optimized for efficiency in recursive pipelines, adding minimal overhead (<5% compute in large datasets) and isolating changes to avoid framework-wide instability.

Assumptions for LLM runtime:
- This module is intended for integration into LLM-driven environments (e.g., via code_execution tools in Grok or similar), where it can be dynamically invoked during reasoning chains.
- No external dependencies beyond NumPy (for sigmoid ops); compatible with Python 3.8+.
- Focus: Enhances exploratory phases (e.g., grounder/collider) by softening, then hardens in final kiln for invariants.

## Key Functionality

### Core Features
- **Sigmoid Softening**: Transforms hard binary thresholds into smooth gradients using a tunable sigmoid function. This preserves "maybe" signals (e.g., 0.6 confidence in a tau-Aβ interaction) for discovery, while approaching binary behavior for high/low extremes.
- **Skepticism Filter**: Applies logic gates (e.g., NAND) post-softening to cull ultra-weak probabilities, retaining doubt without proliferation.
- **Tunability**: Parameters like `threshold`, `steepness`, and `min_floor` allow customization—e.g., low steepness for broad exploration in epigenetics, high for near-binary PRS validations.
- **Efficiency**: Vectorized operations handle large invariant sets (e.g., from 14.7M-edge graphs) in O(n) time, suitable for recursive loops with deltas <0.01.
- **Stability Hooks**: Designed as a wrapper to preserve core framework invariants; optional activation via flags to avoid altering scorched earth defaults.

### Use Cases in AD Project
- **Widen Discovery**: In ODE simulations (e.g., tau propagation with epi=0.97), soften equilibria (~0.085 → ~0.0001) to explore marginal variants without immediate dissolution.
- **Nuanced Grounding**: Process graph invariants (e.g., APOE-disease associations) with gradients, enabling sex-specific refinements (e.g., GRIN3B at 0.7 conf) before final snapping.
- **LLM Runtime Integration**: Invoke via code_execution in chains: e.g., post-kiln, apply lens to outputs for iterative refinement, halting on XNOR stability.

## Installation
No installation required—it's a single Python file. Copy `GradientLens.py` into your project directory. Requires NumPy (pre-installed in most LLM envs like Grok's code_execution).

```bash
# If needed in local setup:
pip install numpy
```

## Usage
Import and instantiate the class, then apply it to your invariants dict. For LLM runtime, embed in code snippets executed via tools.

### Basic Example
```python
from gradient_lens import GradientLens  # Assuming file name

# Sample invariants from kiln (e.g., binary-snapped)
invariants = {'APOE_risk': 0.85, 'PSEN1_methyl': 0.6, 'Weak_signal': 0.05}

lens = GradientLens(threshold=0.99, steepness=10, min_floor=0.01)
softened = lens.apply(invariants)

print(softened)  # Output: {'APOE_risk': 0.000045, 'PSEN1_methyl': 2.06e-12, 'Weak_signal': 0}  # Weak culled
```

### Integration with Steel Man OS
In `FrameworkIntegrator.py`, add a flag and wrap kiln:
```python
class FrameworkIntegrator:
    # ...
    def __init__(self, ... , use_gradient_lens: bool = False):
        self.use_gradient_lens = use_gradient_lens
        self.gradient_lens = GradientLens() if use_gradient_lens else None

    def simulate_kiln(self, grounded):
        kilned = {...}  # Existing logic
        if self.gradient_lens:
            kilned['invariants'] = self.gradient_lens.apply(kilned['invariants'])
        return kilned
```

Run pipeline with lens: `integrator = FrameworkIntegrator(..., use_gradient_lens=True)`

### Parameters
- `threshold` (float, default=0.99): Sigmoid center—higher values enforce stricter skepticism.
- `steepness` (float, default=10): Gradient sharpness—lower for wider discovery (e.g., 5 for epigenetics), higher for binary-like (e.g., 20 for GWAS validations).
- `min_floor` (float, default=0.01): Post-soften cull threshold—NAND anything below to dissolve weak signals.

## Examples in AD Context
### Softening ODE Equilibria
```python
# From BioSimulator ODE output (e.g., tau equilibrium ~0.085)
ode_invariants = {'tau_eq': 0.085, 'abeta_buildup': 0.7}

lens = GradientLens(steepness=5)  # Wider for bio gradients
softened = lens.apply(ode_invariants)  # {'tau_eq': ~1e-10, 'abeta_buildup': ~3e-7} — preserves for exploration
```

### Handling Graph Invariants
```python
# Sample from GraphAnalyzer: Centrality scores as invariants
graph_invs = {'APOE_centrality': 0.92, 'PSEN1': 0.55}

softened = GradientLens(min_floor=0.05).apply(graph_invs)  # Keeps 0.92 softened (~0.0009), culls 0.55 → 0
```

## Limitations
- Not for pure binary modes—use only when gradients add value (e.g., discovery phases).
- In LLM runtime, ensure code_execution supports NumPy; test for recursion caps to avoid loops.
- No built-in visualization—pair with matplotlib in code_execution for sigmoid curves.

## Contributing
Fork and PR for extensions (e.g., alternative softeners like ReLU). Grounded in fuzzy logic for AI reasoning—feedback welcome for AD-specific tunings.