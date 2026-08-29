# Q5296: write-feeds via liquidate-multi: record a repayment larger than the value actually delivere

## Question
Does `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) let an unprivileged attacker who controls the full batch list and its ordering reach `write-feeds` (mainnet/contracts/market/v0-4-market.clar:149) in a state where it record a repayment larger than the value actually delivered? Given that it folds up to three attacker-supplied buffers through `write-feed` with a `(response bool uint)` accumulator, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:149` -> `write-feeds`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the full batch list and its ordering
- Exploit idea: `write-feeds` folds up to three attacker-supplied buffers through `write-feed` with a `(response bool uint)` accumulator. Reach it through `liquidate-multi` and record a repayment larger than the value actually delivered.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `liquidate-multi` with the full batch list and its ordering, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
