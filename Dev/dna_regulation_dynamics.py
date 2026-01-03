# dna_regulation_dynamics.py
# Multidimensional DNA regulatory simulation adapted from harmony/peptide attractor
# Models regulatory expression as harmony basin (accurate cell-type prediction)
# vs. dysregulation rigidity (e.g., hypermethylation silencing, cancer-like traps)
# Lineage: Neuresthetic Ethics Eternal – DNA Multidimensional Hardening
# Evaluation: 2025-12-20

import sympy as sp
import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

# Symbolic Definitions
t, rho, P, epi, kappa, v_s, lam, mu = sp.symbols('t rho P epi kappa v_s lambda mu')

# Rigidity (dysregulation, e.g., overfixed epigenetics)
drho_dt = v_s * (1 - kappa) * (1 - rho) * epi - lam * rho + mu * rho * (1 - rho)

# Power (expression accuracy / cellular adequacy)
dP_dt = P * (1 - rho) * kappa * lam - v_s * rho * P * epi

# Epigenetic state (accessibility transient, 0 closed → 1 open)
depi_dt = lam * (1 - epi) - mu * epi * rho  # Simplified modulation

# Adaptive kappa (reciprocal coupling across dimensions)
kappa_t = kappa * sp.tanh((P - rho) + (epi - 0.5))  # Boost when balanced

# Numerical simulation
def dna_dynamics(y, t, kappa_val=0.9, lam_val=0.4, v_s_val=0.3, mu_val=0.1):
    rho, P, epi = y
    drho = v_s_val * (1 - kappa_val) * (1 - rho) * epi - lam_val * rho + mu_val * rho * (1 - rho)
    dP = P * (1 - rho) * kappa_val * lam_val - v_s_val * rho * P * epi
    depi = lam_val * (1 - epi) - mu_val * epi * rho
    return [drho, dP, depi]

# Initial conditions: benign start (low rigidity, moderate power/access)
y0_benign = [0.1, 1.0, 0.8]

# Toxic start (epigenetic stressor spike)
y0_toxic = [0.2, 0.8, 0.3]

t_span = np.linspace(0, 20, 200)

sol_benign = odeint(dna_dynamics, y0_benign, t_span)
sol_toxic = odeint(dna_dynamics, y0_toxic, t_span)

# Plot trajectories
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
plt.plot(t_span, sol_benign[:, 0], label='ρ (Benign)', color='green')
plt.plot(t_span, sol_toxic[:, 0], label='ρ (Dysregulated)', color='red')
plt.plot(t_span, sol_benign[:, 2], label='Epigenetic Access (Benign)', color='lightgreen', linestyle='--')
plt.plot(t_span, sol_toxic[:, 2], label='Epigenetic Access (Toxic)', color='pink', linestyle='--')
plt.xlabel('Time')
plt.ylabel('State')
plt.title('Multidimensional Trajectories')
plt.legend()
plt.grid(True)

plt.subplot(1, 2, 2)
plt.plot(sol_benign[:, 0], sol_benign[:, 1], label='Benign Attractor', color='green')
plt.plot(sol_toxic[:, 0], sol_toxic[:, 1], label='Rigidity Trap', color='red')
plt.xlabel('ρ (Rigidity)')
plt.ylabel('P (Expression Power)')
plt.title('Phase Space: Harmony vs Dysregulation')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()

# Fixed point approximation
print("Benign attractor approximates low ρ, high P, balanced epi under preemptive κ")