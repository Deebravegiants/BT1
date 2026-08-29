# Q0748: vault-accrue via liquidate: destroy value through a truncation the opposite operation 

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls `collateral-receiver` reach `vault-accrue` (mainnet/contracts/market/v0-4-market.clar:189) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it dispatches accrual to one of six vaults by asset id, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:189` -> `vault-accrue`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `collateral-receiver`
- Exploit idea: `vault-accrue` dispatches accrual to one of six vaults by asset id. Reach it through `liquidate` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `liquidate` with `collateral-receiver`, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
