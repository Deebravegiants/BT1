# Q0471: iter-lookup-collateral via supply-collateral-add: have the same quantity scaled twice by two contracts that 

## Question
`iter-lookup-collateral` (mainnet/contracts/market/v0-market-vault.clar:180) skips rows failing `relevant`, so a disabled asset's collateral vanishes from the returned position. Can an unprivileged caller of `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), by choosing `amount`, use that to have the same quantity scaled twice by two contracts that round differently, violating the invariant that shares outstanding valued at the current share price never exceed `total-assets` and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:180` -> `iter-lookup-collateral`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `iter-lookup-collateral` skips rows failing `relevant`, so a disabled asset's collateral vanishes from the returned position. Reach it through `supply-collateral-add` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `iter-lookup-collateral` touches, run `supply-collateral-add` with `amount`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
