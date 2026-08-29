# Q4372: linear-interpolate via accrue: mint shares whose backing was never received

## Question
Does `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) let an unprivileged attacker who controls the utilization the rate is interpolated at reach `linear-interpolate` (mainnet/contracts/vault/v0-vault-stx.clar:221) in a state where it mint shares whose backing was never received? Given that it interpolates between two points, dividing by `(- x2 x1)`, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:221` -> `linear-interpolate`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the utilization the rate is interpolated at
- Exploit idea: `linear-interpolate` interpolates between two points, dividing by `(- x2 x1)`. Reach it through `accrue` and mint shares whose backing was never received.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `accrue` with the utilization the rate is interpolated at, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
