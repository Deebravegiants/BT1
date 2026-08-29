# Q3079: accrue-user-debts via collateral-add: count one deposit as backing for two simultaneous claims

## Question
`accrue-user-debts` (mainnet/contracts/market/v0-4-market.clar:259) folds accrual over the position's debt list only. Can an unprivileged caller of `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), by choosing the position's existing collateral and debt composition, use that to count one deposit as backing for two simultaneous claims, violating the invariant that every round-up has a paired round-down that repetition cannot exploit and producing direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:259` -> `accrue-user-debts`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the position's existing collateral and debt composition
- Exploit idea: `accrue-user-debts` folds accrual over the position's debt list only. Reach it through `collateral-add` and count one deposit as backing for two simultaneous claims.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `collateral-add` with the position's existing collateral and debt composition, then read `accrue-user-debts` state before and after in the same block and assert the two sides of the invariant are equal.
