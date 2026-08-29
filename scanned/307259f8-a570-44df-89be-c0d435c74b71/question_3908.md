# Q3908: normalize via call-ststx-ratio: make the per-user ledger and the vault aggregate disagree 

## Question
Does `call-ststx-ratio` (mainnet/contracts/market/v0-4-market.clar:1015) let an unprivileged attacker who controls the block and transaction position at which the external ratio is fetched reach `normalize` (mainnet/contracts/market/v0-4-market.clar:576) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it divides by `(pow u10 decimals)` only AFTER multiplying amount by price, making the protocol's USD unit a whole dollar, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:576` -> `normalize`
- Entrypoint: `call-ststx-ratio` (`mainnet/contracts/market/v0-4-market.clar:1015`), unprivileged and publicly callable
- Attacker controls: the block and transaction position at which the external ratio is fetched
- Exploit idea: `normalize` divides by `(pow u10 decimals)` only AFTER multiplying amount by price, making the protocol's USD unit a whole dollar. Reach it through `call-ststx-ratio` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `call-ststx-ratio` twice with the block and transaction position at which the external ratio is fetched varied, and assert that the value `normalize` returns is identical in both runs; a divergence confirms the finding.
