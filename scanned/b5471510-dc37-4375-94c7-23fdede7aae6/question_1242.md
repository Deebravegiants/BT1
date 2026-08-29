# Q1242: accrue-user-debts via liquidate: record a repayment larger than the value actually delivere

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling `borrower`, any third-party principal, can an unprivileged attacker make `accrue-user-debts` (mainnet/contracts/market/v0-4-market.clar:259) record a repayment larger than the value actually delivered? `accrue-user-debts` folds accrual over the position's debt list only, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:259` -> `accrue-user-debts`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `borrower`, any third-party principal
- Exploit idea: `accrue-user-debts` folds accrual over the position's debt list only. Reach it through `liquidate` and record a repayment larger than the value actually delivered.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `borrower`, any third-party principal across its boundary values through `liquidate` in simnet and assert `accrue-user-debts` never returns a value that breaks the invariant.
