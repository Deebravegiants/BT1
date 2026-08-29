# Q2200: next-index via collateral-remove: credit one side of an accounting pair without the other

## Question
Does `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) let an unprivileged attacker who controls the set of assets held reach `next-index` (mainnet/contracts/vault/v0-vault-stx.clar:379) in a state where it credit one side of an accounting pair without the other? Given that it returns the stale `index` unchanged when the accrue pause state is set, instead of reverting, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:379` -> `next-index`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the set of assets held
- Exploit idea: `next-index` returns the stale `index` unchanged when the accrue pause state is set, instead of reverting. Reach it through `collateral-remove` and credit one side of an accounting pair without the other.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `collateral-remove` with the set of assets held, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
