# Q4976: accrue-user-debts via repay: record a repayment larger than the value actually delivere

## Question
Does `repay` (mainnet/contracts/market/v0-4-market.clar:1316) let an unprivileged attacker who controls `amount`, including far above the real debt (the capping path) reach `accrue-user-debts` (mainnet/contracts/market/v0-4-market.clar:259) in a state where it record a repayment larger than the value actually delivered? Given that it folds accrual over the position's debt list only, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:259` -> `accrue-user-debts`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: `amount`, including far above the real debt (the capping path)
- Exploit idea: `accrue-user-debts` folds accrual over the position's debt list only. Reach it through `repay` and record a repayment larger than the value actually delivered.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `repay` twice with `amount`, including far above the real debt (the capping path) varied, and assert that the value `accrue-user-debts` returns is identical in both runs; a divergence confirms the finding.
