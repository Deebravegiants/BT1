# Q2986: refresh via repay: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `repay` (mainnet/contracts/market/v0-4-market.clar:1316) while controlling `amount`, including far above the real debt (the capping path), can an unprivileged attacker make `refresh` (mainnet/contracts/market/v0-market-vault.clar:171) leave a residue that no reconciliation pass ever inspects? `refresh` rewrites `mask` and stamps `last-update` to `stacks-block-time` on every write, so the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury would fail, yielding direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:171` -> `refresh`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: `amount`, including far above the real debt (the capping path)
- Exploit idea: `refresh` rewrites `mask` and stamps `last-update` to `stacks-block-time` on every write. Reach it through `repay` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `repay` with `amount`, including far above the real debt (the capping path), and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
