# Q3910: calc-principal-ratio-reduction via accrue: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) while controlling the block time at which accrual is first triggered in a block, can an unprivileged attacker make `calc-principal-ratio-reduction` (mainnet/contracts/vault/v0-vault-stx.clar:191) leave a residue that no reconciliation pass ever inspects? `calc-principal-ratio-reduction` reduces scaled principal proportionally to an amount over total debt, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:191` -> `calc-principal-ratio-reduction`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the block time at which accrual is first triggered in a block
- Exploit idea: `calc-principal-ratio-reduction` reduces scaled principal proportionally to an amount over total debt. Reach it through `accrue` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `accrue` with the block time at which accrual is first triggered in a block, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
