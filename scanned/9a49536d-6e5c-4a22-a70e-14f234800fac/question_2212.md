# Q2212: linear-interpolate via repay: credit one side of an accounting pair without the other

## Question
Does `repay` (mainnet/contracts/market/v0-4-market.clar:1316) let an unprivileged attacker who controls `on-behalf-of`, naming any third-party principal reach `linear-interpolate` (mainnet/contracts/vault/v0-vault-stx.clar:221) in a state where it credit one side of an accounting pair without the other? Given that it interpolates between two points, dividing by `(- x2 x1)`, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:221` -> `linear-interpolate`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: `on-behalf-of`, naming any third-party principal
- Exploit idea: `linear-interpolate` interpolates between two points, dividing by `(- x2 x1)`. Reach it through `repay` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `repay` with `on-behalf-of`, naming any third-party principal, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
