# Q0159: write-feed via call-ststx-ratio: have the same quantity scaled twice by two contracts that 

## Question
`write-feed` (mainnet/contracts/market/v0-4-market.clar:129) applies one Pyth price-feed update and folds its status. Can an unprivileged caller of `call-ststx-ratio` (mainnet/contracts/market/v0-4-market.clar:1015), by choosing the block and transaction position at which the external ratio is fetched, use that to have the same quantity scaled twice by two contracts that round differently, violating the invariant that shares outstanding valued at the current share price never exceed `total-assets` and producing permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:129` -> `write-feed`
- Entrypoint: `call-ststx-ratio` (`mainnet/contracts/market/v0-4-market.clar:1015`), unprivileged and publicly callable
- Attacker controls: the block and transaction position at which the external ratio is fetched
- Exploit idea: `write-feed` applies one Pyth price-feed update and folds its status. Reach it through `call-ststx-ratio` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `write-feed` touches, run `call-ststx-ratio` with the block and transaction position at which the external ratio is fetched, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
