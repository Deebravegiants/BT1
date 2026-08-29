# Q0708: get-bitmap via liquidate: destroy value through a truncation the opposite operation 

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls the `price-feeds` buffers and their ordering reach `get-bitmap` (mainnet/contracts/registry/v0-assets.clar:145) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it returns the global enabled bitmap that every position read filters on, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:145` -> `get-bitmap`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers and their ordering
- Exploit idea: `get-bitmap` returns the global enabled bitmap that every position read filters on. Reach it through `liquidate` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the `price-feeds` buffers and their ordering across its boundary values through `liquidate` in simnet and assert `get-bitmap` never returns a value that breaks the invariant.
