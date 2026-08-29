# Q5104: accrue-collateral-asset via collateral-add: record a repayment larger than the value actually delivere

## Question
Does `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) let an unprivileged attacker who controls the three `price-feeds` buffers and their order reach `accrue-collateral-asset` (mainnet/contracts/market/v0-4-market.clar:273) in a state where it record a repayment larger than the value actually delivered? Given that it maps a ztoken id to a vault id through a chain of `is-eq` tests that falls through to the u100 sentinel, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:273` -> `accrue-collateral-asset`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the three `price-feeds` buffers and their order
- Exploit idea: `accrue-collateral-asset` maps a ztoken id to a vault id through a chain of `is-eq` tests that falls through to the u100 sentinel. Reach it through `collateral-add` and record a repayment larger than the value actually delivered.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `collateral-add` with the three `price-feeds` buffers and their order, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
