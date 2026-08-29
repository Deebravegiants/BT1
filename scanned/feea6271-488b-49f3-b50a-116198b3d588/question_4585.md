# Q4585: get-bitmap via collateral-add: have the same quantity scaled twice by two contracts that 

## Question
Can an unprivileged attacker entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), controlling whether this asset is already collateral (the is-new-collateral branch), drive `get-bitmap` (mainnet/contracts/registry/v0-assets.clar:145) — which returns the global enabled bitmap that every position read filters on — to have the same quantity scaled twice by two contracts that round differently, breaking the invariant that value leaving a call equals value entering plus value minted minus value burned, and cause direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:145` -> `get-bitmap`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: whether this asset is already collateral (the is-new-collateral branch)
- Exploit idea: `get-bitmap` returns the global enabled bitmap that every position read filters on. Reach it through `collateral-add` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `collateral-add` with whether this asset is already collateral (the is-new-collateral branch), then read `get-bitmap` state before and after in the same block and assert the two sides of the invariant are equal.
