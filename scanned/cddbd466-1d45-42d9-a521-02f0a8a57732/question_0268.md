# Q0268: is-liquidation-paused via liquidate: destroy value through a truncation the opposite operation 

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls `collateral-receiver` reach `is-liquidation-paused` (mainnet/contracts/market/v0-4-market.clar:691) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it returns true if the manual pause, the GLOBAL grace entry, OR the per-asset grace entry is live, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:691` -> `is-liquidation-paused`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `collateral-receiver`
- Exploit idea: `is-liquidation-paused` returns true if the manual pause, the GLOBAL grace entry, OR the per-asset grace entry is live. Reach it through `liquidate` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `liquidate` with `collateral-receiver`, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
