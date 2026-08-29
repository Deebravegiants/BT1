# Q5401: accrue-user-collateral via deposit: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763), controlling `amount`, drive `accrue-user-collateral` (mainnet/contracts/market/v0-4-market.clar:270) — which accrues only rows that `is-ztoken` recognises, skipping everything else — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that every round-up has a paired round-down that repetition cannot exploit, and cause direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:270` -> `accrue-user-collateral`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `accrue-user-collateral` accrues only rows that `is-ztoken` recognises, skipping everything else. Reach it through `deposit` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `deposit` with `amount`, then read `accrue-user-collateral` state before and after in the same block and assert the two sides of the invariant are equal.
