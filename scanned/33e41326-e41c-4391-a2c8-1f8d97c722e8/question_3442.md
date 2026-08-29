# Q3442: find-debt-scaled via collateral-remove: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) while controlling `amount` relative to the current collateral row (the removing-all branch), can an unprivileged attacker make `find-debt-scaled` (mainnet/contracts/market/v0-4-market.clar:621) leave a residue that no reconciliation pass ever inspects? `find-debt-scaled` returns u0 for an absent asset, making a missing debt row indistinguishable from no debt, so the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury would fail, yielding direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:621` -> `find-debt-scaled`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: `amount` relative to the current collateral row (the removing-all branch)
- Exploit idea: `find-debt-scaled` returns u0 for an absent asset, making a missing debt row indistinguishable from no debt. Reach it through `collateral-remove` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `collateral-remove` with `amount` relative to the current collateral row (the removing-all branch), and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
