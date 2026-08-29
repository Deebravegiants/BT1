# Q5764: add-user-collateral via borrow: record a repayment larger than the value actually delivere

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls the `ft` trait principal reach `add-user-collateral` (mainnet/contracts/market/v0-market-vault.clar:198) in a state where it record a repayment larger than the value actually delivered? Given that it adds to the collateral row with a graceful u0 default, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:198` -> `add-user-collateral`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `add-user-collateral` adds to the collateral row with a graceful u0 default. Reach it through `borrow` and record a repayment larger than the value actually delivered.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `borrow` with the `ft` trait principal, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
