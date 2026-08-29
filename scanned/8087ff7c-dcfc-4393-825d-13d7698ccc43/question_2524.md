# Q2524: iter-lookup-debt via collateral-remove-redeem: credit one side of an accounting pair without the other

## Question
Does `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) let an unprivileged attacker who controls `amount` used for BOTH the collateral removal and the share redemption reach `iter-lookup-debt` (mainnet/contracts/market/v0-market-vault.clar:218) in a state where it credit one side of an accounting pair without the other? Given that it skips rows failing `relevant`, so a disabled asset's DEBT vanishes from the returned position, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:218` -> `iter-lookup-debt`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `amount` used for BOTH the collateral removal and the share redemption
- Exploit idea: `iter-lookup-debt` skips rows failing `relevant`, so a disabled asset's DEBT vanishes from the returned position. Reach it through `collateral-remove-redeem` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `collateral-remove-redeem` with `amount` used for BOTH the collateral removal and the share redemption, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
