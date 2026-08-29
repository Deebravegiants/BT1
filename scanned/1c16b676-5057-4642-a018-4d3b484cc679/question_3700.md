# Q3700: resolve-interpolation-points via redeem: make the per-user ledger and the vault aggregate disagree 

## Question
Does `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) let an unprivileged attacker who controls `recipient` reach `resolve-interpolation-points` (mainnet/contracts/vault/v0-vault-stx.clar:205) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it selects the bracketing curve points for a utilization, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:205` -> `resolve-interpolation-points`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: `recipient`
- Exploit idea: `resolve-interpolation-points` selects the bracketing curve points for a utilization. Reach it through `redeem` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `redeem` with `recipient`, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
