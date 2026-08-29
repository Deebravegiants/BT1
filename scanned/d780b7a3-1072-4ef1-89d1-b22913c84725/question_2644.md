# Q2644: resolve-interpolation-points via call-ststx-ratio: credit one side of an accounting pair without the other

## Question
Does `call-ststx-ratio` (mainnet/contracts/market/v0-4-market.clar:1015) let an unprivileged attacker who controls whether the ratio is fetched before or after other state changes in the block reach `resolve-interpolation-points` (mainnet/contracts/vault/v0-vault-stx.clar:205) in a state where it credit one side of an accounting pair without the other? Given that it selects the bracketing curve points for a utilization, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:205` -> `resolve-interpolation-points`
- Entrypoint: `call-ststx-ratio` (`mainnet/contracts/market/v0-4-market.clar:1015`), unprivileged and publicly callable
- Attacker controls: whether the ratio is fetched before or after other state changes in the block
- Exploit idea: `resolve-interpolation-points` selects the bracketing curve points for a utilization. Reach it through `call-ststx-ratio` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `call-ststx-ratio` with whether the ratio is fetched before or after other state changes in the block, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
