# Q0363: price-multi-resolve via call-ststx-ratio: have the same quantity scaled twice by two contracts that 

## Question
`price-multi-resolve` (mainnet/contracts/market/v0-4-market.clar:397) folds `iter-price-multi` into a POSITIONAL price list, asserting only the `valid` flag at the end. Can an unprivileged caller of `call-ststx-ratio` (mainnet/contracts/market/v0-4-market.clar:1015), by choosing the block and transaction position at which the external ratio is fetched, use that to have the same quantity scaled twice by two contracts that round differently, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:397` -> `price-multi-resolve`
- Entrypoint: `call-ststx-ratio` (`mainnet/contracts/market/v0-4-market.clar:1015`), unprivileged and publicly callable
- Attacker controls: the block and transaction position at which the external ratio is fetched
- Exploit idea: `price-multi-resolve` folds `iter-price-multi` into a POSITIONAL price list, asserting only the `valid` flag at the end. Reach it through `call-ststx-ratio` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `price-multi-resolve` touches, run `call-ststx-ratio` with the block and transaction position at which the external ratio is fetched, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
