# Q4537: ubalance via transfer: have the same quantity scaled twice by two contracts that 

## Question
Can an unprivileged attacker entering through `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752), controlling `amount`, drive `ubalance` (mainnet/contracts/vault/v0-vault-stx.clar:303) — which reads the real underlying balance, which `deposit` and `redeem` never reconcile against the `assets` var — to have the same quantity scaled twice by two contracts that round differently, breaking the invariant that value leaving a call equals value entering plus value minted minus value burned, and cause direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:303` -> `ubalance`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `ubalance` reads the real underlying balance, which `deposit` and `redeem` never reconcile against the `assets` var. Reach it through `transfer` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `transfer` with `amount`, then read `ubalance` state before and after in the same block and assert the two sides of the invariant are equal.
