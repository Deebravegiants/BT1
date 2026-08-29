# Q3226: interpolate-rate via supply-collateral-add: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) while controlling vault share price at the moment of the deposit leg, can an unprivileged attacker make `interpolate-rate` (mainnet/contracts/vault/v0-vault-stx.clar:196) leave a residue that no reconciliation pass ever inspects? `interpolate-rate` interpolates between packed u16 curve points, so the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury would fail, yielding direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:196` -> `interpolate-rate`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: vault share price at the moment of the deposit leg
- Exploit idea: `interpolate-rate` interpolates between packed u16 curve points. Reach it through `supply-collateral-add` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `supply-collateral-add` with vault share price at the moment of the deposit leg, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
