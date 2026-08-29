# Q5668: create via borrow: record a repayment larger than the value actually delivere

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls the `ft` trait principal reach `create` (mainnet/contracts/market/v0-market-vault.clar:150) in a state where it record a repayment larger than the value actually delivered? Given that it binds a principal to a fresh numeric id, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:150` -> `create`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `create` binds a principal to a fresh numeric id. Reach it through `borrow` and record a repayment larger than the value actually delivered.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `borrow` with the `ft` trait principal, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
