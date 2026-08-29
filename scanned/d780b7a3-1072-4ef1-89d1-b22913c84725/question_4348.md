# Q4348: convert-to-assets-preview via deposit: mint shares whose backing was never received

## Question
Does `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) let an unprivileged attacker who controls `min-out` reach `convert-to-assets-preview` (mainnet/contracts/vault/v0-vault-stx.clar:317) in a state where it mint shares whose backing was never received? Given that it prices a redemption against `total-assets-preview` and `total-supply-preview`, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:317` -> `convert-to-assets-preview`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `min-out`
- Exploit idea: `convert-to-assets-preview` prices a redemption against `total-assets-preview` and `total-supply-preview`. Reach it through `deposit` and mint shares whose backing was never received.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `deposit` with `min-out`, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
