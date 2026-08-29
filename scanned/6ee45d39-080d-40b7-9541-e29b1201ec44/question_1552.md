# Q1552: send-underlying via accrue: count one deposit as backing for two simultaneous claims

## Question
Does `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) let an unprivileged attacker who controls the utilization the rate is interpolated at reach `send-underlying` (mainnet/contracts/vault/v0-vault-stx.clar:296) in a state where it count one deposit as backing for two simultaneous claims? Given that it pushes the underlying under an `as-contract?` post-condition scope, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:296` -> `send-underlying`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the utilization the rate is interpolated at
- Exploit idea: `send-underlying` pushes the underlying under an `as-contract?` post-condition scope. Reach it through `accrue` and count one deposit as backing for two simultaneous claims.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `accrue` with the utilization the rate is interpolated at, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
