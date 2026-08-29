# Q4482: iter-lookup-debt via collateral-remove-redeem: destroy value through a truncation the opposite operation 

## Question
Entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) while controlling `amount` used for BOTH the collateral removal and the share redemption, can an unprivileged attacker make `iter-lookup-debt` (mainnet/contracts/market/v0-market-vault.clar:218) destroy value through a truncation the opposite operation does not restore? `iter-lookup-debt` skips rows failing `relevant`, so a disabled asset's DEBT vanishes from the returned position, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:218` -> `iter-lookup-debt`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `amount` used for BOTH the collateral removal and the share redemption
- Exploit idea: `iter-lookup-debt` skips rows failing `relevant`, so a disabled asset's DEBT vanishes from the returned position. Reach it through `collateral-remove-redeem` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `amount` used for BOTH the collateral removal and the share redemption across its boundary values through `collateral-remove-redeem` in simnet and assert `iter-lookup-debt` never returns a value that breaks the invariant.
