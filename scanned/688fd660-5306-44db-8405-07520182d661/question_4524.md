# Q4524: ubalance via deposit: mint shares whose backing was never received

## Question
Does `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) let an unprivileged attacker who controls `recipient`, including a contract principal reach `ubalance` (mainnet/contracts/vault/v0-vault-stx.clar:303) in a state where it mint shares whose backing was never received? Given that it reads the real underlying balance, which `deposit` and `redeem` never reconcile against the `assets` var, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:303` -> `ubalance`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `recipient`, including a contract principal
- Exploit idea: `ubalance` reads the real underlying balance, which `deposit` and `redeem` never reconcile against the `assets` var. Reach it through `deposit` and mint shares whose backing was never received.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `recipient`, including a contract principal across its boundary values through `deposit` in simnet and assert `ubalance` never returns a value that breaks the invariant.
