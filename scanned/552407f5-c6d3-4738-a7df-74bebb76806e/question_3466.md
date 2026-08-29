# Q3466: filter-out-debt-asset via collateral-add: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) while controlling the `ft` trait principal, can an unprivileged attacker make `filter-out-debt-asset` (mainnet/contracts/market/v0-4-market.clar:633) leave a residue that no reconciliation pass ever inspects? `filter-out-debt-asset` rebuilds the debt list without one asset, under `as-max-len? ... u64`, so the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury would fail, yielding direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:633` -> `filter-out-debt-asset`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `filter-out-debt-asset` rebuilds the debt list without one asset, under `as-max-len? ... u64`. Reach it through `collateral-add` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `collateral-add` with the `ft` trait principal, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
