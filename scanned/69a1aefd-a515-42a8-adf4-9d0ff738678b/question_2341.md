# Q2341: calc-multiplier-delta via deposit: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763), controlling `recipient`, including a contract principal, drive `calc-multiplier-delta` (mainnet/contracts/vault/v0-vault-stx.clar:170) — which compounds a rate over `time-delta` with a caller-independent rounding flag — to mint shares whose backing was never received, breaking the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury, and cause direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:170` -> `calc-multiplier-delta`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `recipient`, including a contract principal
- Exploit idea: `calc-multiplier-delta` compounds a rate over `time-delta` with a caller-independent rounding flag. Reach it through `deposit` and mint shares whose backing was never received.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `deposit` with `recipient`, including a contract principal, then read `calc-multiplier-delta` state before and after in the same block and assert the two sides of the invariant are equal.
