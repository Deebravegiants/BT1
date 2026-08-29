# Q1371: iter-lookup-debt via supply-collateral-add: leave a residue that no reconciliation pass ever inspects

## Question
`iter-lookup-debt` (mainnet/contracts/market/v0-market-vault.clar:218) skips rows failing `relevant`, so a disabled asset's DEBT vanishes from the returned position. Can an unprivileged caller of `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), by choosing `min-shares` (the only slippage bound on the deposit leg), use that to leave a residue that no reconciliation pass ever inspects, violating the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:218` -> `iter-lookup-debt`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `min-shares` (the only slippage bound on the deposit leg)
- Exploit idea: `iter-lookup-debt` skips rows failing `relevant`, so a disabled asset's DEBT vanishes from the returned position. Reach it through `supply-collateral-add` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `iter-lookup-debt` touches, run `supply-collateral-add` with `min-shares` (the only slippage bound on the deposit leg), recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
