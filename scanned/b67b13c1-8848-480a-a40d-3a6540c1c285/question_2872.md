# Q2872: vault-socialize-debt via liquidate: credit one side of an accounting pair without the other

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls the `price-feeds` buffers and their ordering reach `vault-socialize-debt` (mainnet/contracts/market/v0-4-market.clar:216) in a state where it credit one side of an accounting pair without the other? Given that it routes a scaled write-down to one of six vaults, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:216` -> `vault-socialize-debt`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers and their ordering
- Exploit idea: `vault-socialize-debt` routes a scaled write-down to one of six vaults. Reach it through `liquidate` and credit one side of an accounting pair without the other.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `liquidate` with the `price-feeds` buffers and their ordering, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
