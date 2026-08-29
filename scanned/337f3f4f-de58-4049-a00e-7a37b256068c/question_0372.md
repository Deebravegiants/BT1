# Q0372: debt-preview via supply-collateral-add: destroy value through a truncation the opposite operation 

## Question
Does `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) let an unprivileged attacker who controls `min-shares` (the only slippage bound on the deposit leg) reach `debt-preview` (mainnet/contracts/vault/v0-vault-stx.clar:331) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it computes cumulative debt from `principal-scaled` and the FORWARD index, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:331` -> `debt-preview`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `min-shares` (the only slippage bound on the deposit leg)
- Exploit idea: `debt-preview` computes cumulative debt from `principal-scaled` and the FORWARD index. Reach it through `supply-collateral-add` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `min-shares` (the only slippage bound on the deposit leg) across its boundary values through `supply-collateral-add` in simnet and assert `debt-preview` never returns a value that breaks the invariant.
