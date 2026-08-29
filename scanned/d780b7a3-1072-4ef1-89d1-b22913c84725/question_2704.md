# Q2704: merge-price via collateral-remove: credit one side of an accounting pair without the other

## Question
Does `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) let an unprivileged attacker who controls the set of assets held reach `merge-price` (mainnet/contracts/market/v0-4-market.clar:506) in a state where it credit one side of an accounting pair without the other? Given that it attaches a price to an asset record by position in the fold, not by asset id, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:506` -> `merge-price`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the set of assets held
- Exploit idea: `merge-price` attaches a price to an asset record by position in the fold, not by asset id. Reach it through `collateral-remove` and credit one side of an accounting pair without the other.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `collateral-remove` with the set of assets held, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
