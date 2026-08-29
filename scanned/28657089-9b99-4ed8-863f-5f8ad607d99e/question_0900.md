# Q0900: write-feed via collateral-remove: destroy value through a truncation the opposite operation 

## Question
Does `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) let an unprivileged attacker who controls the set of assets held reach `write-feed` (mainnet/contracts/market/v0-4-market.clar:129) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it applies one Pyth price-feed update and folds its status, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:129` -> `write-feed`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the set of assets held
- Exploit idea: `write-feed` applies one Pyth price-feed update and folds its status. Reach it through `collateral-remove` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the set of assets held across its boundary values through `collateral-remove` in simnet and assert `write-feed` never returns a value that breaks the invariant.
