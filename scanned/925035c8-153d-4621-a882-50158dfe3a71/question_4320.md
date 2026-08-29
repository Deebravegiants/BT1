# Q4320: find-asset via liquidate: mint shares whose backing was never received

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls `collateral-receiver` reach `find-asset` (mainnet/contracts/market/v0-4-market.clar:584) in a state where it mint shares whose backing was never received? Given that it returns `none` when the id is absent, and several callers resolve that with `unwrap-panic`, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:584` -> `find-asset`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `collateral-receiver`
- Exploit idea: `find-asset` returns `none` when the id is absent, and several callers resolve that with `unwrap-panic`. Reach it through `liquidate` and mint shares whose backing was never received.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz `collateral-receiver` across its boundary values through `liquidate` in simnet and assert `find-asset` never returns a value that breaks the invariant.
