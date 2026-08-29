# Q3610: unwrap-status via collateral-remove: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) while controlling `amount` relative to the current collateral row (the removing-all branch), can an unprivileged attacker make `unwrap-status` (mainnet/contracts/registry/v0-assets.clar:111) leave a residue that no reconciliation pass ever inspects? `unwrap-status` resolves `status` with `unwrap-panic`, so the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury would fail, yielding direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:111` -> `unwrap-status`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: `amount` relative to the current collateral row (the removing-all branch)
- Exploit idea: `unwrap-status` resolves `status` with `unwrap-panic`. Reach it through `collateral-remove` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `collateral-remove` with `amount` relative to the current collateral row (the removing-all branch), and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
