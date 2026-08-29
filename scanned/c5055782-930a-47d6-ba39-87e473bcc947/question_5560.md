# Q5560: get-liquidation-position via borrow: record a repayment larger than the value actually delivere

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls the `ft` trait principal reach `get-liquidation-position` (mainnet/contracts/market/v0-4-market.clar:473) in a state where it record a repayment larger than the value actually delivered? Given that it returns enabled collateral plus ALL debt, a different view from the one borrow validated against, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:473` -> `get-liquidation-position`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `get-liquidation-position` returns enabled collateral plus ALL debt, a different view from the one borrow validated against. Reach it through `borrow` and record a repayment larger than the value actually delivered.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `borrow` with the `ft` trait principal, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
