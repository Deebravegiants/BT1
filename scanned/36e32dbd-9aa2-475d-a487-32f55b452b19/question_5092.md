# Q5092: linear-interpolate via borrow: record a repayment larger than the value actually delivere

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls the `ft` trait principal reach `linear-interpolate` (mainnet/contracts/vault/v0-vault-stx.clar:221) in a state where it record a repayment larger than the value actually delivered? Given that it interpolates between two points, dividing by `(- x2 x1)`, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:221` -> `linear-interpolate`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `linear-interpolate` interpolates between two points, dividing by `(- x2 x1)`. Reach it through `borrow` and record a repayment larger than the value actually delivered.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `borrow` with the `ft` trait principal, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
