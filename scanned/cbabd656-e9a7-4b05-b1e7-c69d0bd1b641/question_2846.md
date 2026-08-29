# Q2846: iter-lookup-debt via liquidate-multi: have the same quantity scaled twice by two contracts that 

## Question
Entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) while controlling the trait principals supplied per entry, can an unprivileged attacker make `iter-lookup-debt` (mainnet/contracts/market/v0-market-vault.clar:218) have the same quantity scaled twice by two contracts that round differently? `iter-lookup-debt` skips rows failing `relevant`, so a disabled asset's DEBT vanishes from the returned position, so the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:218` -> `iter-lookup-debt`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the trait principals supplied per entry
- Exploit idea: `iter-lookup-debt` skips rows failing `relevant`, so a disabled asset's DEBT vanishes from the returned position. Reach it through `liquidate-multi` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `liquidate-multi` twice with the trait principals supplied per entry varied, and assert that the value `iter-lookup-debt` returns is identical in both runs; a divergence confirms the finding.
