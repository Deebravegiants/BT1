# Q4896: total-debt via redeem: record a repayment larger than the value actually delivere

## Question
Does `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) let an unprivileged attacker who controls `amount` of shares burned reach `total-debt` (mainnet/contracts/vault/v0-vault-stx.clar:328) in a state where it record a repayment larger than the value actually delivered? Given that it computes cumulative debt from `principal-scaled` and `index`, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:328` -> `total-debt`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: `amount` of shares burned
- Exploit idea: `total-debt` computes cumulative debt from `principal-scaled` and `index`. Reach it through `redeem` and record a repayment larger than the value actually delivered.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `amount` of shares burned across its boundary values through `redeem` in simnet and assert `total-debt` never returns a value that breaks the invariant.
