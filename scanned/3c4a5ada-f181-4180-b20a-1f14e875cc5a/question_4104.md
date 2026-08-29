# Q4104: collateral-add via liquidate: mint shares whose backing was never received

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls `collateral-receiver` reach `collateral-add` (mainnet/contracts/market/v0-market-vault.clar:374) in a state where it mint shares whose backing was never received? Given that it evaluates the map write and `mask-update` as `let` bindings BEFORE `check-impl-auth`, the pause state and the amount assertion, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:374` -> `collateral-add`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `collateral-receiver`
- Exploit idea: `collateral-add` evaluates the map write and `mask-update` as `let` bindings BEFORE `check-impl-auth`, the pause state and the amount assertion. Reach it through `liquidate` and mint shares whose backing was never received.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `collateral-receiver` across its boundary values through `liquidate` in simnet and assert `collateral-add` never returns a value that breaks the invariant.
