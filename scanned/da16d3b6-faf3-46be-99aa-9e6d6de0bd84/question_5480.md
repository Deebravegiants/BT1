# Q5480: accrue-user-collateral via call-ststx-ratio: record a repayment larger than the value actually delivere

## Question
Does `call-ststx-ratio` (mainnet/contracts/market/v0-4-market.clar:1015) let an unprivileged attacker who controls the block and transaction position at which the external ratio is fetched reach `accrue-user-collateral` (mainnet/contracts/market/v0-4-market.clar:270) in a state where it record a repayment larger than the value actually delivered? Given that it accrues only rows that `is-ztoken` recognises, skipping everything else, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:270` -> `accrue-user-collateral`
- Entrypoint: `call-ststx-ratio` (`mainnet/contracts/market/v0-4-market.clar:1015`), unprivileged and publicly callable
- Attacker controls: the block and transaction position at which the external ratio is fetched
- Exploit idea: `accrue-user-collateral` accrues only rows that `is-ztoken` recognises, skipping everything else. Reach it through `call-ststx-ratio` and record a repayment larger than the value actually delivered.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `call-ststx-ratio` twice with the block and transaction position at which the external ratio is fetched varied, and assert that the value `accrue-user-collateral` returns is identical in both runs; a divergence confirms the finding.
