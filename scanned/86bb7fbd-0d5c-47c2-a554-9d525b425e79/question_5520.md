# Q5520: calc-cumulative-debt via accrue: record a repayment larger than the value actually delivere

## Question
Does `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) let an unprivileged attacker who controls the utilization the rate is interpolated at reach `calc-cumulative-debt` (mainnet/contracts/vault/v0-vault-stx.clar:180) in a state where it record a repayment larger than the value actually delivered? Given that it multiplies scaled principal by an index, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:180` -> `calc-cumulative-debt`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the utilization the rate is interpolated at
- Exploit idea: `calc-cumulative-debt` multiplies scaled principal by an index. Reach it through `accrue` and record a repayment larger than the value actually delivered.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the utilization the rate is interpolated at across its boundary values through `accrue` in simnet and assert `calc-cumulative-debt` never returns a value that breaks the invariant.
