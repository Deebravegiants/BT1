# Q0180: filter-u128 via collateral-remove: destroy value through a truncation the opposite operation 

## Question
Does `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) let an unprivileged attacker who controls the set of assets held reach `filter-u128` (mainnet/contracts/registry/v0-egroup.clar:97) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it filters a 128-entry bucket list, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:97` -> `filter-u128`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the set of assets held
- Exploit idea: `filter-u128` filters a 128-entry bucket list. Reach it through `collateral-remove` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the set of assets held across its boundary values through `collateral-remove` in simnet and assert `filter-u128` never returns a value that breaks the invariant.
