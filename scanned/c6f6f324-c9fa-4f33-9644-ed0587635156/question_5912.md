# Q5912: iter-lookup-collateral via liquidate: have the same quantity scaled twice by two contracts that 

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls `debt-amount` reach `iter-lookup-collateral` (mainnet/contracts/market/v0-market-vault.clar:180) in a state where it have the same quantity scaled twice by two contracts that round differently? Given that it skips rows failing `relevant`, so a disabled asset's collateral vanishes from the returned position, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:180` -> `iter-lookup-collateral`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `debt-amount`
- Exploit idea: `iter-lookup-collateral` skips rows failing `relevant`, so a disabled asset's collateral vanishes from the returned position. Reach it through `liquidate` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `liquidate` twice with `debt-amount` varied, and assert that the value `iter-lookup-collateral` returns is identical in both runs; a divergence confirms the finding.
