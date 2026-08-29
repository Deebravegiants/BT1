# Q4878: collateral-remove via supply-collateral-add: destroy value through a truncation the opposite operation 

## Question
Entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) while controlling `min-shares` (the only slippage bound on the deposit leg), can an unprivileged attacker make `collateral-remove` (mainnet/contracts/market/v0-market-vault.clar:406) destroy value through a truncation the opposite operation does not restore? `collateral-remove` decrements the map and writes the entry before `send-tokens` executes, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:406` -> `collateral-remove`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `min-shares` (the only slippage bound on the deposit leg)
- Exploit idea: `collateral-remove` decrements the map and writes the entry before `send-tokens` executes. Reach it through `supply-collateral-add` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz `min-shares` (the only slippage bound on the deposit leg) across its boundary values through `supply-collateral-add` in simnet and assert `collateral-remove` never returns a value that breaks the invariant.
