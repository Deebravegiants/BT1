# Q3541: unwrap-status via liquidate: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), controlling `collateral-receiver`, drive `unwrap-status` (mainnet/contracts/registry/v0-assets.clar:111) — which resolves `status` with `unwrap-panic` — to record a repayment larger than the value actually delivered, breaking the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal, and cause direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:111` -> `unwrap-status`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `collateral-receiver`
- Exploit idea: `unwrap-status` resolves `status` with `unwrap-panic`. Reach it through `liquidate` and record a repayment larger than the value actually delivered.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `liquidate` with `collateral-receiver`, then read `unwrap-status` state before and after in the same block and assert the two sides of the invariant are equal.
