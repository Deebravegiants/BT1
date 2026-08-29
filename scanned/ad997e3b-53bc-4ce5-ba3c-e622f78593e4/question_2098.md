# Q2098: scale-debt-for-liquidation via liquidate: have the same quantity scaled twice by two contracts that 

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling the `price-feeds` buffers and their ordering, can an unprivileged attacker make `scale-debt-for-liquidation` (mainnet/contracts/market/v0-4-market.clar:858) have the same quantity scaled twice by two contracts that round differently? `scale-debt-for-liquidation` re-scales collateral by `scaled-to-remove / scaled-debt` after the debt was already capped, so the invariant that every round-up has a paired round-down that repetition cannot exploit would fail, yielding direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:858` -> `scale-debt-for-liquidation`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers and their ordering
- Exploit idea: `scale-debt-for-liquidation` re-scales collateral by `scaled-to-remove / scaled-debt` after the debt was already capped. Reach it through `liquidate` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `liquidate` with the `price-feeds` buffers and their ordering, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
