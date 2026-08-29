# Q5500: get-asset-value via collateral-add: record a repayment larger than the value actually delivere

## Question
Does `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) let an unprivileged attacker who controls the three `price-feeds` buffers and their order reach `get-asset-value` (mainnet/contracts/market/v0-4-market.clar:679) in a state where it record a repayment larger than the value actually delivered? Given that it resolves a fresh price for a single asset and normalizes with a caller-supplied rounding direction, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:679` -> `get-asset-value`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the three `price-feeds` buffers and their order
- Exploit idea: `get-asset-value` resolves a fresh price for a single asset and normalizes with a caller-supplied rounding direction. Reach it through `collateral-add` and record a repayment larger than the value actually delivered.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `collateral-add` with the three `price-feeds` buffers and their order, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
