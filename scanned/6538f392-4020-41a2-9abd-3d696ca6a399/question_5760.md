# Q5760: convert-to-shares-preview via supply-collateral-add: record a repayment larger than the value actually delivere

## Question
Does `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) let an unprivileged attacker who controls the position state the final collateral-add is validated against reach `convert-to-shares-preview` (mainnet/contracts/vault/v0-vault-stx.clar:308) in a state where it record a repayment larger than the value actually delivered? Given that it returns u0 outright when `total-assets-preview` is non-zero and supply is zero, minting nothing for a real deposit, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:308` -> `convert-to-shares-preview`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: the position state the final collateral-add is validated against
- Exploit idea: `convert-to-shares-preview` returns u0 outright when `total-assets-preview` is non-zero and supply is zero, minting nothing for a real deposit. Reach it through `supply-collateral-add` and record a repayment larger than the value actually delivered.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the position state the final collateral-add is validated against across its boundary values through `supply-collateral-add` in simnet and assert `convert-to-shares-preview` never returns a value that breaks the invariant.
