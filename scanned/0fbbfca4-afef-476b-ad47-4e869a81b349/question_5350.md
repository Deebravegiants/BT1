# Q5350: interpolate-rate via call-ststx-ratio: count one deposit as backing for two simultaneous claims

## Question
Entering through `call-ststx-ratio` (mainnet/contracts/market/v0-4-market.clar:1015) while controlling the block and transaction position at which the external ratio is fetched, can an unprivileged attacker make `interpolate-rate` (mainnet/contracts/vault/v0-vault-stx.clar:196) count one deposit as backing for two simultaneous claims? `interpolate-rate` interpolates between packed u16 curve points, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:196` -> `interpolate-rate`
- Entrypoint: `call-ststx-ratio` (`mainnet/contracts/market/v0-4-market.clar:1015`), unprivileged and publicly callable
- Attacker controls: the block and transaction position at which the external ratio is fetched
- Exploit idea: `interpolate-rate` interpolates between packed u16 curve points. Reach it through `call-ststx-ratio` and count one deposit as backing for two simultaneous claims.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `call-ststx-ratio` with the block and transaction position at which the external ratio is fetched, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
