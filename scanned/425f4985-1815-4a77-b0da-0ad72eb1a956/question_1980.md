# Q1980: find-and-resolve-asset-value via supply-collateral-add: credit one side of an accounting pair without the other

## Question
Does `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) let an unprivileged attacker who controls `min-shares` (the only slippage bound on the deposit leg) reach `find-and-resolve-asset-value` (mainnet/contracts/market/v0-4-market.clar:668) in a state where it credit one side of an accounting pair without the other? Given that it reuses an already-resolved price from the asset list and returns u0 when the asset is not found, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:668` -> `find-and-resolve-asset-value`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `min-shares` (the only slippage bound on the deposit leg)
- Exploit idea: `find-and-resolve-asset-value` reuses an already-resolved price from the asset list and returns u0 when the asset is not found. Reach it through `supply-collateral-add` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz `min-shares` (the only slippage bound on the deposit leg) across its boundary values through `supply-collateral-add` in simnet and assert `find-and-resolve-asset-value` never returns a value that breaks the invariant.
