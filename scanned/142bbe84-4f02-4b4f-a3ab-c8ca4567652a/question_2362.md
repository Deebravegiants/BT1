# Q2362: find-asset via liquidate: have the same quantity scaled twice by two contracts that 

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling the `price-feeds` buffers and their ordering, can an unprivileged attacker make `find-asset` (mainnet/contracts/market/v0-4-market.clar:584) have the same quantity scaled twice by two contracts that round differently? `find-asset` returns `none` when the id is absent, and several callers resolve that with `unwrap-panic`, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:584` -> `find-asset`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers and their ordering
- Exploit idea: `find-asset` returns `none` when the id is absent, and several callers resolve that with `unwrap-panic`. Reach it through `liquidate` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `liquidate` with the `price-feeds` buffers and their ordering, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
