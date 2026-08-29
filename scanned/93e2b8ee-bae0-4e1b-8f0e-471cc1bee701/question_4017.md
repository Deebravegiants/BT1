# Q4017: resolve-price-feed via collateral-remove: have the same quantity scaled twice by two contracts that 

## Question
Can an unprivileged attacker entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107), controlling `amount` relative to the current collateral row (the removing-all branch), drive `resolve-price-feed` (mainnet/contracts/market/v0-4-market.clar:332) — which dispatches on a 1-byte type to `resolve-pyth` or `resolve-dia`, erroring otherwise — to have the same quantity scaled twice by two contracts that round differently, breaking the invariant that value leaving a call equals value entering plus value minted minus value burned, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:332` -> `resolve-price-feed`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: `amount` relative to the current collateral row (the removing-all branch)
- Exploit idea: `resolve-price-feed` dispatches on a 1-byte type to `resolve-pyth` or `resolve-dia`, erroring otherwise. Reach it through `collateral-remove` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `resolve-price-feed` touches, run `collateral-remove` with `amount` relative to the current collateral row (the removing-all branch), recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
