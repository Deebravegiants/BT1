# Q5014: convert-to-scaled-debt via collateral-remove: count one deposit as backing for two simultaneous claims

## Question
Entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) while controlling the `ft` trait principal, can an unprivileged attacker make `convert-to-scaled-debt` (mainnet/contracts/market/v0-4-market.clar:648) count one deposit as backing for two simultaneous claims? `convert-to-scaled-debt` scales a token amount by the cached borrow index, rounding up on the borrow path, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:648` -> `convert-to-scaled-debt`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `convert-to-scaled-debt` scales a token amount by the cached borrow index, rounding up on the borrow path. Reach it through `collateral-remove` and count one deposit as backing for two simultaneous claims.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `collateral-remove` with the `ft` trait principal, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
