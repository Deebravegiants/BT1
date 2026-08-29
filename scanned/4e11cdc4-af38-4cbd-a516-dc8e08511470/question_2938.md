# Q2938: total-debt via redeem: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) while controlling `amount` of shares burned, can an unprivileged attacker make `total-debt` (mainnet/contracts/vault/v0-vault-stx.clar:328) leave a residue that no reconciliation pass ever inspects? `total-debt` computes cumulative debt from `principal-scaled` and `index`, so the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury would fail, yielding direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:328` -> `total-debt`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: `amount` of shares burned
- Exploit idea: `total-debt` computes cumulative debt from `principal-scaled` and `index`. Reach it through `redeem` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `redeem` with `amount` of shares burned, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
