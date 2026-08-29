# Q1964: iter-lookup-debt via collateral-add: credit one side of an accounting pair without the other

## Question
Does `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) let an unprivileged attacker who controls the position's existing collateral and debt composition reach `iter-lookup-debt` (mainnet/contracts/market/v0-market-vault.clar:218) in a state where it credit one side of an accounting pair without the other? Given that it skips rows failing `relevant`, so a disabled asset's DEBT vanishes from the returned position, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:218` -> `iter-lookup-debt`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the position's existing collateral and debt composition
- Exploit idea: `iter-lookup-debt` skips rows failing `relevant`, so a disabled asset's DEBT vanishes from the returned position. Reach it through `collateral-add` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `collateral-add` twice with the position's existing collateral and debt composition varied, and assert that the value `iter-lookup-debt` returns is identical in both runs; a divergence confirms the finding.
