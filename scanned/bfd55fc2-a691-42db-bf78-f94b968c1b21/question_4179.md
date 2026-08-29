# Q4179: accrue-user-debts via liquidate: credit one side of an accounting pair without the other

## Question
`accrue-user-debts` (mainnet/contracts/market/v0-4-market.clar:259) folds accrual over the position's debt list only. Can an unprivileged caller of `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), by choosing `borrower`, any third-party principal, use that to credit one side of an accounting pair without the other, violating the invariant that shares outstanding valued at the current share price never exceed `total-assets` and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:259` -> `accrue-user-debts`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `borrower`, any third-party principal
- Exploit idea: `accrue-user-debts` folds accrual over the position's debt list only. Reach it through `liquidate` and credit one side of an accounting pair without the other.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `accrue-user-debts` touches, run `liquidate` with `borrower`, any third-party principal, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
