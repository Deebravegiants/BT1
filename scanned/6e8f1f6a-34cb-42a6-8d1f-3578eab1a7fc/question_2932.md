# Q2932: total-debt via supply-collateral-add: credit one side of an accounting pair without the other

## Question
Does `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) let an unprivileged attacker who controls vault share price at the moment of the deposit leg reach `total-debt` (mainnet/contracts/vault/v0-vault-stx.clar:328) in a state where it credit one side of an accounting pair without the other? Given that it computes cumulative debt from `principal-scaled` and `index`, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:328` -> `total-debt`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: vault share price at the moment of the deposit leg
- Exploit idea: `total-debt` computes cumulative debt from `principal-scaled` and `index`. Reach it through `supply-collateral-add` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `supply-collateral-add` with vault share price at the moment of the deposit leg, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
