# Q2654: calc-treasury-lp-preview via deposit: have the same quantity scaled twice by two contracts that 

## Question
Entering through `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) while controlling `amount`, can an unprivileged attacker make `calc-treasury-lp-preview` (mainnet/contracts/vault/v0-vault-stx.clar:350) have the same quantity scaled twice by two contracts that round differently? `calc-treasury-lp-preview` divides by `(- ta-preview reserve-inc)`, a denominator that can reach zero or underflow, so the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:350` -> `calc-treasury-lp-preview`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `calc-treasury-lp-preview` divides by `(- ta-preview reserve-inc)`, a denominator that can reach zero or underflow. Reach it through `deposit` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `deposit` twice with `amount` varied, and assert that the value `calc-treasury-lp-preview` returns is identical in both runs; a divergence confirms the finding.
