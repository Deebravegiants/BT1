# Q5889: iter-lookup-debt via liquidate: destroy value through a truncation the opposite operation 

## Question
Can an unprivileged attacker entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), controlling `min-collateral-expected`, drive `iter-lookup-debt` (mainnet/contracts/market/v0-market-vault.clar:218) — which skips rows failing `relevant`, so a disabled asset's DEBT vanishes from the returned position — to destroy value through a truncation the opposite operation does not restore, breaking the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:218` -> `iter-lookup-debt`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `min-collateral-expected`
- Exploit idea: `iter-lookup-debt` skips rows failing `relevant`, so a disabled asset's DEBT vanishes from the returned position. Reach it through `liquidate` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `iter-lookup-debt` touches, run `liquidate` with `min-collateral-expected`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
