# Q4960: accrue-debt-asset via supply-collateral-add: record a repayment larger than the value actually delivere

## Question
Does `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) let an unprivileged attacker who controls the position state the final collateral-add is validated against reach `accrue-debt-asset` (mainnet/contracts/market/v0-4-market.clar:262) in a state where it record a repayment larger than the value actually delivered? Given that it calls `accrue-and-cache` with `unwrap-panic` inside a fold whose accumulator ignores the result, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:262` -> `accrue-debt-asset`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: the position state the final collateral-add is validated against
- Exploit idea: `accrue-debt-asset` calls `accrue-and-cache` with `unwrap-panic` inside a fold whose accumulator ignores the result. Reach it through `supply-collateral-add` and record a repayment larger than the value actually delivered.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `supply-collateral-add` with the position state the final collateral-add is validated against, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
