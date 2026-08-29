# Q4704: create via collateral-remove-redeem: mint shares whose backing was never received

## Question
Does `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) let an unprivileged attacker who controls `receiver` for the underlying leg reach `create` (mainnet/contracts/market/v0-market-vault.clar:150) in a state where it mint shares whose backing was never received? Given that it binds a principal to a fresh numeric id, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:150` -> `create`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `receiver` for the underlying leg
- Exploit idea: `create` binds a principal to a fresh numeric id. Reach it through `collateral-remove-redeem` and mint shares whose backing was never received.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `receiver` for the underlying leg across its boundary values through `collateral-remove-redeem` in simnet and assert `create` never returns a value that breaks the invariant.
