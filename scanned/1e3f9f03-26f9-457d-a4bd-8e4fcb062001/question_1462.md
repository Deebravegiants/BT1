# Q1462: total-assets-preview via transfer: record a repayment larger than the value actually delivere

## Question
Entering through `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752) while controlling `amount`, can an unprivileged attacker make `total-assets-preview` (mainnet/contracts/vault/v0-vault-stx.clar:341) record a repayment larger than the value actually delivered? `total-assets-preview` re-derives a FORWARD index inside calls that have already accrued, so the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` would fail, yielding direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:341` -> `total-assets-preview`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `total-assets-preview` re-derives a FORWARD index inside calls that have already accrued. Reach it through `transfer` and record a repayment larger than the value actually delivered.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `transfer` with `amount`, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
