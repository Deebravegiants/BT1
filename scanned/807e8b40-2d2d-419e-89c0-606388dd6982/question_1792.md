# Q1792: get-liquidation-position via supply-collateral-add: count one deposit as backing for two simultaneous claims

## Question
Does `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) let an unprivileged attacker who controls the `ft` trait principal deciding which vault is routed to reach `get-liquidation-position` (mainnet/contracts/market/v0-4-market.clar:473) in a state where it count one deposit as backing for two simultaneous claims? Given that it returns enabled collateral plus ALL debt, a different view from the one borrow validated against, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:473` -> `get-liquidation-position`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal deciding which vault is routed to
- Exploit idea: `get-liquidation-position` returns enabled collateral plus ALL debt, a different view from the one borrow validated against. Reach it through `supply-collateral-add` and count one deposit as backing for two simultaneous claims.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `supply-collateral-add` with the `ft` trait principal deciding which vault is routed to, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
