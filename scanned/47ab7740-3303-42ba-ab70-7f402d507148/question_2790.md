# Q2790: mask-to-list-internal via supply-collateral-add: have the same quantity scaled twice by two contracts that 

## Question
Entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) while controlling `min-shares` (the only slippage bound on the deposit leg), can an unprivileged attacker make `mask-to-list-internal` (mainnet/contracts/market/v0-4-market.clar:435) have the same quantity scaled twice by two contracts that round differently? `mask-to-list-internal` expands mask bits into a list bounded at 64 entries, so the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset would fail, yielding temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:435` -> `mask-to-list-internal`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `min-shares` (the only slippage bound on the deposit leg)
- Exploit idea: `mask-to-list-internal` expands mask bits into a list bounded at 64 entries. Reach it through `supply-collateral-add` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz `min-shares` (the only slippage bound on the deposit leg) across its boundary values through `supply-collateral-add` in simnet and assert `mask-to-list-internal` never returns a value that breaks the invariant.
