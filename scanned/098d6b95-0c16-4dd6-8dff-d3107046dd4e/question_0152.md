# Q0152: resolve-price-feed via call-ststx-ratio: destroy value through a truncation the opposite operation 

## Question
Does `call-ststx-ratio` (mainnet/contracts/market/v0-4-market.clar:1015) let an unprivileged attacker who controls whether the ratio is fetched before or after other state changes in the block reach `resolve-price-feed` (mainnet/contracts/market/v0-4-market.clar:332) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it dispatches on a 1-byte type to `resolve-pyth` or `resolve-dia`, erroring otherwise, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:332` -> `resolve-price-feed`
- Entrypoint: `call-ststx-ratio` (`mainnet/contracts/market/v0-4-market.clar:1015`), unprivileged and publicly callable
- Attacker controls: whether the ratio is fetched before or after other state changes in the block
- Exploit idea: `resolve-price-feed` dispatches on a 1-byte type to `resolve-pyth` or `resolve-dia`, erroring otherwise. Reach it through `call-ststx-ratio` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `call-ststx-ratio` twice with whether the ratio is fetched before or after other state changes in the block varied, and assert that the value `resolve-price-feed` returns is identical in both runs; a divergence confirms the finding.
