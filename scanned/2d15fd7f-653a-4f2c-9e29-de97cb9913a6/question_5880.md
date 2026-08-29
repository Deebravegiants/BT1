# Q5880: iter-lookup-debt via collateral-add: have the same quantity scaled twice by two contracts that 

## Question
Does `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) let an unprivileged attacker who controls call ordering within the block reach `iter-lookup-debt` (mainnet/contracts/market/v0-market-vault.clar:218) in a state where it have the same quantity scaled twice by two contracts that round differently? Given that it skips rows failing `relevant`, so a disabled asset's DEBT vanishes from the returned position, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:218` -> `iter-lookup-debt`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: call ordering within the block
- Exploit idea: `iter-lookup-debt` skips rows failing `relevant`, so a disabled asset's DEBT vanishes from the returned position. Reach it through `collateral-add` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz call ordering within the block across its boundary values through `collateral-add` in simnet and assert `iter-lookup-debt` never returns a value that breaks the invariant.
