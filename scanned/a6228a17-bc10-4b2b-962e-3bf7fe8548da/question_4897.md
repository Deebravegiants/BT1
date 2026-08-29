# Q4897: interest-rate via collateral-add: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), controlling call ordering within the block, drive `interest-rate` (mainnet/contracts/vault/v0-vault-stx.clar:371) — which interpolates the packed curve at the current utilization — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that every round-up has a paired round-down that repetition cannot exploit, and cause direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:371` -> `interest-rate`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: call ordering within the block
- Exploit idea: `interest-rate` interpolates the packed curve at the current utilization. Reach it through `collateral-add` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `collateral-add` with call ordering within the block, then read `interest-rate` state before and after in the same block and assert the two sides of the invariant are equal.
