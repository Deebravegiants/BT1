# Q3178: principal-ratio-reduction via supply-collateral-add: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) while controlling `amount`, can an unprivileged attacker make `principal-ratio-reduction` (mainnet/contracts/vault/v0-vault-stx.clar:406) leave a residue that no reconciliation pass ever inspects? `principal-ratio-reduction` derives a principal reduction from an amount, the scaled principal and the previewed debt, so the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury would fail, yielding direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:406` -> `principal-ratio-reduction`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `principal-ratio-reduction` derives a principal reduction from an amount, the scaled principal and the previewed debt. Reach it through `supply-collateral-add` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `supply-collateral-add` with `amount`, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
