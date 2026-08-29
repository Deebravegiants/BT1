# Q5240: write-feeds via collateral-add: record a repayment larger than the value actually delivere

## Question
Does `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) let an unprivileged attacker who controls the `ft` trait principal reach `write-feeds` (mainnet/contracts/market/v0-4-market.clar:149) in a state where it record a repayment larger than the value actually delivered? Given that it folds up to three attacker-supplied buffers through `write-feed` with a `(response bool uint)` accumulator, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:149` -> `write-feeds`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `write-feeds` folds up to three attacker-supplied buffers through `write-feed` with a `(response bool uint)` accumulator. Reach it through `collateral-add` and record a repayment larger than the value actually delivered.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `collateral-add` twice with the `ft` trait principal varied, and assert that the value `write-feeds` returns is identical in both runs; a divergence confirms the finding.
