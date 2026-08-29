# Q5095: zip via redeem: make the per-user ledger and the vault aggregate disagree 

## Question
`zip` (mainnet/contracts/vault/v0-vault-stx.clar:226) pairs the utilization and rate point lists element by element. Can an unprivileged caller of `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797), by choosing the gap between the `assets` var and the real balance, use that to make the per-user ledger and the vault aggregate disagree by a repeatable amount, violating the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal and producing direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:226` -> `zip`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: the gap between the `assets` var and the real balance
- Exploit idea: `zip` pairs the utilization and rate point lists element by element. Reach it through `redeem` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `redeem` with the gap between the `assets` var and the real balance, then read `zip` state before and after in the same block and assert the two sides of the invariant are equal.
