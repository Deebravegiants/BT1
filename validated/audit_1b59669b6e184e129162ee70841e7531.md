Looking at the vulnerability class from the report — a privileged role can access/use restricted assets that bypass safety invariants — I need to find an analog in the NEAR MPC codebase where a privileged role (below threshold) can bypass the threshold requirement.

Let me examine the `respond_ckd` function closely.