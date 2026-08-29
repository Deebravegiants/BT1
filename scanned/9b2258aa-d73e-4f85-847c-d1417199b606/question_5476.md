# Q5476: interest-rate via collateral-remove: record a repayment larger than the value actually delivere

## Question
Does `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) let an unprivileged attacker who controls the `ft` trait principal reach `interest-rate` (mainnet/contracts/vault/v0-vault-stx.clar:371) in a state where it record a repayment larger than the value actually delivered? Given that it interpolates the packed curve at the current utilization, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:371` -> `interest-rate`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `interest-rate` interpolates the packed curve at the current utilization. Reach it through `collateral-remove` and record a repayment larger than the value actually delivered.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `collateral-remove` with the `ft` trait principal, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
