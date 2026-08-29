# Q2978: iter-lookup-collateral via repay: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `repay` (mainnet/contracts/market/v0-4-market.clar:1316) while controlling `amount`, including far above the real debt (the capping path), can an unprivileged attacker make `iter-lookup-collateral` (mainnet/contracts/market/v0-market-vault.clar:180) leave a residue that no reconciliation pass ever inspects? `iter-lookup-collateral` skips rows failing `relevant`, so a disabled asset's collateral vanishes from the returned position, so the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury would fail, yielding permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:180` -> `iter-lookup-collateral`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: `amount`, including far above the real debt (the capping path)
- Exploit idea: `iter-lookup-collateral` skips rows failing `relevant`, so a disabled asset's collateral vanishes from the returned position. Reach it through `repay` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `repay` twice with `amount`, including far above the real debt (the capping path) varied, and assert that the value `iter-lookup-collateral` returns is identical in both runs; a divergence confirms the finding.
