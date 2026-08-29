# Q3850: total-assets-preview via collateral-remove-redeem: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) while controlling `receiver` for the underlying leg, can an unprivileged attacker make `total-assets-preview` (mainnet/contracts/vault/v0-vault-stx.clar:341) leave a residue that no reconciliation pass ever inspects? `total-assets-preview` re-derives a FORWARD index inside calls that have already accrued, so the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury would fail, yielding theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:341` -> `total-assets-preview`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `receiver` for the underlying leg
- Exploit idea: `total-assets-preview` re-derives a FORWARD index inside calls that have already accrued. Reach it through `collateral-remove-redeem` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `collateral-remove-redeem` with `receiver` for the underlying leg, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
