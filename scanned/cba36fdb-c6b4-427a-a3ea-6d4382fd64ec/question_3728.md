# Q3728: iter-lookup-collateral via collateral-remove: make the per-user ledger and the vault aggregate disagree 

## Question
Does `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) let an unprivileged attacker who controls the `price-feeds` buffers reach `iter-lookup-collateral` (mainnet/contracts/market/v0-market-vault.clar:180) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it skips rows failing `relevant`, so a disabled asset's collateral vanishes from the returned position, the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:180` -> `iter-lookup-collateral`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers
- Exploit idea: `iter-lookup-collateral` skips rows failing `relevant`, so a disabled asset's collateral vanishes from the returned position. Reach it through `collateral-remove` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `collateral-remove` twice with the `price-feeds` buffers varied, and assert that the value `iter-lookup-collateral` returns is identical in both runs; a divergence confirms the finding.
