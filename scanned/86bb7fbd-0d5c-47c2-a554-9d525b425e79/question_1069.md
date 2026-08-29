# Q1069: accrue-user-debts via accrue: make the per-user ledger and the vault aggregate disagree 

## Question
Can an unprivileged attacker entering through `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835), controlling the utilization the rate is interpolated at, drive `accrue-user-debts` (mainnet/contracts/market/v0-4-market.clar:259) — which folds accrual over the position's debt list only — to make the per-user ledger and the vault aggregate disagree by a repeatable amount, breaking the invariant that every round-up has a paired round-down that repetition cannot exploit, and cause theft of unclaimed yield?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:259` -> `accrue-user-debts`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the utilization the rate is interpolated at
- Exploit idea: `accrue-user-debts` folds accrual over the position's debt list only. Reach it through `accrue` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: In `local-testing/tests` on a local fork, drive `accrue` with the utilization the rate is interpolated at, then read `accrue-user-debts` state before and after in the same block and assert the two sides of the invariant are equal.
