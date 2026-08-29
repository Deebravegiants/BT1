# Q5969: iter-lookup-debt via repay: destroy value through a truncation the opposite operation 

## Question
Can an unprivileged attacker entering through `repay` (mainnet/contracts/market/v0-4-market.clar:1316), controlling the `ft` trait principal, drive `iter-lookup-debt` (mainnet/contracts/market/v0-market-vault.clar:218) — which skips rows failing `relevant`, so a disabled asset's DEBT vanishes from the returned position — to destroy value through a truncation the opposite operation does not restore, breaking the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury, and cause protocol insolvency?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:218` -> `iter-lookup-debt`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `iter-lookup-debt` skips rows failing `relevant`, so a disabled asset's DEBT vanishes from the returned position. Reach it through `repay` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `repay` call, then the attacker-shaped one with the `ft` trait principal, and assert the attacker's net token balance change is zero or negative.
