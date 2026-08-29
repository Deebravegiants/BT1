# Q3018: accrue-user-debts via repay: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `repay` (mainnet/contracts/market/v0-4-market.clar:1316) while controlling `amount`, including far above the real debt (the capping path), can an unprivileged attacker make `accrue-user-debts` (mainnet/contracts/market/v0-4-market.clar:259) leave a residue that no reconciliation pass ever inspects? `accrue-user-debts` folds accrual over the position's debt list only, so the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:259` -> `accrue-user-debts`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: `amount`, including far above the real debt (the capping path)
- Exploit idea: `accrue-user-debts` folds accrual over the position's debt list only. Reach it through `repay` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `amount`, including far above the real debt (the capping path) across its boundary values through `repay` in simnet and assert `accrue-user-debts` never returns a value that breaks the invariant.
