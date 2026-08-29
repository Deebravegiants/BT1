# Q2333: iter-lookup-collateral via collateral-remove-redeem: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211), controlling remaining zToken collateral whose price moves with the redeem, drive `iter-lookup-collateral` (mainnet/contracts/market/v0-market-vault.clar:180) — which skips rows failing `relevant`, so a disabled asset's collateral vanishes from the returned position — to mint shares whose backing was never received, breaking the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury, and cause protocol insolvency?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:180` -> `iter-lookup-collateral`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: remaining zToken collateral whose price moves with the redeem
- Exploit idea: `iter-lookup-collateral` skips rows failing `relevant`, so a disabled asset's collateral vanishes from the returned position. Reach it through `collateral-remove-redeem` and mint shares whose backing was never received.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `collateral-remove-redeem` call, then the attacker-shaped one with remaining zToken collateral whose price moves with the redeem, and assert the attacker's net token balance change is zero or negative.
