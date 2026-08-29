# Q2100: accrue-user-debts via collateral-add: credit one side of an accounting pair without the other

## Question
Does `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) let an unprivileged attacker who controls `amount` reach `accrue-user-debts` (mainnet/contracts/market/v0-4-market.clar:259) in a state where it credit one side of an accounting pair without the other? Given that it folds accrual over the position's debt list only, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:259` -> `accrue-user-debts`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `accrue-user-debts` folds accrual over the position's debt list only. Reach it through `collateral-add` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `amount` across its boundary values through `collateral-add` in simnet and assert `accrue-user-debts` never returns a value that breaks the invariant.
