# Q3769: mask-to-list-internal via supply-collateral-add: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), controlling `min-shares` (the only slippage bound on the deposit leg), drive `mask-to-list-internal` (mainnet/contracts/market/v0-4-market.clar:435) — which expands mask bits into a list bounded at 64 entries — to record a repayment larger than the value actually delivered, breaking the invariant that `assets` never exceeds the underlying the vault actually holds, and cause theft of unclaimed yield?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:435` -> `mask-to-list-internal`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `min-shares` (the only slippage bound on the deposit leg)
- Exploit idea: `mask-to-list-internal` expands mask bits into a list bounded at 64 entries. Reach it through `supply-collateral-add` and record a repayment larger than the value actually delivered.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: In `local-testing/tests` on a local fork, drive `supply-collateral-add` with `min-shares` (the only slippage bound on the deposit leg), then read `mask-to-list-internal` state before and after in the same block and assert the two sides of the invariant are equal.
