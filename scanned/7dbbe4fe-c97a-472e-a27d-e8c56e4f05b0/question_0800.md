# Q0800: vault-accrue via call-ststx-ratio: destroy value through a truncation the opposite operation 

## Question
Does `call-ststx-ratio` (mainnet/contracts/market/v0-4-market.clar:1015) let an unprivileged attacker who controls whether the ratio is fetched before or after other state changes in the block reach `vault-accrue` (mainnet/contracts/market/v0-4-market.clar:189) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it dispatches accrual to one of six vaults by asset id, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:189` -> `vault-accrue`
- Entrypoint: `call-ststx-ratio` (`mainnet/contracts/market/v0-4-market.clar:1015`), unprivileged and publicly callable
- Attacker controls: whether the ratio is fetched before or after other state changes in the block
- Exploit idea: `vault-accrue` dispatches accrual to one of six vaults by asset id. Reach it through `call-ststx-ratio` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `call-ststx-ratio` twice with whether the ratio is fetched before or after other state changes in the block varied, and assert that the value `vault-accrue` returns is identical in both runs; a divergence confirms the finding.
