# Q2368: get-bitmap via collateral-remove: credit one side of an accounting pair without the other

## Question
Does `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) let an unprivileged attacker who controls the set of assets held reach `get-bitmap` (mainnet/contracts/registry/v0-assets.clar:145) in a state where it credit one side of an accounting pair without the other? Given that it returns the global enabled bitmap that every position read filters on, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:145` -> `get-bitmap`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the set of assets held
- Exploit idea: `get-bitmap` returns the global enabled bitmap that every position read filters on. Reach it through `collateral-remove` and credit one side of an accounting pair without the other.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `collateral-remove` with the set of assets held, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
