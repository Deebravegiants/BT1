# Q4261: write-feeds via collateral-add: have the same quantity scaled twice by two contracts that 

## Question
Can an unprivileged attacker entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), controlling whether this asset is already collateral (the is-new-collateral branch), drive `write-feeds` (mainnet/contracts/market/v0-4-market.clar:149) — which folds up to three attacker-supplied buffers through `write-feed` with a `(response bool uint)` accumulator — to have the same quantity scaled twice by two contracts that round differently, breaking the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`, and cause direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:149` -> `write-feeds`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: whether this asset is already collateral (the is-new-collateral branch)
- Exploit idea: `write-feeds` folds up to three attacker-supplied buffers through `write-feed` with a `(response bool uint)` accumulator. Reach it through `collateral-add` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `collateral-add` with whether this asset is already collateral (the is-new-collateral branch), then read `write-feeds` state before and after in the same block and assert the two sides of the invariant are equal.
