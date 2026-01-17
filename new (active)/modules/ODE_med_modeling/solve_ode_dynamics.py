def solve_ode_dynamics(self, model_type: str = 'general', params: Optional[Dict[str, float]] = None, t_span: List[float] = [0, 10], steps: int = 100) -> pd.DataFrame:
    """
    Solve ODE for regulatory dynamics with AD-specific models.
    :param model_type: 'general' (default), 'abeta' (Aβ aggregation), 'tau' (tau propagation), or 'epigenetic' (methylation influence).
    :param params: Optional dict to override defaults (e.g., {'beta': 0.1, 'delta': 0.05}).
    :param t_span: Time span [start, end]
    :param steps: Number of evaluation steps
    :return: DataFrame with time and state values
    """
    t = sp.symbols('t')
    x = sp.Function('x')(t)  # State variable (e.g., Aβ concentration or methylation level)
    
    # Default params
    if params is None:
        params = {}
    
    if model_type == 'abeta':  # Aβ aggregation: dx/dt = β - δx + γx^2 (production - degradation + aggregation)
        beta = params.get('beta', 0.1)  # Production rate
        delta = params.get('delta', 0.05)  # Degradation rate
        gamma = params.get('gamma', 0.001)  # Aggregation rate
        ode = sp.Eq(x.diff(t), beta - delta * x + gamma * x**2)
    
    elif model_type == 'tau':  # Tau propagation: dx/dt = ρ (1 - x) - epi * x (rigidity vs. epigenetic spread)
        rho = params.get('rho', 0.09)
        epi = params.get('epi', 0.97)
        ode = sp.Eq(x.diff(t), rho * (1 - x) - epi * x)
    
    elif model_type == 'epigenetic':  # Methylation dynamics: dx/dt = m_rate * (1 - x) - d_rate * x (methylation - demethylation)
        m_rate = params.get('m_rate', 0.03)  # Hypermethylation rate in AD loci
        d_rate = params.get('d_rate', 0.02)  # Demethylation (hypo in PSEN1)
        ode = sp.Eq(x.diff(t), m_rate * (1 - x) - d_rate * x)
    
    else:  # General/fallback
        rho = params.get('rho', 0.09)
        epi = params.get('epi', 0.97)
        ode = sp.Eq(x.diff(t), rho * (1 - x) - epi * x)
    
    sol = sp.dsolve(ode, x)
    
    # Numerical evaluation (initial x(0)=0.5)
    times = np.linspace(t_span[0], t_span[1], steps)
    C1 = 0.5  # Placeholder constant
    func = sp.lambdify(t, sol.rhs.subs('C1', C1), 'numpy')
    states = func(times)
    
    return pd.DataFrame({'time': times, 'state': states})