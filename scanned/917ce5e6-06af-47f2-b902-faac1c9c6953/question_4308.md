# Q4308: iter-lookup-debt via supply-collateral-add: mint shares whose backing was never received

## Question
Does `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) let an unprivileged attacker who controls `min-shares` (the only slippage bound on the deposit leg) reach `iter-lookup-debt` (mainnet/contracts/market/v0-market-vault.clar:218) in a state where it mint shares whose backing was never received? Given that it skips rows failing `relevant`, so a disabled asset's DEBT vanishes from the returned position, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:218` -> `iter-lookup-debt`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `min-shares` (the only slippage bound on the deposit leg)
- Exploit idea: `iter-lookup-debt` skips rows failing `relevant`, so a disabled asset's DEBT vanishes from the returned position. Reach it through `supply-collateral-add` and mint shares whose backing was never received.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `min-shares` (the only slippage bound on the deposit leg) across its boundary values through `supply-collateral-add` in simnet and assert `iter-lookup-debt` never returns a value that breaks the invariant.
