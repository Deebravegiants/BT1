# Q5230: resolve-ststx via call-ststx-ratio: count one deposit as backing for two simultaneous claims

## Question
Entering through `call-ststx-ratio` (mainnet/contracts/market/v0-4-market.clar:1015) while controlling the block and transaction position at which the external ratio is fetched, can an unprivileged attacker make `resolve-ststx` (mainnet/contracts/market/v0-4-market.clar:339) count one deposit as backing for two simultaneous claims? `resolve-ststx` calls the external stSTX ratio contract inside price resolution and scales by STSTX-RATIO-DECIMALS with `mul-div-down`, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:339` -> `resolve-ststx`
- Entrypoint: `call-ststx-ratio` (`mainnet/contracts/market/v0-4-market.clar:1015`), unprivileged and publicly callable
- Attacker controls: the block and transaction position at which the external ratio is fetched
- Exploit idea: `resolve-ststx` calls the external stSTX ratio contract inside price resolution and scales by STSTX-RATIO-DECIMALS with `mul-div-down`. Reach it through `call-ststx-ratio` and count one deposit as backing for two simultaneous claims.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `call-ststx-ratio` with the block and transaction position at which the external ratio is fetched, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
