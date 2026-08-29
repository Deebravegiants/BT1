# Q2470: find-collateral-amount via collateral-add: have the same quantity scaled twice by two contracts that 

## Question
Entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) while controlling call ordering within the block, can an unprivileged attacker make `find-collateral-amount` (mainnet/contracts/market/v0-4-market.clar:609) have the same quantity scaled twice by two contracts that round differently? `find-collateral-amount` returns u0 for an absent asset, making a missing row indistinguishable from a zero holding, so the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset would fail, yielding direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:609` -> `find-collateral-amount`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: call ordering within the block
- Exploit idea: `find-collateral-amount` returns u0 for an absent asset, making a missing row indistinguishable from a zero holding. Reach it through `collateral-add` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `collateral-add` with call ordering within the block, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
