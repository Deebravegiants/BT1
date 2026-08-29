# Q5916: write-feeds via call-ststx-ratio: have the same quantity scaled twice by two contracts that 

## Question
Does `call-ststx-ratio` (mainnet/contracts/market/v0-4-market.clar:1015) let an unprivileged attacker who controls whether the ratio is fetched before or after other state changes in the block reach `write-feeds` (mainnet/contracts/market/v0-4-market.clar:149) in a state where it have the same quantity scaled twice by two contracts that round differently? Given that it folds up to three attacker-supplied buffers through `write-feed` with a `(response bool uint)` accumulator, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:149` -> `write-feeds`
- Entrypoint: `call-ststx-ratio` (`mainnet/contracts/market/v0-4-market.clar:1015`), unprivileged and publicly callable
- Attacker controls: whether the ratio is fetched before or after other state changes in the block
- Exploit idea: `write-feeds` folds up to three attacker-supplied buffers through `write-feed` with a `(response bool uint)` accumulator. Reach it through `call-ststx-ratio` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz whether the ratio is fetched before or after other state changes in the block across its boundary values through `call-ststx-ratio` in simnet and assert `write-feeds` never returns a value that breaks the invariant.
