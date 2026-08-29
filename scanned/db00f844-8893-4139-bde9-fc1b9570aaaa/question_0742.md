# Q0742: principal-ratio-reduction via accrue: mint shares whose backing was never received

## Question
Entering through `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) while controlling the block time at which accrual is first triggered in a block, can an unprivileged attacker make `principal-ratio-reduction` (mainnet/contracts/vault/v0-vault-stx.clar:406) mint shares whose backing was never received? `principal-ratio-reduction` derives a principal reduction from an amount, the scaled principal and the previewed debt, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:406` -> `principal-ratio-reduction`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the block time at which accrual is first triggered in a block
- Exploit idea: `principal-ratio-reduction` derives a principal reduction from an amount, the scaled principal and the previewed debt. Reach it through `accrue` and mint shares whose backing was never received.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `accrue` with the block time at which accrual is first triggered in a block, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
