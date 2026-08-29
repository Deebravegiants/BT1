# Q5020: is-healthy-with-mask via supply-collateral-add: record a repayment larger than the value actually delivere

## Question
Does `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) let an unprivileged attacker who controls the position state the final collateral-add is validated against reach `is-healthy-with-mask` (mainnet/contracts/market/v0-4-market.clar:663) in a state where it record a repayment larger than the value actually delivered? Given that it resolves an egroup for a caller-influenced mask and applies its LTV-BORROW, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:663` -> `is-healthy-with-mask`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: the position state the final collateral-add is validated against
- Exploit idea: `is-healthy-with-mask` resolves an egroup for a caller-influenced mask and applies its LTV-BORROW. Reach it through `supply-collateral-add` and record a repayment larger than the value actually delivered.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `supply-collateral-add` with the position state the final collateral-add is validated against, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
