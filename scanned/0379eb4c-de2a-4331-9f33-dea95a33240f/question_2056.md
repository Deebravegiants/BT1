# Q2056: lookup via collateral-add: credit one side of an accounting pair without the other

## Question
Does `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) let an unprivileged attacker who controls call ordering within the block reach `lookup` (mainnet/contracts/registry/v0-assets.clar:139) in a state where it credit one side of an accounting pair without the other? Given that it returns the registry record, including the `decimals` captured once at registration, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:139` -> `lookup`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: call ordering within the block
- Exploit idea: `lookup` returns the registry record, including the `decimals` captured once at registration. Reach it through `collateral-add` and credit one side of an accounting pair without the other.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `collateral-add` with call ordering within the block, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
