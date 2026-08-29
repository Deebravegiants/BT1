# Q2860: mask-to-list-internal via collateral-remove: credit one side of an accounting pair without the other

## Question
Does `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) let an unprivileged attacker who controls the set of assets held reach `mask-to-list-internal` (mainnet/contracts/market/v0-4-market.clar:435) in a state where it credit one side of an accounting pair without the other? Given that it expands mask bits into a list bounded at 64 entries, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:435` -> `mask-to-list-internal`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the set of assets held
- Exploit idea: `mask-to-list-internal` expands mask bits into a list bounded at 64 entries. Reach it through `collateral-remove` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `collateral-remove` with the set of assets held, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
