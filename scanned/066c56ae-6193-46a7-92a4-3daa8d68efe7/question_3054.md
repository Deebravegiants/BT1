# Q3054: iter-lookup-collateral via borrow: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling the `ft` trait principal, can an unprivileged attacker make `iter-lookup-collateral` (mainnet/contracts/market/v0-market-vault.clar:180) leave a residue that no reconciliation pass ever inspects? `iter-lookup-collateral` skips rows failing `relevant`, so a disabled asset's collateral vanishes from the returned position, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:180` -> `iter-lookup-collateral`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `iter-lookup-collateral` skips rows failing `relevant`, so a disabled asset's collateral vanishes from the returned position. Reach it through `borrow` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the `ft` trait principal across its boundary values through `borrow` in simnet and assert `iter-lookup-collateral` never returns a value that breaks the invariant.
