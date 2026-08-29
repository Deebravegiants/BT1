# Q0566: iter-lookup-debt via collateral-remove-redeem: mint shares whose backing was never received

## Question
Entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) while controlling `amount` used for BOTH the collateral removal and the share redemption, can an unprivileged attacker make `iter-lookup-debt` (mainnet/contracts/market/v0-market-vault.clar:218) mint shares whose backing was never received? `iter-lookup-debt` skips rows failing `relevant`, so a disabled asset's DEBT vanishes from the returned position, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:218` -> `iter-lookup-debt`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `amount` used for BOTH the collateral removal and the share redemption
- Exploit idea: `iter-lookup-debt` skips rows failing `relevant`, so a disabled asset's DEBT vanishes from the returned position. Reach it through `collateral-remove-redeem` and mint shares whose backing was never received.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `collateral-remove-redeem` twice with `amount` used for BOTH the collateral removal and the share redemption varied, and assert that the value `iter-lookup-debt` returns is identical in both runs; a divergence confirms the finding.
