# Q0244: uint-to-list-u64 via collateral-remove: destroy value through a truncation the opposite operation 

## Question
Does `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) let an unprivileged attacker who controls whether the position has any enabled debt row (the has-debt branch) reach `uint-to-list-u64` (mainnet/contracts/registry/v0-assets.clar:80) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it expands a bitmap into a 64-element list, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:80` -> `uint-to-list-u64`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: whether the position has any enabled debt row (the has-debt branch)
- Exploit idea: `uint-to-list-u64` expands a bitmap into a 64-element list. Reach it through `collateral-remove` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `collateral-remove` with whether the position has any enabled debt row (the has-debt branch), and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
