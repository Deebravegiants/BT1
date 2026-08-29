# Q0406: write-feed via borrow: mint shares whose backing was never received

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling the `price-feeds` buffers, can an unprivileged attacker make `write-feed` (mainnet/contracts/market/v0-4-market.clar:129) mint shares whose backing was never received? `write-feed` applies one Pyth price-feed update and folds its status, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:129` -> `write-feed`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers
- Exploit idea: `write-feed` applies one Pyth price-feed update and folds its status. Reach it through `borrow` and mint shares whose backing was never received.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `borrow` with the `price-feeds` buffers, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
