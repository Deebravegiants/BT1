# Q5734: collateral-add via collateral-add: count one deposit as backing for two simultaneous claims

## Question
Entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) while controlling the three `price-feeds` buffers and their order, can an unprivileged attacker make `collateral-add` (mainnet/contracts/market/v0-market-vault.clar:374) count one deposit as backing for two simultaneous claims? `collateral-add` evaluates the map write and `mask-update` as `let` bindings BEFORE `check-impl-auth`, the pause state and the amount assertion, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:374` -> `collateral-add`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the three `price-feeds` buffers and their order
- Exploit idea: `collateral-add` evaluates the map write and `mask-update` as `let` bindings BEFORE `check-impl-auth`, the pause state and the amount assertion. Reach it through `collateral-add` and count one deposit as backing for two simultaneous claims.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `collateral-add` with the three `price-feeds` buffers and their order, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
