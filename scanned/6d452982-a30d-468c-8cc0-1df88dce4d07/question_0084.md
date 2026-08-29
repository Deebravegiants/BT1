# Q0084: calc-principal-ratio-reduction via transfer: destroy value through a truncation the opposite operation 

## Question
Does `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752) let an unprivileged attacker who controls the timing relative to a pledge or a liquidation reach `calc-principal-ratio-reduction` (mainnet/contracts/vault/v0-vault-stx.clar:191) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it reduces scaled principal proportionally to an amount over total debt, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:191` -> `calc-principal-ratio-reduction`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: the timing relative to a pledge or a liquidation
- Exploit idea: `calc-principal-ratio-reduction` reduces scaled principal proportionally to an amount over total debt. Reach it through `transfer` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the timing relative to a pledge or a liquidation across its boundary values through `transfer` in simnet and assert `calc-principal-ratio-reduction` never returns a value that breaks the invariant.
