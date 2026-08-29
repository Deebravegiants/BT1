# Q1300: send-underlying via deposit: count one deposit as backing for two simultaneous claims

## Question
Does `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) let an unprivileged attacker who controls `amount` reach `send-underlying` (mainnet/contracts/vault/v0-vault-stx.clar:296) in a state where it count one deposit as backing for two simultaneous claims? Given that it pushes the underlying under an `as-contract?` post-condition scope, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:296` -> `send-underlying`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `send-underlying` pushes the underlying under an `as-contract?` post-condition scope. Reach it through `deposit` and count one deposit as backing for two simultaneous claims.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `deposit` with `amount`, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
