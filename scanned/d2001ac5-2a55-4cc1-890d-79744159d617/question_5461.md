# Q5461: iter-lookup-debt via collateral-remove-redeem: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211), controlling `amount` used for BOTH the collateral removal and the share redemption, drive `iter-lookup-debt` (mainnet/contracts/market/v0-market-vault.clar:218) — which skips rows failing `relevant`, so a disabled asset's DEBT vanishes from the returned position — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset, and cause direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:218` -> `iter-lookup-debt`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `amount` used for BOTH the collateral removal and the share redemption
- Exploit idea: `iter-lookup-debt` skips rows failing `relevant`, so a disabled asset's DEBT vanishes from the returned position. Reach it through `collateral-remove-redeem` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `collateral-remove-redeem` with `amount` used for BOTH the collateral removal and the share redemption, then read `iter-lookup-debt` state before and after in the same block and assert the two sides of the invariant are equal.
