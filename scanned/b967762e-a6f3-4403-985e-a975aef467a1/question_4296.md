# Q4296: increment via supply-collateral-add: mint shares whose backing was never received

## Question
Does `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) let an unprivileged attacker who controls the position state the final collateral-add is validated against reach `increment` (mainnet/contracts/market/v0-market-vault.clar:137) in a state where it mint shares whose backing was never received? Given that it advances the user-id nonce, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:137` -> `increment`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: the position state the final collateral-add is validated against
- Exploit idea: `increment` advances the user-id nonce. Reach it through `supply-collateral-add` and mint shares whose backing was never received.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the position state the final collateral-add is validated against across its boundary values through `supply-collateral-add` in simnet and assert `increment` never returns a value that breaks the invariant.
