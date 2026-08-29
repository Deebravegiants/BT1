# Q1420: accrue-user-debts via collateral-remove: count one deposit as backing for two simultaneous claims

## Question
Does `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) let an unprivileged attacker who controls the `price-feeds` buffers reach `accrue-user-debts` (mainnet/contracts/market/v0-4-market.clar:259) in a state where it count one deposit as backing for two simultaneous claims? Given that it folds accrual over the position's debt list only, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:259` -> `accrue-user-debts`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers
- Exploit idea: `accrue-user-debts` folds accrual over the position's debt list only. Reach it through `collateral-remove` and count one deposit as backing for two simultaneous claims.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `collateral-remove` with the `price-feeds` buffers, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
