# Q3993: get-notional-evaluation via liquidate-multi: have the same quantity scaled twice by two contracts that 

## Question
Can an unprivileged attacker entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593), controlling the full batch list and its ordering, drive `get-notional-evaluation` (mainnet/contracts/market/v0-4-market.clar:514) — which folds over the ENABLED asset list, so a position row whose asset is absent from that list contributes nothing to either total — to have the same quantity scaled twice by two contracts that round differently, breaking the invariant that value leaving a call equals value entering plus value minted minus value burned, and cause permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:514` -> `get-notional-evaluation`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the full batch list and its ordering
- Exploit idea: `get-notional-evaluation` folds over the ENABLED asset list, so a position row whose asset is absent from that list contributes nothing to either total. Reach it through `liquidate-multi` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `get-notional-evaluation` touches, run `liquidate-multi` with the full batch list and its ordering, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
