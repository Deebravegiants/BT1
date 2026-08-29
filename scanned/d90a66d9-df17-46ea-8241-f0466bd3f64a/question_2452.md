# Q2452: accrue-collateral-asset via liquidate: credit one side of an accounting pair without the other

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls the `price-feeds` buffers and their ordering reach `accrue-collateral-asset` (mainnet/contracts/market/v0-4-market.clar:273) in a state where it credit one side of an accounting pair without the other? Given that it maps a ztoken id to a vault id through a chain of `is-eq` tests that falls through to the u100 sentinel, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:273` -> `accrue-collateral-asset`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers and their ordering
- Exploit idea: `accrue-collateral-asset` maps a ztoken id to a vault id through a chain of `is-eq` tests that falls through to the u100 sentinel. Reach it through `liquidate` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `liquidate` with the `price-feeds` buffers and their ordering, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
