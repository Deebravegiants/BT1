# Q5488: iter-price-multi via liquidate-multi: record a repayment larger than the value actually delivere

## Question
Does `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) let an unprivileged attacker who controls the full batch list and its ordering reach `iter-price-multi` (mainnet/contracts/market/v0-4-market.clar:405) in a state where it record a repayment larger than the value actually delivered? Given that it carries `aids` and `idx` in its accumulator but never uses them to align prices with asset ids, and appends under `as-max-len? ... u64`, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:405` -> `iter-price-multi`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the full batch list and its ordering
- Exploit idea: `iter-price-multi` carries `aids` and `idx` in its accumulator but never uses them to align prices with asset ids, and appends under `as-max-len? ... u64`. Reach it through `liquidate-multi` and record a repayment larger than the value actually delivered.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `liquidate-multi` with the full batch list and its ordering, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
