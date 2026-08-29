# Q0316: accrue-and-cache via repay: destroy value through a truncation the opposite operation 

## Question
Does `repay` (mainnet/contracts/market/v0-4-market.clar:1316) let an unprivileged attacker who controls whether the repaid asset is in the accrued debt list reach `accrue-and-cache` (mainnet/contracts/market/v0-4-market.clar:245) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it keys `index-cache` on `{timestamp: stacks-block-time, aid}` and returns the cached record forever after, with no invalidation when the vault later moves, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:245` -> `accrue-and-cache`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: whether the repaid asset is in the accrued debt list
- Exploit idea: `accrue-and-cache` keys `index-cache` on `{timestamp: stacks-block-time, aid}` and returns the cached record forever after, with no invalidation when the vault later moves. Reach it through `repay` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `repay` with whether the repaid asset is in the accrued debt list, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
