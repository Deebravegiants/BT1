# Q0791: iter-lookup-collateral via collateral-remove: have the same quantity scaled twice by two contracts that 

## Question
`iter-lookup-collateral` (mainnet/contracts/market/v0-market-vault.clar:180) skips rows failing `relevant`, so a disabled asset's collateral vanishes from the returned position. Can an unprivileged caller of `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107), by choosing the `price-feeds` buffers, use that to have the same quantity scaled twice by two contracts that round differently, violating the invariant that shares outstanding valued at the current share price never exceed `total-assets` and producing protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:180` -> `iter-lookup-collateral`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers
- Exploit idea: `iter-lookup-collateral` skips rows failing `relevant`, so a disabled asset's collateral vanishes from the returned position. Reach it through `collateral-remove` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `collateral-remove` call, then the attacker-shaped one with the `price-feeds` buffers, and assert the attacker's net token balance change is zero or negative.
