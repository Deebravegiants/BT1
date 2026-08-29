# Q1660: interpolate-rate via accrue: count one deposit as backing for two simultaneous claims

## Question
Does `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) let an unprivileged attacker who controls the utilization the rate is interpolated at reach `interpolate-rate` (mainnet/contracts/vault/v0-vault-stx.clar:196) in a state where it count one deposit as backing for two simultaneous claims? Given that it interpolates between packed u16 curve points, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:196` -> `interpolate-rate`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the utilization the rate is interpolated at
- Exploit idea: `interpolate-rate` interpolates between packed u16 curve points. Reach it through `accrue` and count one deposit as backing for two simultaneous claims.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `accrue` with the utilization the rate is interpolated at, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
