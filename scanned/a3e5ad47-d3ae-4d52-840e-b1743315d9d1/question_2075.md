# Q2075: iter-lookup-collateral via borrow: destroy value through a truncation the opposite operation 

## Question
`iter-lookup-collateral` (mainnet/contracts/market/v0-market-vault.clar:180) skips rows failing `relevant`, so a disabled asset's collateral vanishes from the returned position. Can an unprivileged caller of `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), by choosing `amount`, use that to destroy value through a truncation the opposite operation does not restore, violating the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` and producing protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:180` -> `iter-lookup-collateral`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `iter-lookup-collateral` skips rows failing `relevant`, so a disabled asset's collateral vanishes from the returned position. Reach it through `borrow` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `borrow` call, then the attacker-shaped one with `amount`, and assert the attacker's net token balance change is zero or negative.
