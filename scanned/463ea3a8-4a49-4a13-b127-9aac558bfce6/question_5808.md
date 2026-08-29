# Q5808: total-assets-preview via collateral-remove-redeem: record a repayment larger than the value actually delivere

## Question
Does `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) let an unprivileged attacker who controls `receiver` for the underlying leg reach `total-assets-preview` (mainnet/contracts/vault/v0-vault-stx.clar:341) in a state where it record a repayment larger than the value actually delivered? Given that it re-derives a FORWARD index inside calls that have already accrued, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:341` -> `total-assets-preview`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `receiver` for the underlying leg
- Exploit idea: `total-assets-preview` re-derives a FORWARD index inside calls that have already accrued. Reach it through `collateral-remove-redeem` and record a repayment larger than the value actually delivered.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `receiver` for the underlying leg across its boundary values through `collateral-remove-redeem` in simnet and assert `total-assets-preview` never returns a value that breaks the invariant.
