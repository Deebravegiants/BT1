# Q0970: total-assets-preview via accrue: mint shares whose backing was never received

## Question
Entering through `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) while controlling the block time at which accrual is first triggered in a block, can an unprivileged attacker make `total-assets-preview` (mainnet/contracts/vault/v0-vault-stx.clar:341) mint shares whose backing was never received? `total-assets-preview` re-derives a FORWARD index inside calls that have already accrued, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:341` -> `total-assets-preview`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the block time at which accrual is first triggered in a block
- Exploit idea: `total-assets-preview` re-derives a FORWARD index inside calls that have already accrued. Reach it through `accrue` and mint shares whose backing was never received.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `accrue` with the block time at which accrual is first triggered in a block, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
